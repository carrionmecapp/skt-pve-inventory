# 🚀 Proxmox Multi-Cluster Inventory Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SharePoint Compatible](https://img.shields.io/badge/SharePoint-Compatible-green.svg)](https://www.microsoft.com/sharepoint)

**Herramienta profesional para generar inventarios automatizados de máquinas virtuales en múltiples clusters Proxmox VE con integración directa a SharePoint.**

## 📋 Características

- 🔄 **Multi-cluster**: Inventario simultáneo de múltiples servidores Proxmox
- 📊 **Múltiples formatos**: CSV, JSON, Excel con formato profesional
- ☁️ **Integración SharePoint**: Subida automática con actualización inteligente
- 🔧 **Excel inteligente**: Preserva tablas dinámicas y formato personalizado
- 🛡️ **Manejo de errores**: Diagnóstico detallado y soluciones claras
- ⚡ **Configuración simple**: Archivo .env con ejemplos incluidos

## 🎯 ¿Qué información obtiene?

### Información de VMs
- **Básica**: ID, nombre, estado (running/stopped), nodo
- **Recursos**: CPU (cores/sockets), RAM (GB), almacenamiento total (GB)
- **Red**: Interfaces de red, IPs detectadas via QEMU Agent
- **Sistema**: Tipo de OS, agente habilitado, plantilla, protección
- **Metadatos**: Tags, descripción, fecha de actualización

### Información de Cluster
- **Identificación**: Nombre personalizable, tipo (cluster/standalone)
- **Nodos**: Estado online/offline de cada nodo
- **Organización**: Agrupación automática por cluster de origen

## 🚀 Inicio Rápido

### 1. Instalación
```bash
# Clonar repositorio
git clone https://github.com/carrionmecapp/skt-pve-inventory.git
cd skt-pve-inventory

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración
```bash
# Crear archivo de configuración
python3 main.py --create-example

# Copiar y personalizar
cp .env.example .env
nano .env  # Editar con tus credenciales
```

### 3. Ejecutar
```bash
# Inventario completo (CSV + JSON + Excel)
python3 main.py --output all

# Solo Excel local
python3 main.py --output excel

# Subir a SharePoint
python3 main.py --output sharepoint
```

## 📁 Estructura del Proyecto

```
proxmox-inventory/
├── main.py                    # Script principal
├── config/
│   ├── __init__.py
│   └── settings.py           # Gestión de configuración
├── modules/
│   ├── __init__.py
│   ├── proxmox_api.py        # Cliente API Proxmox
│   ├── inventory_manager.py   # Lógica de inventario
│   ├── excel_generator.py    # Generación Excel
│   └── sharepoint_uploader.py # Integración SharePoint
├── utils/
│   ├── __init__.py
│   └── validators.py         # Validaciones del sistema
├── Inventory/                # Archivos generados
├── requirements.txt
├── .env.example             # Configuración de ejemplo
└── docs/                    # Documentación
    ├── SETUP.md
    └── SHAREPOINT_GUIDE.md
```

## ⚙️ Configuración Detallada

### Proxmox
```env
# Servidor 1
PROXMOX_HOST1=your-proxmox-server.com
PROXMOX_USER1=root@pam
PROXMOX_PASS1=your_password
PROXMOX_SSL1=false
PROXMOX_NAME1=Production-Cluster

# Servidor 2
PROXMOX_HOST2=another-server.com
PROXMOX_USER2=root@pam
PROXMOX_PASS2=another_password
PROXMOX_SSL2=true
PROXMOX_NAME2=Development-Cluster
```

### SharePoint (Opcional)
```env
SHAREPOINT_TENANT_ID=your-tenant-id
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_URL=https://yourcompany.sharepoint.com
SHAREPOINT_SITE_NAME=IT-Operations
SHAREPOINT_DEFAULT_FOLDER=Proxmox-VMs
SHAREPOINT_DEFAULT_FILENAME=inventory_vms.xlsx
```

## 🎮 Comandos Disponibles

### Configuración
```bash
# Crear configuración ejemplo
python3 main.py --create-example

