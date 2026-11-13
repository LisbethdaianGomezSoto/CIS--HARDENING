#!/usr/bin/env python3
"""
cis_hardening.py - Auditoria y hardening de controles seleccionados
                   (basados en recomendaciones de CIS Benchmark)

ALCANCE
  Comprueba un conjunto SELECCIONADO de recomendaciones: 13 en Cisco IOS y 10 en
  FortiGate. No es una auditoria CIS completa y no declara un nivel de cumplimiento
  del benchmark. Los controles marcados como "Adicional" son buenas practicas que no
  tienen identificador en el benchmark utilizado.

MODOS
  --audit   Lee las configuraciones, evalua y genera el informe. NO modifica nada.
  --apply   Evalua, respalda la configuracion, pide confirmacion, aplica las
            correcciones, vuelve a evaluar y genera el informe antes/despues.

SEGURIDAD
  - No hay contrasenas en el codigo ni en devices.json. Se leen de variables de
    entorno (CIS_USER, CIS_PASS, CIS_PASS_<NOMBRE>, CIS_ENABLE, CIS_ENABLE_<NOMBRE>)
    o se piden de forma interactiva con getpass.
  - Antes de modificar un equipo se guarda un respaldo en backups/ (permisos 600).
  - Se pide confirmacion antes de aplicar cambios (se omite con --yes).
  - Los errores de conexion y de comandos se registran en el informe y no detienen
    la revision de los demas equipos.

USO
  pip install -r requirements.txt
  python3 cis_hardening.py --devices devices.json --audit
  python3 cis_hardening.py --devices devices.json --apply

devices.json (sin contrasenas; type = cisco_ios por defecto, o fortinet):
  [{"name": "R1",  "host": "10.7.1.1", "username": "admin"},
   {"name": "FW1", "type": "fortinet", "host": "10.7.2.1", "username": "admin"}]

Variables opcionales:
  ENABLE_SECRET  enable secret nuevo si el control H02 falla en un equipo Cisco
  CIS_BANNER     texto del banner de advertencia (por defecto uno generico)
"""
import argparse
import getpass
import html
import json
import os
import re
import sys
from datetime import datetime

BANNER_TEXT = os.environ.get(
    "CIS_BANNER", "Acceso restringido. Solo personal autorizado. Actividad monitoreada.")

# Redes desde las que se permite administrar el FortiGate (control F09)
TRUSTED_HOSTS = [("10.7.1.0", "255.255.255.0"), ("10.7.2.0", "255.255.255.252")]

BENCHMARKS = {
    "cisco_ios": "CIS Cisco IOS Benchmark v2.2",
    "fortinet": "CIS FortiGate 7.0.x Benchmark v1.3.0",
}

SCOPE_NOTE = ("Alcance: este informe evalua solo los controles seleccionados, "
              "basados en recomendaciones del CIS Benchmark. No es una auditoria CIS completa.")

