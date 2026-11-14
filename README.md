<div style="background-color: #0d1117; padding: 30px 20px; border-radius: 10px;">

  <!-- 1. EL BANNER -->
  <div align="center" style="margin-bottom: 0;">
    <img src="images/banner-hardening.png" alt="Banner Hardening" style="width: 100%; max-width: 900px; height: 220px; object-fit: cover; border-radius: 6px 6px 0 0; display: block; margin: 0 auto;">
  </div>

  <!-- 2. LA LÍNEA DE COLOR DEBAJO DEL BANNER -->
  <div style="height: 4px; background: linear-gradient(90deg, #00e5ff, #ff00ff); width: 100%; max-width: 900px; margin: 0 auto 25px auto;"></div>

  <!-- 3. EL TÍTULO -->
  <h1 align="center" style="color: #ffffff; margin-bottom: 10px; font-weight: 600; font-size: 26px;">
    🛡️ Hardening de Redes con CIS Benchmark
  </h1>

  <!-- 4. EL SUBTÍTULO (Ya sin fondo gris, solo el texto resaltado) -->
  <p align="center" style="color: #00e5ff; font-size: 16px; margin-bottom: 10px;">
    <b>Router, Switch y Firewall en GNS3</b>
  </p>

  <!-- 5. DATOS DE LA AUTORA -->
  <p align="center" style="color: #8b949e; font-size: 13px; margin-bottom: 25px;">
    Autora: Lisbeth Gomez · Matrícula: 2025-0701
  </p>

  <!-- 6. LOS BADGES -->
  <div align="center" style="margin-bottom: 30px;">
    <img src="https://img.shields.io/badge/CISCO-IOS-00e5ff?style=for-the-badge&logo=cisco&logoColor=black" alt="Cisco">
    <img src="https://img.shields.io/badge/FORTIGATE-Firewall-ff00ff?style=for-the-badge&logo=fortinet&logoColor=white" alt="FortiGate">
    <img src="https://img.shields.io/badge/GNS3-Laboratorio-00e5ff?style=for-the-badge" alt="GNS3">
    <img src="https://img.shields.io/badge/PYTHON-Script-ff00ff?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/CIS-Benchmark-00e5ff?style=for-the-badge" alt="CIS">
  </div>

  <br>

  <!-- 7. EL BOTÓN DEL VIDEO (Estilo Badge Cian con ícono de Play) -->
  <h3 align="center" style="color: #ffffff; margin-bottom: 15px; font-size: 18px;">📹 Video demostrativo</h3>
  
  <div align="center" style="margin-bottom: 20px;">
    <a href="https://youtu.be/6xg6ZDsyll0" target="_blank">
      <img src="https://img.shields.io/badge/▶_VER_VIDEO_DEMOSTRATIVO-00e5ff?style=for-the-badge&logoColor=black" alt="Video">
    </a>
  </div>

</div>

<br>


## 📑 Índice de Contenido

