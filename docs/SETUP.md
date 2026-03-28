# 🔧 Guía de Configuración Detallada

Esta guía te llevará paso a paso desde una instalación limpia hasta tener el inventario de Proxmox funcionando completamente.

## 📋 Requisitos Previos

### Sistema Operativo
- ✅ Linux (Ubuntu, CentOS, Debian)
- ✅ Windows 10/11 (con WSL recomendado)
- ✅ macOS

### Software Requerido
- Python 3.8 o superior
- pip (gestor de paquetes Python)
- git (para clonar el repositorio)
- Acceso de red a tus servidores Proxmox

### Permisos Proxmox
- Usuario con acceso API (recomendado: `root@pam`)
- Permisos de lectura en VMs y nodos
- Acceso al puerto 8006 (HTTPS API)

## 🚀 Instalación Paso a Paso

### 1. Preparar el Entorno

#### En Linux/macOS:
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# sudo yum update -y                     # CentOS/RHEL

# Verificar Python
python3 --version  # Debe ser 3.8+

# Instalar pip si no está disponible
sudo apt install python3-pip python3-venv git -y  # Ubuntu/Debian
# sudo yum install python3-pip git -y              # CentOS/RHEL
```

#### En Windows:
```powershell
# Instalar Python desde https://python.org
# Verificar instalación
python --version

# Instalar git desde https://git-scm.com
git --version
```

### 2. Clonar y Configurar Proyecto

```bash
# Clonar repositorio
git clone https://github.com/carrionmecapp/skt-pve-inventory.git
cd skt-pve-inventory

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows CMD
# venv\Scripts\Activate.ps1     # Windows PowerShell
```

### 3. Instalar Dependencias

```bash
# Verificar que el entorno virtual esté activo
which python  # Debe mostrar la ruta del venv

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
python3 main.py --help
```

### 4. Configuración Inicial

```bash
# Crear archivo de configuración ejemplo
python3 main.py --create-example

# Verificar que se creó
ls -la .env.example

# Copiar para personalizar
cp .env.example .env
```

## ⚙️ Configuración de Proxmox

### 1. Obtener Información de Conexión

Para cada servidor Proxmox necesitas:

- **Host**: IP o FQDN del servidor
- **Usuario**: Cuenta con acceso API (ej: `root@pam`)
- **Contraseña**: Password del usuario
- **SSL**: `true` si usas certificados válidos, `false` para self-signed
- **Nombre**: Identificador personalizado para el cluster

### 2. Editar Archivo .env

```bash
nano .env  # o tu editor preferido
```

#### Configuración Básica (Un Servidor):
```env
PROXMOX_HOST1=192.168.1.100
PROXMOX_USER1=root@pam
PROXMOX_PASS1=tu_password_seguro
PROXMOX_SSL1=false
PROXMOX_NAME1=Production-Server
```

#### Configuración Multi-Cluster:
```env
# Servidor 1 - Producción
PROXMOX_HOST1=pve-prod.company.com
PROXMOX_USER1=root@pam
PROXMOX_PASS1=prod_password
PROXMOX_SSL1=true
PROXMOX_NAME1=Production-Cluster

# Servidor 2 - Desarrollo
PROXMOX_HOST2=pve-dev.company.com
PROXMOX_USER2=root@pam
PROXMOX_PASS2=dev_password
PROXMOX_SSL2=false
PROXMOX_NAME2=Development-Cluster

# Servidor 3 - Pruebas
PROXMOX_HOST3=192.168.10.50
PROXMOX_USER3=api@pve
PROXMOX_PASS3=test_password
PROXMOX_SSL3=false
PROXMOX_NAME3=Testing-Environment
```

### 3. Probar Conectividad

```bash
# Verificar conectividad de red
ping pve-prod.company.com

# Probar conexión API manualmente
curl -k https://pve-prod.company.com:8006/api2/json/version

# Ejecutar primera prueba
python3 main.py --output csv
```

## 🛡️ Configuración de Seguridad

### 1. Usuario API Dedicado (Recomendado)

En lugar de usar `root@pam`, crea un usuario específico:

#### En Proxmox Web UI:
1. **Datacenter** → **Permissions** → **Users** → **Add**
2. Crear usuario: `api-inventory@pve`
3. **Datacenter** → **Permissions** → **Add** → **User Permission**
4. Asignar rol: `PVEAuditor` o custom con permisos de lectura

#### Actualizar .env:
```env
PROXMOX_USER1=api-inventory@pve
PROXMOX_PASS1=secure_api_password
```

### 2. Autenticación por Token (Avanzado)

#### Crear Token en Proxmox:
1. **Datacenter** → **Permissions** → **API Tokens** → **Add**
2. Token ID: `inventory-script`
3. Quitar "Privilege Separation"

#### Modificar código para usar tokens:
```python
# En modules/proxmox_api.py, función authenticate()
# Reemplazar password auth con token auth
```

### 3. Restricciones de Red

```bash
# Permitir solo IPs específicas en firewall Proxmox
# Datacenter → Firewall → Add Rule
# Action: ACCEPT
# Type: in
# Source: tu.ip.servidor.script/32
# Dest Port: 8006
```

## 📊 Configuración SharePoint (Opcional)

### 1. Registro en Azure AD

Ver [SHAREPOINT_GUIDE.md](SHAREPOINT_GUIDE.md) para configuración completa.

### 2. Configuración Básica

```bash
# Agregar configuración SharePoint al .env
python3 main.py --setup-sharepoint