# ---------------------------------------------------------------------------
# Controles Cisco IOS
#   cis_id: identificador en el benchmark ("Adicional" si no existe en el)
#   must_match / must_not_match: expresion regular sobre la configuracion
#   fix: comandos de correccion
# ---------------------------------------------------------------------------
CHECKS = [
    {"id": "H01", "cis_id": "1.1.4.4",
     "title": "Cifrado de contrasenas en la config (service password-encryption)",
     "why": "Evita que las contrasenas en texto claro se lean en 'show run' o en respaldos.",
     "must_match": r"^service password-encryption",
     "fix": ["service password-encryption"]},
    {"id": "H02", "cis_id": "1.1.4.1",
     "title": "Enable secret configurado (hash fuerte)",
     "why": "enable secret usa hash; 'enable password' es reversible.",
     "must_match": r"^enable secret \d",
     "fix": ["enable secret {ENABLE_SECRET}"], "needs_env": "ENABLE_SECRET"},
    {"id": "H03", "cis_id": "1.2.2.5",
     "title": "Servidor HTTP deshabilitado (no ip http server)",
     "why": "HTTP envia credenciales sin cifrar y amplia la superficie de ataque.",
     "must_not_match": r"^ip http server",
     "fix": ["no ip http server"]},
    {"id": "H04", "cis_id": "Adicional",
     "title": "SSH version 2",
     "why": "SSHv1 tiene fallas criptograficas conocidas. Requiere 'ip domain-name' y claves RSA.",
     "must_match": r"^ip ssh version 2",
     "fix": ["ip ssh version 2"]},
    {"id": "H05", "cis_id": "1.1.2.3",
     "title": "VTY solo con SSH (transport input ssh)",
     "why": "Telnet transmite todo en claro; solo se permite SSH.",
     "must_match": r"transport input ssh",
     "fix": ["line vty 0 4", "transport input ssh", "exit"]},
    {"id": "H06", "cis_id": "1.1.2.4",
     "title": "Timeout de sesion (sin exec-timeout 0 0)",
     "why": "Sesiones abiertas indefinidamente pueden ser secuestradas.",
     "must_not_match": r"exec-timeout 0 0",
     "fix": ["line vty 0 4", "exec-timeout 5 0", "exit",
             "line con 0", "exec-timeout 5 0", "exit",
             "line aux 0", "exec-timeout 5 0", "exit"]},
    {"id": "H07", "cis_id": "1.1.3.2",
     "title": "Banner de advertencia (banner login)",
     "why": "Aviso legal de acceso no autorizado; respaldo ante incidentes.",
     "must_match": r"^banner (login|motd)",
     "fix": ["banner login #" + BANNER_TEXT + "#"]},
    {"id": "H08", "cis_id": "1.2.2.1",
     "title": "CDP deshabilitado globalmente (no cdp run)",
     "why": "CDP revela modelo, IOS e IPs a quien este en el segmento.",
     "must_match": r"^no cdp run",
     "fix": ["no cdp run"]},
    {"id": "H09", "cis_id": "1.3.1.2",
     "title": "IP source routing deshabilitado",
     "why": "Permite al atacante dictar la ruta de los paquetes y evadir controles.",
     "must_match": r"^no ip source-route",
     "fix": ["no ip source-route"]},
    {"id": "H10", "cis_id": "1.2.3.2",
     "title": "Logging local en buffer",
     "why": "Sin logs locales no hay trazabilidad ni evidencia forense.",
     "must_match": r"^logging buffered",
     "fix": ["logging buffered 16384 informational"]},
    {"id": "H12", "cis_id": "1.2.3.7",
     "title": "Timestamps en los logs",
     "why": "Un log sin fecha y hora no sirve para correlacionar eventos.",
     "must_match": r"^service timestamps log datetime",
     "fix": ["service timestamps log datetime msec"]},
    {"id": "H11", "cis_id": "Adicional",
     "title": "Bloqueo ante intentos de login fallidos (login block-for)",
     "why": "Mitiga fuerza bruta contra SSH.",
     "must_match": r"^login block-for",
     "fix": ["login block-for 120 attempts 3 within 60"]},
    {"id": "H13", "cis_id": "Adicional",
     "title": "Servidor HTTPS deshabilitado (no ip http secure-server)",
     "why": "Si no se usa la GUI web, el servicio HTTPS solo agrega superficie de ataque.",
     "must_not_match": r"^ip http secure-server",
     "fix": ["no ip http secure-server"]},
]


# ---------------------------------------------------------------------------
# Controles FortiGate (se evalua cada seccion de 'show full-configuration')
# ---------------------------------------------------------------------------
def _fg_global(*lines):
    return ["config system global", *lines, "end"]


def _fg_trusthost_fix():
    cmds = ["config system admin", "edit admin"]
    for i, (net, mask) in enumerate(TRUSTED_HOSTS, start=1):
        cmds.append(f"set trusthost{i} {net} {mask}")
    return cmds + ["next", "end"]