- [1. Descripción general](#1-descripción-general)
- [2. Propósito del laboratorio](#2-propósito-del-laboratorio)
- [3. Objetivos](#3-objetivos)
- [4. Tecnologías y herramientas](#4-tecnologías-y-herramientas)
- [5. Arquitectura y topología de red](#5-arquitectura-y-topología-de-red)
- [6. Diagrama de la infraestructura](#6-diagrama-de-la-infraestructura)
- [7. Direccionamiento IP](#7-direccionamiento-ip)
- [8. Metodología de trabajo](#8-metodología-de-trabajo)
- [9. Conexión inicial de los equipos](#9-conexión-inicial-de-los-equipos)
- [10. CIS Benchmark seleccionados](#10-cis-benchmark-seleccionados)
- [11. Medidas de hardening aplicadas](#11-medidas-de-hardening-aplicadas)
- [12. Descripción de los scripts](#12-descripción-de-los-scripts)
- [13. Instrucciones de instalación y ejecución](#13-instrucciones-de-instalación-y-ejecución)
- [14. Auditoría inicial](#14-auditoría-inicial)
- [15. Resultados de las auditorías](#15-resultados-de-las-auditorías)
- [16. Comparación antes y después](#16-comparación-antes-y-después)
- [17. Evidencias de las pruebas](#17-evidencias-de-las-pruebas)
- [18. Conclusiones](#18-conclusiones)
- [19. Referencias y fuentes oficiales](#19-referencias-y-fuentes-oficiales)

---


## 1. Descripción general

Laboratorio de seguridad de redes en GNS3 con un **router Cisco**, un **switch Cisco** y un **firewall FortiGate**. Se evalúa la configuración de cada equipo con controles basados en recomendaciones del **CIS Benchmark**, se aplican medidas de hardening y se comprueba que funcionan. Un script de Python automatiza la auditoría y la aplicación de las reglas, y genera informes comparables antes y después.

## 2. Propósito del laboratorio

Demostrar, con evidencia real, el ciclo completo de hardening de una red: detectar configuraciones inseguras, corregirlas de forma controlada y verificar el resultado.

## 3. Objetivos

- Diseñar una red con router, switch y firewall.
- Evaluar los equipos con recomendaciones del CIS Benchmark.
- Aplicar hardening y documentar cada recomendación y su motivo.
- Probar que las medidas funcionan.
- Automatizar la auditoría y el hardening con un script con dos modos: solo informe, y aplicar con informe posterior.

## 4. Tecnologías y herramientas

| Herramienta | Uso |
|---|---|
| GNS3 | Simulación de la topología |
| Cisco IOS 12.4 (c2691) e IOSv L2 15.2 | Router y switch |
| FortiGate VM, FortiOS 7.0.9 | Firewall |
| Kali Linux | Estación de administración y pruebas |
| Python 3 y Netmiko | Script de auditoría y hardening |
| nmap, curl, netcat, OpenSSH | Pruebas |

Detalle y justificación en [docs/01-dispositivos-y-herramientas.md](docs/01-dispositivos-y-herramientas.md).

## 5. Arquitectura y topología de red

```
Kali ── SW1 ── R1 ── FW1 ── NAT1 (Internet)
```

- **SW1** (switch de acceso) y **R1** (router) forman la LAN `10.7.1.0/24`.
- **FW1** es el perímetro: aplica NAT y una política de salida restrictiva.
- **Kali** administra los equipos por SSH y ejecuta el script.

## 6. Diagrama de la infraestructura

![Diagrama de la topología](images/diagramas/topologia.svg)

![Figura 01 · Topología en GNS3](images/capturas/01-topologia-gns3.png)
*Figura 01 · Topología en GNS3.*

## 7. Direccionamiento IP

| Equipo | Interfaz | Dirección |
|---|---|---|
| Kali | eth1 | 10.7.1.10/24 |
| SW1 | Vlan 1 | 10.7.1.2/24 |
| R1 | f0/1 | 10.7.1.1/24 |
| R1 | f0/0 | 10.7.2.2/30 |
| FW1 | port1 | 10.7.2.1/30 |
| FW1 | port2 | DHCP (NAT de GNS3) |

Conexiones y flujo de tráfico en [docs/02-topologia-y-direccionamiento.md](docs/02-topologia-y-direccionamiento.md).

## 8. Metodología de trabajo

1. Selección de dispositivos, plataforma y herramienta.
2. Diseño de la topología y del direccionamiento.
3. Selección de las recomendaciones CIS.
4. Configuración inicial de los equipos.
5. Auditoría inicial con el script (`--audit`).
6. Aplicación del hardening (`--apply`).
7. Auditoría posterior.
8. Pruebas funcionales.
9. Documentación y evidencias.

Procedimiento paso a paso en [docs/04-procedimiento-y-pruebas.md](docs/04-procedimiento-y-pruebas.md).

## 9. Conexión inicial de los equipos

<div align="center">
  <img src="images/capturas/02-conectividad-kali.png" alt="Conectividad desde Kali" width="700">
  <p><i>Figura 02 · Conectividad desde Kali hacia R1, SW1, FW1 e Internet.</i></p>
</div>

<div align="center">
  <img src="images/capturas/03-ssh-fortigate-banner.png" alt="Acceso SSH a FW1 con banner" width="700">
  <p><i>Figura 03 · Acceso SSH a FW1 mostrando el banner de advertencia.</i></p>
</div>

Las configuraciones iniciales están en [`configs/initial/`](configs/initial/).

## 10. CIS Benchmark seleccionados

- **Cisco (R1 y SW1):** CIS Cisco IOS Benchmark v2.2, aplicable a IOS 12.x o superior.
- **FortiGate (FW1):** CIS FortiGate 7.0.x Benchmark v1.3.0.

| Equipo | Controles evaluados | Con ID CIS | Adicionales |
|---|---|---|---|
| R1 y SW1 | 13 | 10 | 3 (H04, H11, H13) |
| FW1 | 10 | 6 | 4 (F04, F08, F10, F11) |

Los controles **Adicionales** son buenas prácticas que no tienen identificador en el benchmark utilizado. Tabla completa, con problema, riesgo, configuración inicial y segura, aplicación y verificación, en [docs/03-recomendaciones-cis.md](docs/03-recomendaciones-cis.md).

## 11. Medidas de hardening aplicadas

| Área | Medidas |
|---|---|
| Acceso remoto | SSH versión 2, VTY solo con SSH, HTTP y HTTPS apagados, timeouts de sesión |
| Credenciales | Cifrado de contraseñas, enable secret, política de contraseñas en FW1 |
| Protección contra fuerza bruta | `login block-for` en Cisco; bloqueo de 15 minutos tras 3 intentos en FW1 |
| Exposición de información | CDP apagado, banner de advertencia, sin source routing |
| Trazabilidad | Logs en buffer con fecha y hora |
| Perímetro | Política de FW1 con NAT que solo permite DNS, HTTP, HTTPS y PING; trusted hosts para el administrador |

## 12. Descripción de los scripts

[`scripts/cis_hardening.py`](scripts/cis_hardening.py) se conecta por SSH a cada equipo con Netmiko, lee su configuración y evalúa los controles seleccionados.

| Modo | Qué hace |
|---|---|
| `--audit` | Evalúa y genera el informe. **No modifica nada.** |
| `--apply` | Evalúa, respalda, pide confirmación, aplica las correcciones, vuelve a evaluar y genera el informe antes y después. |

Medidas de seguridad del script:

- No guarda contraseñas: se leen de variables de entorno o se piden con `getpass`.
- Respaldo de la configuración antes de modificarla (`backups/`, permisos 600).
- Confirmación antes de aplicar cambios (`--yes` para omitirla).
- Los errores de conexión y los comandos rechazados se registran en el informe.
- Cada informe incluye nombre e IP, fecha y hora, controles evaluados, estado, cambios aplicados, errores y resultado posterior.

**Alcance:** comprueba un conjunto seleccionado de recomendaciones. No es una auditoría CIS completa.

![Diagrama de flujo del script](images/diagramas/flujo-script.svg)

## 13. Instrucciones de instalación y ejecución

```bash
# 1. Dependencias (en Kali también sirve: apt install python3-netmiko)
cd scripts
pip install -r requirements.txt

# 2. Lista de equipos, sin contraseñas
cp devices.example.json devices.json

# 3. Credenciales por variable de entorno (o el script las solicita)
export CIS_PASS='<contraseña>'            # o CIS_PASS_R1, CIS_PASS_SW1, CIS_PASS_FW1
export CIS_ENABLE='<enable secret>'       # solo equipos Cisco

# 4. Auditoría sin cambios
python3 cis_hardening.py --devices devices.json --audit

# 5. Hardening con informe posterior (pide confirmación; --yes la omite)
python3 cis_hardening.py --devices devices.json --apply
```

Los informes se guardan en `reports/` (HTML y JSON) y los respaldos en `backups/`.

### Estructura del repositorio

```
CIS-Hardening-GNS3/
├── README.md
├── docs/            Documentación del laboratorio
├── images/
│   ├── diagramas/   Topología y flujo del script
│   └── capturas/    Evidencias numeradas
├── configs/
│   ├── initial/     Configuración inicial de cada equipo
│   └── running-config/  Configuración final exportada
├── scripts/         Script de auditoría y hardening
├── reports/
│   ├── before/      Informes de la auditoría inicial
│   └── after/       Informes posteriores al hardening
└── evidence/        Salidas de las pruebas
```

## 14. Auditoría inicial

<div align="center">
  <img src="images/capturas/04-auditoria-inicial-cisco.png" alt="Auditoría inicial de R1 y SW1" width="700">
  <p><i>Figura 04 · Informe de la auditoría inicial de R1 y SW1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/05-auditoria-inicial-fortigate.png" alt="Auditoría inicial de FW1" width="700">
  <p><i>Figura 05 · Informe de la auditoría inicial de FW1.</i></p>
</div>

## 15. Resultados de las auditorías

Cumplimiento de los **controles seleccionados** (no de todo el benchmark):

| Equipo | Auditoría inicial | Después del hardening | Controles que fallaban |
|---|---|---|---|
| R1 | 3/12 (25 %) | 12/12 (100 %) | H01, H04, H05, H06, H07, H08, H09, H10, H11 |
| SW1 | 3/12 (25 %) | 12/12 (100 %) | H01, H03, H04, H05, H07, H08, H09, H10, H11 |
| FW1 | 6/10 (60 %) | 10/10 (100 %) | F06, F07, F08, F09 |

La prueba de puertos con nmap mostró el puerto 443 abierto en SW1, lo que llevó a incorporar el control **H13** (HTTPS apagado). Con los 13 controles, SW1 pasó de 12/13 a 13/13 y R1 se mantuvo en 13/13.

<div align="center">
  <img src="images/capturas/06-ejecucion-apply.png" alt="Ejecución del hardening" width="700">
  <p><i>Figura 06 · Ejecución de <code>--apply</code>.</i></p>
</div>

<div align="center">
  <img src="images/capturas/07-informe-apply-cisco.png" alt="Informe de aplicación en R1 y SW1" width="700">
  <p><i>Figura 07 · Informe de <code>--apply</code> en R1 y SW1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/08-informe-apply-sw1-h13.png" alt="Informe de aplicación del control H13" width="700">
  <p><i>Figura 08 · Informe de <code>--apply</code> con el control H13.</i></p>
</div>

<div align="center">
  <img src="images/capturas/09-informe-apply-fortigate.png" alt="Informe de aplicación en FW1" width="700">
  <p><i>Figura 09 · Informe de <code>--apply</code> en FW1.</i></p>
</div>

## 16. Comparación antes y después

| Equipo | Antes | Después |
|---|---|---|
| R1 | 3/12 (25 %) | 13/13 (100 %) |
| SW1 | 3/12 (25 %) | 13/13 (100 %) |
| FW1 | 6/10 (60 %) | 10/10 (100 %) |

La auditoría inicial de R1 y SW1 evaluó 12 controles; el estado final incluye los 13 (se sumó H13).

<br>

<div align="center">
  <img src="images/capturas/10-auditoria-final.png" alt="Auditoría Final" width="700">
  <p><i>Figura 10 · Auditoría posterior al hardening.</i></p>
</div>


Los informes completos están en [`reports/before`](reports/before) y [`reports/after`](reports/after).

## 17. Evidencias de las pruebas

| # | Prueba | Resultado | Control | Evidencia |
|---|---|---|---|---|
| 1 | `nmap -p 22,23,80,443 10.7.1.1 10.7.1.2` | Solo el puerto 22 abierto | H03, H05, H13 | Fig. 11 |
| 2 | `telnet 10.7.1.1` | Conexión rehusada | H05 | Fig. 12 |
| 3 | `show ip ssh` y `show cdp` en R1 | SSH versión 2.0 y CDP desactivado | H04, H08 | Fig. 13 |
| 4 | `curl -I https://example.com` y `nc -vz -w 3 1.1.1.1 22` | HTTPS permitido; SSH hacia Internet sin respuesta | Política de FW1 | Fig. 14 |
| 5 | Cambio de contraseña de FW1 | Se exige la política de contraseñas | F07, F08 | Fig. 15 |
| 6 | Bloqueo y hosts de confianza en FW1 | `lockout-duration 900` y `trusthost` configurados | F05, F06, F09 | Fig. 16 |
| 7 | `show logging` en R1 | Eventos con fecha y hora | H10, H12 | Fig. 17 |
| 8 | Tres contraseñas incorrectas y `show login` | Quiet-Mode activo | H11 | Fig. 18 |

## 17. Evidencias de las pruebas

| # | Prueba | Resultado | Control | Evidencia |
|---|---|---|---|---|
| 1 | `nmap -p 22,23,80,443 10.7.1.1 10.7.1.2` | Solo el puerto 22 abierto | H03, H05, H13 | Fig. 11 |
| 2 | `telnet 10.7.1.1` | Conexión rehusada | H05 | Fig. 12 |
| 3 | `show ip ssh` y `show cdp` en R1 | SSH versión 2.0 y CDP desactivado | H04, H08 | Fig. 13 |
| 4 | `curl -I https://example.com` y `nc -vz -w 3 1.1.1.1 22` | HTTPS permitido; SSH hacia Internet sin respuesta | Política de FW1 | Fig. 14 |
| 5 | Cambio de contraseña de FW1 | Se exige la política de contraseñas | F07, F08 | Fig. 15 |
| 6 | Bloqueo y hosts de confianza en FW1 | `lockout-duration 900` y `trusthost` configurados | F05, F06, F09 | Fig. 16 |
| 7 | `show logging` en R1 | Eventos con fecha y hora | H10, H12 | Fig. 17 |
| 8 | Tres contraseñas incorrectas y `show login` | Quiet-Mode activo | H11 | Fig. 18 |

<br>

<div align="center">
  <img src="images/capturas/11-nmap-puertos.png" alt="nmap" width="700">
  <p><i>Figura 11 · Puertos abiertos en R1 y SW1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/12-telnet-rechazado.png" alt="Telnet rechazado" width="700">
  <p><i>Figura 12 · Telnet rechazado por R1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/13-ssh-version2-cdp.png" alt="SSH versión 2 y CDP" width="700">
  <p><i>Figura 13 · SSH versión 2 y CDP desactivado en R1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/14-politica-firewall-curl-nc.png" alt="Política del firewall" width="700">
  <p><i>Figura 14 · Política de FW1: HTTPS permitido y SSH hacia Internet sin respuesta.</i></p>
</div>

<div align="center">
  <img src="images/capturas/15-politica-contrasenas-fortigate.png" alt="Política de contraseñas" width="700">
  <p><i>Figura 15 · Política de contraseñas exigida por FW1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/16-lockout-trusthost-fortigate.png" alt="Bloqueo y hosts de confianza" width="700">
  <p><i>Figura 16 · Bloqueo del administrador y hosts de confianza en FW1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/17-logs-timestamps.png" alt="Logs con fecha y hora" width="700">
  <p><i>Figura 17 · Logs con fecha y hora en R1.</i></p>
</div>

<div align="center">
  <img src="images/capturas/18-quiet-mode-r1.png" alt="Quiet-Mode" width="700">
  <p><i>Figura 18 · R1 en Quiet-Mode tras intentos fallidos.</i></p>
</div>

<div align="center">
  <img src="images/capturas/18-quiet-mode-r1.png" alt="Quiet-Mode" width="700">
  <p><i>Figura 18 · R1 en Quiet-Mode tras intentos fallidos.</i></p>
</div>


[configs/running-config](https://github.com/LisbethdaianGomezSoto/CIS--HARDENING/tree/main/configs/running-config)


## 18. Conclusiones

- Los tres equipos alcanzaron el 100 % de los controles seleccionados, con evidencia en informes generados por el script y en pruebas funcionales.
- Automatizar la auditoría permite repetirla y comparar el estado antes y después de cada cambio.
- Un informe al 100 % solo refleja lo que se mide: la comprobación con nmap detectó un puerto abierto que el script aún no cubría y permitió ampliarlo.
- El alcance se limita a las recomendaciones seleccionadas; no sustituye una auditoría CIS completa.

## 19. Referencias y fuentes oficiales

- Center for Internet Security, CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks
- CIS Cisco IOS Benchmark v2.2: https://www.cisecurity.org/-/jssmedia/Project/cisecurity/cisecurity/data/media/files/uploads/2017/04/CIS_Cisco_IOS_Benchmark_v22.pdf
- CIS FortiGate 7.0.x Benchmark v1.3.0 (resumen público): https://www.tenable.com/audits/CIS_Fortigate_7.0.x_v1.3.0_L1
- Cisco, *Harden Cisco IOS Devices*: https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html
- Fortinet, documentación de FortiOS: https://docs.fortinet.com
- Netmiko: https://github.com/ktbyers/netmiko · GNS3: https://www.gns3.com · Nmap: https://nmap.org

Lista completa en [docs/05-referencias.md](docs/05-referencias.md).