# Editar .env con tus credenciales Azure
nano .env
```

Agregar al final del .env:
```env
SHAREPOINT_TENANT_ID=tu-tenant-id-azure
SHAREPOINT_CLIENT_ID=tu-app-id
SHAREPOINT_CLIENT_SECRET=tu-secret
SHAREPOINT_URL=https://tuempresa.sharepoint.com
SHAREPOINT_SITE_NAME=IT-Operations
SHAREPOINT_DEFAULT_FOLDER=Proxmox-VMs
SHAREPOINT_DEFAULT_FILENAME=inventario_vms.xlsx
```

## 🧪 Verificación de Configuración

### 1. Test de Dependencias
```bash
python3 main.py --output excel  # Debe mostrar checkmarks verdes
```

### 2. Test de Conectividad Proxmox
```bash
# Inventario solo local para probar conexiones
python3 main.py --output json
cat Inventory/proxmox_multi_cluster_inventory_*.json | jq .
```

### 3. Test SharePoint (si configurado)
```bash
python3 main.py --output sharepoint
```

## 🔄 Automatización y Programación

### 1. Script de Ejecución

Crear `run_inventory.sh`:
```bash
#!/bin/bash
cd /path/to/proxmox-inventory
source venv/bin/activate
python3 main.py --output all
deactivate
```

```bash
chmod +x run_inventory.sh
```

### 2. Programación con Cron

```bash
# Editar crontab
crontab -e

# Agregar ejecución automática
# Todos los días a las 6:00 AM
0 6 * * * /path/to/proxmox-inventory/run_inventory.sh > /var/log/proxmox-inventory.log 2>&1

# Solo días laborables a las 8:00 AM
0 8 * * 1-5 /path/to/proxmox-inventory/run_inventory.sh

# Primer día del mes a las 9:00 AM (reporte mensual)
0 9 1 * * /path/to/proxmox-inventory/run_inventory.sh
```

### 3. Logging y Monitoreo

Crear `run_inventory_with_logging.sh`:
```bash
#!/bin/bash
LOG_FILE="/var/log/proxmox-inventory-$(date +%Y%m%d).log"
echo "$(date): Iniciando inventario Proxmox" >> $LOG_FILE

cd /path/to/proxmox-inventory
source venv/bin/activate

if python3 main.py --output sharepoint >> $LOG_FILE 2>&1; then
    echo "$(date): Inventario completado exitosamente" >> $LOG_FILE
else
    echo "$(date): Error en inventario" >> $LOG_FILE
    # Opcional: enviar email de alerta
    echo "Error en inventario Proxmox" | mail -s "Alert: Proxmox Inventory Failed" admin@company.com
fi

deactivate
```

## 🔍 Solución de Problemas Comunes

### Error: "No module named 'requests'"
```bash
# Verificar que el venv esté activo
which python
source venv/bin/activate
pip install requests
```

### Error: "Connection refused" en Proxmox
```bash
# Verificar conectividad
telnet your-proxmox-server.com 8006

# Verificar firewall
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

### Error: "SSL Certificate verify failed"
```bash
# Configurar SSL=false en .env
PROXMOX_SSL1=false

# O instalar certificados
sudo apt update && sudo apt install ca-certificates
```

### Error: "Permission denied" en SharePoint
```bash
# Verificar configuración Azure AD
# Ver SHAREPOINT_GUIDE.md para permisos correctos
```

### Archivos de inventario no se crean
```bash
# Verificar permisos de escritura
ls -la Inventory/
chmod 755 Inventory/

# Verificar espacio en disco
df -h
```

## 📈 Optimización y Rendimiento

### 1. Configuración para Muchas VMs
```python
# En modules/proxmox_api.py, ajustar timeouts
self.session.timeout = 30  # Aumentar timeout
```

### 2. Paralelización (Avanzado)
```python
# Modificar inventory_manager.py para procesamiento paralelo
from concurrent.futures import ThreadPoolExecutor
```

### 3. Caché de Resultados
```bash
# Crear script que cache resultados por 1 hora
# Útil para dashboards que consultan frecuentemente
```

## 🔄 Mantenimiento

### 1. Actualización de Dependencias
```bash
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt
```

### 2. Backup de Configuración
```bash
# Backup regular del .env (sin passwords)
cp .env .env.backup.$(date +%Y%m%d)
```

### 3. Logs y Limpieza
```bash
# Limpiar logs antiguos
find /var/log -name "proxmox-inventory-*" -mtime +30 -delete

# Limpiar archivos de inventario antiguos
find Inventory/ -name "*.json" -mtime +7 -delete
```

---

¿Problemas con la configuración? Consulta [SHAREPOINT_GUIDE.md](SHAREPOINT_GUIDE.md) o abre un [Issue](https://github.com/tu-usuario/proxmox-inventory/issues).