FG_SHOW = {
    "global": "show full-configuration system global",
    "password-policy": "show full-configuration system password-policy",
    "admin": "show full-configuration system admin",
    "interface": "show full-configuration system interface",
    "snmp": "show full-configuration system snmp sysinfo",
}

FG_CHECKS = [
    {"id": "F01", "cis_id": "2.4.4", "section": "global",
     "title": "Timeout de administracion (admintimeout de 5 minutos o menos)",
     "why": "Una sesion de administracion abierta sin uso puede ser aprovechada por otra persona.",
     "must_match": r"^\s*set admintimeout [1-5]\s*$",
     "fix": _fg_global("set admintimeout 5")},
    {"id": "F02", "cis_id": "2.1.1", "section": "global",
     "title": "Banner previo al login (pre-login-banner)",
     "why": "Aviso legal de acceso no autorizado antes de autenticarse.",
     "must_match": r"^\s*set pre-login-banner enable\s*$",
     "fix": _fg_global("set pre-login-banner enable") +
            ['config system replacemsg admin "pre_admin-disclaimer-text"',
             'set buffer "' + BANNER_TEXT + '"', "end"]},
    {"id": "F04", "cis_id": "Adicional", "section": "global",
     "title": "GUI solo con TLS 1.2 o superior",
     "why": "TLS 1.0 y 1.1 tienen debilidades conocidas.",
     "must_not_match": r"^\s*set admin-https-ssl-versions .*\btlsv1-[01]\b",
     "fix": _fg_global("set admin-https-ssl-versions tlsv1-2 tlsv1-3")},
    {"id": "F05", "cis_id": "2.2.2", "section": "global",
     "title": "Bloqueo del admin tras 3 intentos fallidos",
     "why": "Frena ataques de fuerza bruta contra la cuenta admin.",
     "must_match": r"^\s*set admin-lockout-threshold [1-3]\s*$",
     "fix": _fg_global("set admin-lockout-threshold 3")},
    {"id": "F06", "cis_id": "2.2.2", "section": "global",
     "title": "Duracion del bloqueo de al menos 900 segundos",
     "why": "Un bloqueo muy corto casi no frena la fuerza bruta.",
     "must_match": r"^\s*set admin-lockout-duration (?:9\d\d|[1-9]\d{3,})\s*$",
     "fix": _fg_global("set admin-lockout-duration 900")},
    {"id": "F07", "cis_id": "2.2.1", "section": "password-policy",
     "title": "Politica de contrasenas habilitada",
     "why": "Sin politica, el equipo acepta contrasenas debiles.",
     "must_match": r"^\s*set status enable\s*$",
     "fix": ["config system password-policy", "set status enable",
             "set minimum-length 8", "end"]},
    {"id": "F08", "cis_id": "Adicional", "section": "password-policy",
     "title": "Complejidad de contrasena (mayuscula, minuscula, numero y simbolo)",
     "why": "Hace mucho mas costoso adivinar o crackear las contrasenas.",
     "must_match": [r"^\s*set min-upper-case-letter [1-9]",
                    r"^\s*set min-lower-case-letter [1-9]",
                    r"^\s*set min-number [1-9]",
                    r"^\s*set min-non-alphanumeric [1-9]"],
     "fix": ["config system password-policy", "set min-upper-case-letter 1",
             "set min-lower-case-letter 1", "set min-number 1",
             "set min-non-alphanumeric 1", "end"]},
    {"id": "F09", "cis_id": "2.4.2", "section": "admin",
     "title": "Hosts de confianza para el usuario admin (trusthost)",
     "why": "Limita desde que redes se puede administrar el equipo.",
     "must_match": r"^\s*set trusthost1 (?!0\.0\.0\.0)\S+ \S+",
     "fix": _fg_trusthost_fix()},
    {"id": "F10", "cis_id": "Adicional", "section": "interface",
     "title": "Sin HTTP ni Telnet en la administracion de las interfaces",
     "why": "HTTP y Telnet envian credenciales sin cifrar. Se corrige a mano por interfaz.",
     "must_not_match": r"^\s*set allowaccess .*\b(?:http|telnet)\b",
     "fix": None},
    {"id": "F11", "cis_id": "Adicional", "section": "snmp",
     "title": "Agente SNMP deshabilitado",
     "why": "Un agente SNMP sin uso solo agrega superficie de ataque.",
     "must_match": r"^\s*set status disable\s*$",
     "fix": ["config system snmp sysinfo", "set status disable", "end"]},
]

