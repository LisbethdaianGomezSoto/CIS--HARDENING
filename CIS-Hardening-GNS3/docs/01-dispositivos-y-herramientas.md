# 01 · Dispositivos, plataforma y herramientas

Este documento explica qué equipos se usaron en el laboratorio, por qué se eligieron y con qué herramienta se evaluó su seguridad.

## Dispositivos seleccionados

| Equipo | Plataforma y versión | Rol en la red | Benchmark de referencia |
|---|---|---|---|
| **FW1** | FortiGate VM, FortiOS 7.0.9 | Firewall perimetral con NAT y política de salida | CIS FortiGate 7.0.x Benchmark v1.3.0 |
| **R1** | Cisco c2691, IOS 12.4(25d) | Router entre la LAN y el firewall | CIS Cisco IOS Benchmark v2.2 |
| **SW1** | Cisco IOSv L2, IOS 15.2 | Switch de acceso de la LAN | CIS Cisco IOS Benchmark v2.2 |
| **Kali** | Kali Linux (VM) | Estación de administración y auditoría | — |

### Por qué estos equipos
- **Los tres tipos de dispositivo.** El laboratorio incluye router, switch y firewall, de modo que se comprueba el hardening en cada capa: acceso (SW1), enrutamiento (R1) y perímetro (FW1).
- **Versiones con benchmark disponible.** El CIS Cisco IOS Benchmark v2.2 indica que aplica a Cisco IOS 12.x o superior, lo que cubre R1 (12.4) y SW1 (15.2). Para FW1 existe el CIS FortiGate Benchmark para la rama 7.0.x.
- **Gestión remota por SSH.** Los tres equipos se administran por SSH, lo que permite automatizar la auditoría y el hardening desde Kali.
- **Plataformas gratuitas o de laboratorio.** Todo se ejecuta en GNS3 con imágenes de laboratorio.

## Herramienta de evaluación

La evaluación se hace con el script [`cis_hardening.py`](../scripts/cis_hardening.py), desarrollado para este laboratorio con Python y Netmiko:

- Se conecta por SSH a cada equipo, lee su configuración y evalúa cada control con expresiones regulares.
- Cada control está asociado al identificador de la recomendación CIS correspondiente. Los controles que no figuran en el benchmark utilizado se marcan como **Adicional** (buenas prácticas).
- Tiene dos modos: `--audit` (sin cambios) y `--apply` (hardening y auditoría posterior).

**Alcance.** El script comprueba un conjunto *seleccionado* de recomendaciones (13 en Cisco IOS y 10 en FortiGate). No es una auditoría CIS completa ni declara un nivel de cumplimiento del benchmark.

## Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| GNS3 | Simulación de la topología |
| Kali Linux | Estación de administración, auditoría y pruebas |
| Python 3 y Netmiko | Automatización de la auditoría y el hardening |
| OpenSSH (cliente) | Acceso a los equipos |
| nmap | Comprobación de puertos abiertos |
| curl y netcat | Pruebas de la política del firewall |
| Navegador web | Lectura de los informes HTML |
