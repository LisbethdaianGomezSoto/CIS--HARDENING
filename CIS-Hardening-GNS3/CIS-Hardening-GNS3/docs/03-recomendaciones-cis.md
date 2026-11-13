# 03 · Recomendaciones CIS seleccionadas

Para cada recomendación se documenta el identificador, el problema y su riesgo, la configuración inicial y la segura, cómo se aplica, cómo se verifica y dónde está la evidencia.

- **Benchmark Cisco:** CIS Cisco IOS Benchmark v2.2 (aplica a IOS 12.x o superior). Equipos: R1 (IOS 12.4) y SW1 (IOS 15.2).
- **Benchmark FortiGate:** CIS FortiGate 7.0.x Benchmark v1.3.0. Equipo: FW1 (FortiOS 7.0.9).
- Los controles marcados **Adicional** son buenas prácticas de seguridad que no tienen identificador en el benchmark utilizado.
- El benchmark no se redistribuye en este repositorio: consulte los enlaces en [05-referencias.md](05-referencias.md).

> El script verifica la presencia o ausencia de cada configuración. El número de figura indica la captura que demuestra el resultado.

## Router R1 y switch SW1 (Cisco IOS)

| ID (CIS) | Problema y riesgo | Configuración inicial → segura | Aplicación y verificación | Evidencia |
|---|---|---|---|---|
| **H01** (1.1.4.4) Cifrado de contraseñas | Las contraseñas locales quedan legibles en la configuración y en los respaldos | Sin `service password-encryption` → habilitado | `service password-encryption` · `show run \| include service password` | Fig. 04, 07 |
| **H02** (1.1.4.1) Enable secret | `enable password` se guarda reversible; `enable secret` usa hash | `enable secret` ya configurado (cumplido desde el inicio) | `enable secret <valor>` · `show run \| include enable` | Fig. 04 |
| **H03** (1.2.2.5) Servidor HTTP apagado | HTTP envía credenciales sin cifrar y amplía la superficie de ataque | R1: ya apagado. SW1: `ip http server` activo → `no ip http server` | `no ip http server` · `nmap -p 80` | Fig. 04, 07, 11 |
| **H04** (Adicional) SSH versión 2 | SSHv1 tiene fallas criptográficas conocidas | `show ip ssh`: versión 1.99 → `ip ssh version 2` | `ip ssh version 2` · `show ip ssh` muestra `version 2.0` | Fig. 13 |
| **H05** (1.1.2.3) VTY solo con SSH | Telnet transmite usuario y contraseña en claro | `transport input all` → `transport input ssh` | `line vty 0 4` / `transport input ssh` · `telnet 10.7.1.1` y `nmap -p 23` | Fig. 11, 12 |
| **H06** (1.1.2.4) Timeout de sesión | Una sesión abierta sin límite puede ser secuestrada | R1: `exec-timeout 0 0` en consola y auxiliar. SW1: valor por defecto → `exec-timeout 5 0` | `exec-timeout 5 0` en vty, con y aux · `show run \| section line` | Fig. 04 |
| **H07** (1.1.3.2) Banner de advertencia | Sin aviso legal es más difícil actuar contra un acceso no autorizado | Sin `banner login` → banner de acceso restringido | `banner login #<texto>#` · el banner aparece al conectar por SSH | Fig. 07 |
| **H08** (1.2.2.1) CDP apagado | CDP revela modelo, versión de IOS e IPs a cualquiera del segmento | CDP activo → `no cdp run` | `no cdp run` · `show cdp` responde `% CDP is not enabled` | Fig. 13 |
| **H09** (1.3.1.2) Sin source routing | Permite a un atacante dictar la ruta de los paquetes | Sin `no ip source-route` → configurado | `no ip source-route` · `show run \| include source-route` | Fig. 07 |
| **H10** (1.2.3.2) Logging en buffer | Sin logs locales no hay trazabilidad ni evidencia | Sin `logging buffered` → `logging buffered 16384 informational` | `logging buffered 16384 informational` · `show logging` | Fig. 17 |
| **H12** (1.2.3.7) Timestamps en logs | Un log sin fecha y hora no sirve para correlacionar eventos | `service timestamps log datetime msec` ya presente | `service timestamps log datetime msec` · `show run \| include service timestamps` | Fig. 17 |
| **H11** (Adicional) Bloqueo por intentos fallidos | La fuerza bruta contra SSH no tiene freno | Sin `login block-for` → `login block-for 120 attempts 3 within 60` | `login block-for 120 attempts 3 within 60` · tres contraseñas incorrectas y `show login` | Fig. 18 |
| **H13** (Adicional) Servidor HTTPS apagado | Si no se usa la GUI web, el puerto 443 solo agrega superficie de ataque | SW1: puerto 443 abierto → `no ip http secure-server` | `no ip http secure-server` · `nmap -p 443` | Fig. 08, 11 |