CHECKS_BY_TYPE = {"cisco_ios": CHECKS, "fortinet": FG_CHECKS}

# Patrones que indican que el equipo rechazo un comando
ERROR_PATTERNS = {
    "cisco_ios": re.compile(r"^% (?:Invalid|Incomplete|Ambiguous|Unknown).*$|Invalid input detected.*$",
                            re.M | re.I),
    "fortinet": re.compile(r"command parse error.*$|Command fail.*$|Unknown action.*$", re.M | re.I),
}


# ---------------------------------------------------------------------------
# Evaluacion
# ---------------------------------------------------------------------------
def evaluate(config, checks):
    """Devuelve [(control, 'PASS'|'FAIL')]. config es texto (Cisco) o dict seccion->texto."""
    results = []
    for c in checks:
        text = config[c["section"]] if c.get("section") else config
        if "must_match" in c:
            pats = c["must_match"]
            if isinstance(pats, str):
                pats = [pats]
            ok = all(re.search(p, text, re.M) for p in pats)
        else:
            ok = re.search(c["must_not_match"], text, re.M) is None
        results.append((c, "PASS" if ok else "FAIL"))
    return results


# ---------------------------------------------------------------------------
# Conexion y credenciales
# ---------------------------------------------------------------------------
def get_credentials(dev):
    """Usuario desde devices.json/CIS_USER; contrasenas desde entorno o getpass."""
    name = dev.get("name", dev["host"])
    key = re.sub(r"\W", "_", name).upper()
    user = dev.get("username") or os.environ.get("CIS_USER") or input(f"Usuario para {name}: ")
    pwd = os.environ.get(f"CIS_PASS_{key}") or os.environ.get("CIS_PASS")
    if not pwd:
        pwd = getpass.getpass(f"Contrasena de {user}@{name} ({dev['host']}): ")
    secret = ""
    if dev.get("type", "cisco_ios") != "fortinet":
        secret = os.environ.get(f"CIS_ENABLE_{key}") or os.environ.get("CIS_ENABLE")
        if secret is None:
            secret = getpass.getpass(f"Enable secret de {name} (Enter si no aplica): ")
    return user, pwd, secret


def connect(dev, user, pwd, secret):
    from netmiko import ConnectHandler  # import aqui para poder probar sin Netmiko
    dev_type = dev.get("type", "cisco_ios")
    params = dict(device_type=dev_type, host=dev["host"], username=user, password=pwd)
    if dev_type == "fortinet":  # la VM del FortiGate es lenta: mas tiempo de espera
        params.update(read_timeout_override=60, banner_timeout=30, auth_timeout=30)
    else:
        params["secret"] = secret
    conn = ConnectHandler(**params)
    if dev_type != "fortinet":
        conn.enable()
    return conn


def get_config(conn, dev_type):
    if dev_type == "fortinet":
        return {key: conn.send_command(cmd, read_timeout=60) for key, cmd in FG_SHOW.items()}
    return conn.send_command("show running-config")