# Agregar configuración SharePoint
python3 main.py --setup-sharepoint
```

### Generación de Inventario
```bash
# Todos los formatos
python3 main.py --output all

# Formatos específicos
python3 main.py --output csv
python3 main.py --output json
python3 main.py --output excel
python3 main.py --output sharepoint
```

### SharePoint Personalizado
```bash
# Carpeta personalizada
python3 main.py --output sharepoint --sharepoint-folder "IT-Infrastructure"

# Archivo personalizado
python3 main.py --output sharepoint --sharepoint-filename "monthly_report.xlsx"

# Ambos
python3 main.py --output sharepoint \
  --sharepoint-folder "Reports/Monthly" \
  --sharepoint-filename "proxmox_inventory_$(date +%Y%m).xlsx"
```

## 📊 Integración con SharePoint

### Características Excel Inteligente
- ✅ **Actualización preservativa**: Mantiene tablas dinámicas y gráficos
- ✅ **Limpieza automática**: Solo actualiza datos, preserva estructura
- ✅ **Formato profesional**: Headers con colores, estados con códigos de color
- ✅ **Compatibilidad total**: Funciona con Excel Online y Desktop

### Organización Automática
Todos los archivos se organizan en:
```
/Inventory/[tu-carpeta]/archivo.xlsx
```

Ejemplos:
- `/Inventory/Proxmox-VMs/inventory_vms.xlsx`
- `/Inventory/IT-Infrastructure/monthly_report.xlsx`
- `/Inventory/Servers-Production/consolidated_view.xlsx`

## 🛡️ Solución de Problemas

### Error 423 - Archivo Bloqueado
```
🔒 Archivo bloqueado en SharePoint
💡 Solución: Cierra el archivo en SharePoint y vuelve a intentar
```

### Errores de Conexión Proxmox
```bash
# Verificar conectividad
ping your-proxmox-server.com

# Probar credenciales manualmente
curl -k https://your-proxmox-server.com:8006/api2/json/access/ticket
```

### Problemas de Autenticación SharePoint
```bash
# Verificar configuración Azure AD
python3 main.py --output sharepoint  # Mensaje detallado de error
```

## 📈 Casos de Uso

### 1. Inventario Mensual Automatizado
```bash
# Crear script cron para ejecutar mensualmente
0 1 1 * * /path/to/venv/bin/python3 /path/to/main.py --output sharepoint
```

### 2. Dashboard Ejecutivo
1. Ejecuta inventario: `python3 main.py --output sharepoint`
2. En SharePoint: Crea tabla dinámica con campos `cluster_name`, `status`, `memory_gb`
3. Siguientes ejecuciones actualizarán automáticamente el dashboard

### 3. Auditoría Multi-Entorno
```bash
# Inventario completo con múltiples formatos para diferentes audiencias
python3 main.py --output all
```

## 🔧 Dependencias

### Requeridas
- Python 3.8+
- requests
- python-dotenv

### Opcionales
- openpyxl (para Excel)
- msal (para SharePoint)

```bash
# Instalar todas
pip install requests python-dotenv openpyxl msal
```

## 📚 Documentación Adicional

- [SETUP.md](docs/SETUP.md) - Configuración detallada paso a paso
- [SHAREPOINT_GUIDE.md](docs/SHAREPOINT_GUIDE.md) - Guía completa SharePoint + Azure AD

---

## 📜 Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE), lo que permite su uso, copia, modificación y distribución con fines personales, académicos o comerciales.

> **Autoría**: Este software fue creado y es mantenido por [@SktCod.ByChisto](https://github.com/carrionmecapp).  
> Aunque es de código abierto, se agradece el reconocimiento correspondiente en derivados o menciones públicas.

---

## 👤 Autor

Desarrollado por [@SktCod.ByChisto](https://github.com/carrionmecapp)  
© 2025 – Todos los derechos reservados.
