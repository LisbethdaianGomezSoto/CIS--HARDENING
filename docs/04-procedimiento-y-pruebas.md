# 04 · Procedimiento y pruebas

Procedimiento completo para reproducir el laboratorio, con el resultado esperado en cada etapa y la evidencia que se guarda.

## Etapa 1 · Preparar la topología en GNS3

1. Crear los nodos: Kali (VM), SW1 (IOSv L2), R1 (c2691), FW1 (FortiGate VM) y NAT1.
2. Conectar: Kali `eth1` ↔ SW1 `Gi0/1`; SW1 `Gi0/0` ↔ R1 `f0/1`; R1 `f0/0` ↔ FW1 `port1`; FW1 `port2` ↔ NAT1.
3. Encender todos los nodos y esperar a que los puntos pasen a verde.

**Evidencia:** Fig. 01 (topología).

## Etapa 2 · Configuración inicial

Aplicar por consola las configuraciones de [`configs/initial/`](../configs/initial/): `R1-initial.txt`, `SW1-initial.txt` y `FW1-initial.txt`. En Kali, aplicar `Kali-red.txt`.

- En FW1, el primer inicio de sesión (`admin`, contraseña vacía) pide definir una contraseña.
- Las contraseñas de R1 y SW1 aparecen como marcadores `<...>` y deben sustituirse.

## Etapa 3 · Verificar la conectividad

Desde Kali:

```bash
ping -c 3 10.7.1.1      # R1
ping -c 3 10.7.1.2      # SW1
ping -c 3 10.7.2.1      # FW1
ping -c 3 8.8.8.8       # Internet a través de FW1
```

**Esperado:** 0 % de pérdida en los cuatro. **Evidencia:** Fig. 02.

Acceso por SSH. Los IOS 12.4 solo ofrecen algoritmos antiguos, por lo que un cliente OpenSSH moderno necesita habilitarlos:

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa \
    -oCiphers=+aes128-cbc,aes256-cbc,3des-cbc admin@10.7.1.1
ssh admin@10.7.2.1      # FortiGate
```

**Esperado:** se muestra el banner y el prompt del equipo. **Evidencia:** Fig. 03.

## Etapa 4 · Preparar el script

```bash
cd scripts
pip install -r requirements.txt     # en Kali: apt install python3-netmiko
cp devices.example.json devices.json
```

Las credenciales no se guardan en archivos. Se pasan por variables de entorno o el script las solicita:

```bash
export CIS_PASS='<contraseña>'              # o CIS_PASS_R1, CIS_PASS_SW1, CIS_PASS_FW1
export CIS_ENABLE='<enable secret>'          # solo equipos Cisco
```

## Etapa 5 · Auditoría inicial (sin cambios)

```bash
python3 cis_hardening.py --devices devices.json --audit
```

**Esperado:** un porcentaje de cumplimiento por equipo y un informe en `reports/` con los controles en PASS o FAIL. El modo `--audit` no modifica ninguna configuración.

**Evidencia:** Fig. 04 (Cisco) y Fig. 05 (FortiGate).

## Etapa 6 · Aplicación del hardening

```bash
python3 cis_hardening.py --devices devices.json --apply
```

El script, para cada equipo con controles en FAIL:

1. guarda un respaldo en `backups/`,
2. pide confirmación (se omite con `--yes`),
3. aplica las correcciones y registra los comandos rechazados,
4. guarda la configuración y vuelve a evaluar,
5. genera el informe con el estado antes y después.

**Esperado:** todos los controles en PASS después de aplicar, excepto los marcados `MANUAL` (F10), que no tienen corrección automática. **Evidencia:** Fig. 06 a Fig. 09.

## Etapa 7 · Auditoría posterior

```bash
python3 cis_hardening.py --devices devices.json --audit
```

**Esperado:** 100 % de los controles seleccionados en PASS en los tres equipos. **Evidencia:** Fig. 10.

## Etapa 8 · Pruebas funcionales

| # | Dónde | Comando | Resultado esperado | Control | Fig. |
|---|---|---|---|---|---|
| 1 | Kali | `nmap -p 22,23,80,443 10.7.1.1 10.7.1.2` | Solo el puerto 22 abierto | H03, H05, H13 | 11 |
| 2 | Kali | `telnet 10.7.1.1` | Conexión rehusada | H05 | 12 |
| 3 | R1 | `show ip ssh` | `SSH Enabled - version 2.0` | H04 | 13 |
| 4 | R1 | `show cdp` | `% CDP is not enabled` | H08 | 13 |
| 5 | Kali | `curl -I https://example.com` | `HTTP/2 200` | Política de FW1 | 14 |
| 6 | Kali | `nc -vz -w 3 1.1.1.1 22` | Tiempo de espera agotado | Política de FW1 | 14 |
| 7 | FW1 | Cambiar la contraseña del admin con una que no cumple | Rechazada con la política exigida | F07, F08 | 15 |
| 8 | FW1 | `get system global \| grep lockout` y `show full-configuration system admin \| grep trusthost` | Bloqueo de 900 s y hosts de confianza configurados | F05, F06, F09 | 16 |
| 9 | R1 | `show logging` y `show run \| include service timestamps` | Eventos con fecha y hora | H10, H12 | 17 |
| 10 | Kali y R1 | Tres contraseñas incorrectas por SSH y `show login` | `Quiet-Mode` y `Denying logins from all sources` | H11 | 18 |

La prueba 10 bloquea los accesos al router durante 120 segundos; se realiza al final.

## Etapa 9 · Comparación de resultados

Ver la tabla de resultados en el [README](../README.md#15-resultados-de-las-auditorías) y los informes en [`reports/`](../reports/).