**Nota sobre H06.** El control verifica que no exista `exec-timeout 0 0` (sesiones sin límite). La recomendación CIS indica un máximo de 10 minutos; se aplica 5 minutos en R1.

## Firewall FW1 (FortiGate)

| ID (CIS) | Problema y riesgo | Configuración inicial → segura | Aplicación y verificación | Evidencia |
|---|---|---|---|---|
| **F01** (2.4.4) Timeout de administración | Una sesión inactiva puede ser aprovechada por otra persona | `admintimeout 5` ya configurado | `config system global` / `set admintimeout 5` · `get system global \| grep admintimeout` | Fig. 05 |
| **F02** (2.1.1) Banner previo al login | Sin aviso legal antes de autenticarse | `pre-login-banner` habilitado desde la configuración inicial | `set pre-login-banner enable` y mensaje `pre_admin-disclaimer-text` · el banner aparece al conectar | Fig. 03 |
| **F04** (Adicional) GUI solo con TLS 1.2 o superior | TLS 1.0 y 1.1 tienen debilidades conocidas | Sin versiones antiguas (cumplido) | `set admin-https-ssl-versions tlsv1-2 tlsv1-3` · `get system global \| grep ssl-versions` | Fig. 05 |
| **F05** (2.2.2) Reintentos del administrador | Sin límite de intentos, la cuenta admin es vulnerable a fuerza bruta | `admin-lockout-threshold 3` (cumplido) | `set admin-lockout-threshold 3` · `get system global \| grep lockout` | Fig. 16 |
| **F06** (2.2.2) Duración del bloqueo | Un bloqueo muy corto casi no frena la fuerza bruta | `admin-lockout-duration 60` → `900` | `set admin-lockout-duration 900` · `get system global \| grep lockout` | Fig. 05, 09, 16 |
| **F07** (2.2.1) Política de contraseñas | Sin política, el equipo acepta contraseñas débiles | `status disable` → `status enable` | `config system password-policy` / `set status enable` · al cambiar la contraseña muestra la política exigida | Fig. 09, 15 |
| **F08** (Adicional) Complejidad de contraseña | Contraseñas simples son fáciles de adivinar | Sin mínimos → mayúscula, minúscula, número y símbolo (1 de cada) | `set min-upper-case-letter 1` y equivalentes · `show full-configuration system password-policy \| grep min-` | Fig. 15 |
| **F09** (2.4.2) Hosts de confianza | Cualquier red puede intentar administrar el equipo | `trusthost1 0.0.0.0 0.0.0.0` → `10.7.1.0/24` y `10.7.2.0/30` | `config system admin` / `edit admin` / `set trusthost1 ...` · `show full-configuration system admin \| grep trusthost` | Fig. 09, 16 |
| **F10** (Adicional) Sin HTTP ni Telnet en interfaces | HTTP y Telnet envían credenciales sin cifrar | port1: `ping ssh https`; port2: `ping` (cumplido) | Se corrige a mano por interfaz · `show full-configuration system interface \| grep allowaccess` | Fig. 05 |
| **F11** (Adicional) SNMP deshabilitado | Un agente SNMP sin uso agrega superficie de ataque | `status disable` (cumplido) | `config system snmp sysinfo` / `set status disable` | Fig. 05 |

## Política de firewall (medida de seguridad de la topología)

Además de los controles anteriores, FW1 aplica la política **LAN-a-Internet**:

| Elemento | Valor |
|---|---|
| Origen → destino | port1 (LAN) → port2 (Internet) |
| Servicios permitidos | DNS, HTTP, HTTPS, PING |
| NAT | Habilitado |
| Registro | `logtraffic all` |
| Todo lo demás | Denegado por la regla implícita |

Se comprueba con `curl -I https://example.com` (permitido) y `nc -vz -w 3 1.1.1.1 22` (sin respuesta). Evidencia: Fig. 14.