def backup_config(conn, dev_type, name, config, backup_dir):
    """Guarda la configuracion completa antes de modificarla."""
    os.makedirs(backup_dir, exist_ok=True)
    if dev_type == "fortinet":
        text = conn.send_command("show full-configuration", read_timeout=180)
    else:
        text = config
    path = os.path.join(backup_dir, f"{name}_{datetime.now():%Y%m%d_%H%M%S}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(path, 0o600)
    return path


def confirm(question, assume_yes):
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print("No hay terminal interactiva: use --yes para confirmar los cambios.")
        return False
    return input(f"{question} Escriba SI para continuar: ").strip().upper() == "SI"


# ---------------------------------------------------------------------------
# Proceso por equipo
# ---------------------------------------------------------------------------
def process_device(dev, apply, assume_yes, backup_dir):
    dev_type = dev.get("type", "cisco_ios")
    name = dev.get("name", dev["host"])
    entry = {"name": name, "host": dev["host"], "type": dev_type,
             "benchmark": BENCHMARKS.get(dev_type, "-"),
             "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "before": [], "after": [], "applied": [], "errors": [],
             "backup": None, "error": None}
    if dev_type not in CHECKS_BY_TYPE:
        entry["error"] = f"Tipo de equipo no soportado: {dev_type}"
        return entry
    checks = CHECKS_BY_TYPE[dev_type]
    conn = None
    try:
        user, pwd, secret = get_credentials(dev)
        conn = connect(dev, user, pwd, secret)
        config = get_config(conn, dev_type)
        before = evaluate(config, checks)
        entry["before"] = [(c["id"], s) for c, s in before]
        failing = [c for c, s in before if s == "FAIL"]

        if apply and not failing:
            entry["after"] = list(entry["before"])
        elif apply:
            entry["backup"] = backup_config(conn, dev_type, name, config, backup_dir)
            if not confirm(f"Aplicar {len(failing)} correcciones en {name} ({dev['host']})?",
                           assume_yes):
                entry["errors"].append("Aplicacion cancelada: no se confirmo el cambio.")
            else:
                for c in failing:
                    cmds = c.get("fix")
                    if not cmds:
                        entry["applied"].append((c["id"], "MANUAL"))
                        continue
                    env = c.get("needs_env")
                    if env:
                        if not os.environ.get(env):
                            entry["applied"].append((c["id"], f"OMITIDO (falta {env})"))
                            continue
                        cmds = [x.replace("{" + env + "}", os.environ[env]) for x in cmds]
                    if dev_type == "fortinet":
                        out = conn.send_config_set(cmds, cmd_verify=False)
                    else:
                        out = conn.send_config_set(cmds)
                    err = ERROR_PATTERNS[dev_type].search(out or "")
                    if err:
                        entry["errors"].append(f"{c['id']}: {err.group(0).strip()}")
                        entry["applied"].append((c["id"], "ERROR"))
                    else:
                        entry["applied"].append((c["id"], "APLICADO"))
                if dev_type != "fortinet":  # FortiGate guarda cada cambio solo
                    conn.save_config()
                after = evaluate(get_config(conn, dev_type), checks)
                entry["after"] = [(c["id"], s) for c, s in after]
    except Exception as exc:  # noqa: BLE001 - se registra y se sigue con el siguiente equipo
        entry["error"] = str(exc).strip().splitlines()[0] if str(exc).strip() else repr(exc)
    finally:
        if conn is not None:
            try:
                conn.disconnect()
            except Exception:  # noqa: BLE001
                pass
    return entry


# ---------------------------------------------------------------------------
# Informes
# ---------------------------------------------------------------------------
def score(pairs):
    if not pairs:
        return "N/A"
    ok = sum(1 for _, s in pairs if s == "PASS")
    return f"{ok}/{len(pairs)} ({round(100 * ok / len(pairs))}%)"


def build_html(entries, mode):
    names = {c["id"]: c for c in CHECKS + FG_CHECKS}
    out = ["<html><head><meta charset='utf-8'><title>Informe CIS</title>"
           "<style>body{font-family:sans-serif}table{border-collapse:collapse}"
           "td,th{border:1px solid #999;padding:4px 8px;font-size:13px}"
           ".PASS{background:#c8f7c5}.FAIL{background:#f7c5c5}</style></head><body>",
           f"<h1>Informe de hardening - modo {mode}</h1>",
           f"<p>Generado: {datetime.now():%Y-%m-%d %H:%M:%S}</p>",
           f"<p><i>{html.escape(SCOPE_NOTE)}</i></p>"]
    for e in entries:
        out.append(f"<h2>{html.escape(e['name'])} ({e['host']}) - {e['type']}</h2>")
        out.append(f"<p>Benchmark de referencia: {html.escape(e['benchmark'])} | "
                   f"Fecha y hora de la auditoria: {e['started']}</p>")
        if e["error"]:
            out.append(f"<p><b>ERROR:</b> {html.escape(e['error'])}</p>")
            continue
        out.append(f"<p>Controles cumplidos antes: {score(e['before'])}"
                   + (f" | despues: {score(e['after'])}" if e["after"] else "") + "</p>")
        if e["backup"]:
            out.append(f"<p>Respaldo previo: {html.escape(e['backup'])}</p>")
        out.append("<table><tr><th>ID</th><th>CIS</th><th>Control</th><th>Por que</th>"
                   "<th>Antes</th><th>Accion</th><th>Despues</th></tr>")
        after = dict(e["after"])
        acts = dict(e["applied"])
        for cid, st in e["before"]:
            c = names[cid]
            af = after.get(cid, "-")
            out.append(f"<tr><td>{cid}</td><td>{html.escape(c['cis_id'])}</td>"
                       f"<td>{html.escape(c['title'])}</td><td>{html.escape(c['why'])}</td>"
                       f"<td class='{st}'>{st}</td><td>{html.escape(acts.get(cid, '-'))}</td>"
                       f"<td class='{af}'>{af}</td></tr>")
        out.append("</table>")
        if e["errors"]:
            out.append("<p><b>Errores durante la ejecucion:</b></p><ul>"
                       + "".join(f"<li>{html.escape(x)}</li>" for x in e["errors"]) + "</ul>")
    out.append("</body></html>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="Auditoria/hardening de controles seleccionados (Cisco IOS y FortiGate)")
    ap.add_argument("--devices", default="devices.json", help="JSON con la lista de equipos")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--audit", action="store_true", help="solo informe, no cambia nada")
    grp.add_argument("--apply", action="store_true",
                     help="respalda, aplica las correcciones y genera informe posterior")
    ap.add_argument("--yes", action="store_true", help="no pedir confirmacion al aplicar")
    ap.add_argument("--outdir", default="reports", help="carpeta de informes")
    ap.add_argument("--backupdir", default="backups", help="carpeta de respaldos")
    args = ap.parse_args()

    try:
        with open(args.devices, encoding="utf-8") as f:
            devices = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"No se pudo leer {args.devices}: {exc}")
        return 2

    mode = "APPLY" if args.apply else "AUDIT"
    entries = [process_device(d, args.apply, args.yes, args.backupdir) for d in devices]

    os.makedirs(args.outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.join(args.outdir, f"cis_{mode.lower()}_{stamp}")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    with open(base + ".html", "w", encoding="utf-8") as f:
        f.write(build_html(entries, mode))

    for e in entries:
        print(f"[{e['name']}] antes: {score(e['before'])}"
              + (f" -> despues: {score(e['after'])}" if e["after"] else "")
              + (f"  ERROR: {e['error']}" if e["error"] else "")
              + (f"  ({len(e['errors'])} aviso(s))" if e["errors"] else ""))
    print(f"Informes: {base}.html / {base}.json")
    return 1 if any(e["error"] for e in entries) else 0


if __name__ == "__main__":
    sys.exit(main())
