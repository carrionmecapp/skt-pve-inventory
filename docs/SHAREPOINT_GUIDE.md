# 📊 Guía Completa SharePoint + Azure AD

Esta guía te llevará paso a paso para configurar la integración completa con SharePoint, incluyendo registro de aplicación en Azure AD, permisos, y configuración del Excel inteligente.

## 🎯 ¿Por qué SharePoint?

### Ventajas de la Integración
- ✅ **Centralización**: Inventario accesible desde cualquier lugar
- ✅ **Colaboración**: Múltiples usuarios pueden ver los datos
- ✅ **Automatización**: Actualización automática sin intervención manual
- ✅ **Excel Inteligente**: Preserva tablas dinámicas, gráficos y formato
- ✅ **Historial**: Versiones automáticas de archivos
- ✅ **Seguridad**: Control de acceso granular

### Casos de Uso
- **Dashboard Ejecutivo**: Tablas dinámicas con métricas de infraestructura
- **Reportes Mensuales**: Archivo que se actualiza automáticamente
- **Inventario en Tiempo Real**: Datos frescos para el equipo IT
- **Auditorías**: Histórico de cambios y estados de VMs

## 🔧 Configuración Azure AD

### Paso 1: Acceder a Azure Portal

1. Ve a [portal.azure.com](https://portal.azure.com)
2. Inicia sesión con cuenta administrativa
3. Busca "Azure Active Directory" o "Entra ID"

### Paso 2: Registrar Nueva Aplicación

1. **Azure Active Directory** → **App registrations** → **New registration**

2. **Configuración básica**:
   ```
   Name: Proxmox Inventory Tool
   Supported account types: Accounts in this organizational directory only
   Redirect URI: (leave blank for now)
   ```

3. **Hacer clic en "Register"**

### Paso 3: Obtener IDs Necesarios

Después del registro, obtendrás:

1. **Application (client) ID**: 
   - Copia este valor → será tu `SHAREPOINT_CLIENT_ID`

2. **Directory (tenant) ID**:
   - Copia este valor → será tu `SHAREPOINT_TENANT_ID`

### Paso 4: Crear Client Secret

1. En tu aplicación: **Certificates & secrets** → **Client secrets** → **New client secret**

2. **Configuración**:
   ```
   Description: Proxmox Inventory Secret
   Expires: 24 months (recommended)
   ```

3. **¡IMPORTANTE!** Copia el **Value** inmediatamente → será tu `SHAREPOINT_CLIENT_SECRET`
   
   ⚠️ **Este valor solo se muestra una vez. Si lo pierdes, tendrás que crear uno nuevo.**

### Paso 5: Configurar Permisos API

1. **API permissions** → **Add a permission**

2. **Microsoft Graph** → **Application permissions**

3. **Agregar estos permisos**:
   ```
   Sites.ReadWrite.All      (Para leer/escribir sitios SharePoint)
   Files.ReadWrite.All      (Para leer/escribir archivos)
   Sites.Manage.All         (Para gestión completa de sitios)
   ```

4. **¡CRUCIAL!** Hacer clic en **"Grant admin consent for [Your Organization]"**
   
   ✅ Debe aparecer un checkmark verde en cada permiso

### Paso 6: Configurar Autenticación

1. **Authentication** → **Platform configurations** → **Add a platform**

2. **Web**:
   ```
   Redirect URIs: http://localhost (opcional para esta aplicación)
   ```

3. **Advanced settings**:
   ```
   ✅ Allow public client flows: Yes
   ```

## 🏢 Configuración SharePoint

### Paso 1: Identificar tu Sitio SharePoint

#### Opción A: Sitio Específico
Si tienes un sitio como `https://tuempresa.sharepoint.com/sites/IT-Operations`:
```env
SHAREPOINT_URL=https://tuempresa.sharepoint.com
SHAREPOINT_SITE_NAME=IT-Operations
```

#### Opción B: Sitio Raíz
Si usas el sitio principal `https://tuempresa.sharepoint.com`:
```env
SHAREPOINT_URL=https://tuempresa.sharepoint.com
SHAREPOINT_SITE_NAME=
```

### Paso 2: Configurar Biblioteca de Documentos

#### Biblioteca por Defecto (Documents):
```env
SHAREPOINT_LIBRARY_NAME=Documents
```

#### Biblioteca Personalizada:
```env
SHAREPOINT_LIBRARY_NAME=IT-Infrastructure
```

### Paso 3: Estructura de Carpetas

El script organiza automáticamente en:
```
📁 [Biblioteca]/
  📁 Inventory/
    📁 [Tu Carpeta]/
      📄 [Tu Archivo].xlsx
```

Ejemplos de rutas finales:
- `Documents/Inventory/Proxmox-VMs/inventario_vms.xlsx`
- `IT-Infrastructure/Inventory/Servers/monthly_report.xlsx`
- `Shared Documents/Inventory/Production/vm_inventory.xlsx`

## ⚙️ Configuración del .env

### Archivo Completo de Ejemplo

```env
# ==========================================
# CONFIGURACIÓN SHAREPOINT COMPLETA
# ==========================================

# Azure AD Application IDs
SHAREPOINT_TENANT_ID=12345678-1234-1234-1234-123456789012
SHAREPOINT_CLIENT_ID=87654321-4321-4321-4321-210987654321
SHAREPOINT_CLIENT_SECRET=tu_secreto_de_aplicacion_azure

# SharePoint Site Configuration  
SHAREPOINT_URL=https://tuempresa.sharepoint.com
SHAREPOINT_SITE_NAME=IT-Operations

# File Organization (Optional - defaults provided)
SHAREPOINT_LIBRARY_NAME=Documents
SHAREPOINT_DEFAULT_FOLDER=Proxmox-VMs
SHAREPOINT_DEFAULT_FILENAME=inventario_proxmox_vms.xlsx
```

### Configuraciones Alternativas

#### Para Múltiples Departamentos:
```env
# IT Operations
SHAREPOINT_SITE_NAME=IT-Operations
SHAREPOINT_DEFAULT_FOLDER=Infrastructure
SHAREPOINT_DEFAULT_FILENAME=proxmox_inventory.xlsx

# O ejecutar con parámetros:
# python3 main.py --output sharepoint --sharepoint-folder "Servers" --sharepoint-filename "monthly_vms.xlsx"
```

#### Para Reportes Ejecutivos:
```env
SHAREPOINT_SITE_NAME=Executive-Reports
SHAREPOINT_DEFAULT_FOLDER=IT-Metrics
SHAREPOINT_DEFAULT_FILENAME=vm_dashboard.xlsx
```

## 🧪 Verificación y Testing

### 1. Test de Conexión Azure AD

```bash
# Verificar que las credenciales son correctas
python3 main.py --output sharepoint
```

**Mensajes de éxito esperados**:
```
✓ Autenticación exitosa con SharePoint
✓ Carpeta 'Inventory' creada
📤 Actualizando archivo: Inventory/Proxmox-VMs/inventario_proxmox_vms.xlsx
✅ Archivo actualizado exitosamente en SharePoint!
```

### 2. Test Manual con PowerShell (Opcional)

```powershell
# Instalar módulo
Install-Module -Name Microsoft.Graph -Force

# Conectar con tus credenciales
Connect-MgGraph -TenantId "tu-tenant-id" -ClientId "tu-client-id"

# Listar sitios
Get-MgSite -All

# Verificar permisos
Get-MgContext
```

### 3. Verificación Web

1. Ve a SharePoint en tu navegador
2. Navega a la biblioteca configurada
3. Busca la carpeta `Inventory/[tu-carpeta]/`
4. Verifica que el archivo Excel se haya creado

## 📊 Excel Inteligente: Configuración Avanzada

### Funcionalidad Excel Inteligente

El script implementa "Excel Inteligente" que:
- ✅ Descarga el archivo existente de SharePoint
- ✅ Mantiene headers, formato y estructura
- ✅ **Preserva tablas dinámicas y gráficos**
- ✅ Solo limpia y actualiza los datos (fila 2 hacia abajo)
- ✅ Sube el archivo actualizado manteniendo todo tu trabajo

### Configuración de Dashboard Profesional

#### Paso 1: Primera Ejecución
```bash
# Crear archivo base en SharePoint
python3 main.py --output sharepoint
```

#### Paso 2: Configurar Tabla Dinámica en SharePoint

1. **Abrir archivo en SharePoint**:
   - Ve a tu sitio SharePoint
   - Navega a `Inventory/[tu-carpeta]/[tu-archivo].xlsx`
   - Hacer clic para abrir en Excel Online

2. **Crear tabla de datos**:
   - Seleccionar todos los datos (Ctrl+A en la hoja "VM Inventory")
   - **Insertar** → **Tabla** → Confirmar rango → OK
   - Nombre sugerido: `TablaVMs`

3. **Crear tabla dinámica**:
   - Seleccionar cualquier celda de la tabla
   - **Insertar** → **Tabla dinámica** → **Nueva hoja de cálculo**

#### Paso 3: Configurar Campos de Tabla Dinámica

**Dashboard de Estado de VMs**:
```
🔹 Filas: cluster_name, node
🔹 Columnas: status  
🔹 Valores: Recuento de vmid
🔹 Filtros: fecha_actualizacion
```

**Dashboard de Recursos**:
```
🔹 Filas: cluster_name
🔹 Valores: 
  - Suma de memory_gb
  - Suma de total_disk_gb
  - Recuento de vmid
```

**Dashboard por Sistema Operativo**:
```
🔹 Filas: os_type
🔹 Columnas: status
🔹 Valores: Recuento de vmid
```

#### Paso 4: Agregar Gráficos

1. **Seleccionar tabla dinámica**
2. **Insertar** → **Gráfico recomendado**
3. **Tipos sugeridos**:
   - **Gráfico de barras**: VMs por cluster
   - **Gráfico circular**: Distribución por estado
   - **Gráfico de columnas**: Recursos por nodo

#### Paso 5: Formatear Dashboard

1. **Renombrar hojas**:
   - `VM Inventory` → Datos
   - `Hoja2` → Dashboard Estado
   - `Hoja3` → Dashboard Recursos

2. **Agregar títulos y formato**:
   ```
   📊 INVENTARIO PROXMOX - DASHBOARD EJECUTIVO
   🕒 Última actualización: [Se actualiza automáticamente]
   ```

3. **Configurar colores corporativos**

### Dashboard Ejemplos Profesionales

#### Dashboard IT Manager
```
📊 Resumen Ejecutivo de Infraestructura Proxmox

┌─ VMs por Estado ─────────────────────┐
│ ⚪ Running:  85 VMs (78%)           │
│ 🔴 Stopped:  24 VMs (22%)           │
│ 📊 Total:    109 VMs                │
└─────────────────────────────────────┘

┌─ Recursos por Cluster ──────────────┐
│ 🏢 Production:  1,024 GB RAM        │
│ 🧪 Development: 512 GB RAM          │
│ 🔧 Testing:     256 GB RAM          │
└─────────────────────────────────────┘

┌─ Distribución por OS ───────────────┐
│ 🐧 Linux:     67 VMs (61%)          │
│ 🪟 Windows:   42 VMs (39%)          │
└─────────────────────────────────────┘
```

#### Dashboard Técnico
```
🔧 Vista Técnica Detallada

┌─ Nodos por Cluster ─────────────────┐
│ Production → pve-01, pve-02, pve-03 │
│ Development → pve-dev-01            │
│ Testing → pve-test-01               │
└─────────────────────────────────────┘

┌─ IPs Detectadas ────────────────────┐
│ ✅ Con IP: 78 VMs (72%)             │
│ ❌ Sin IP: 31 VMs (28%)             │
│ 💡 Instalar QEMU Agent              │
└─────────────────────────────────────┘

┌─ Almacenamiento Total ──────────────┐
│ 📁 Total Discos: 15.7 TB           │
│ 📊 Promedio VM: 150 GB              │
└─────────────────────────────────────┘
```

## 🔄 Automatización Completa

### Script PowerShell para Windows

Crear `Update-ProxmoxInventory.ps1`:
```powershell
# Proxmox Inventory Automation Script
param(
    [string]$LogPath = "C:\Logs\ProxmoxInventory",
    [string]$ProjectPath = "C:\Scripts\proxmox-inventory"
)

# Crear directorio de logs si no existe
if (!(Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force
}

$LogFile = Join-Path $LogPath "inventory-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$ErrorCount = 0

try {
    Write-Output "$(Get-Date): Iniciando inventario Proxmox" | Tee-Object -FilePath $LogFile -Append
    
    # Cambiar al directorio del proyecto
    Set-Location $ProjectPath
    
    # Activar entorno virtual
    & ".\venv\Scripts\Activate.ps1"
    
    # Ejecutar inventario
    $result = & python main.py --output sharepoint 2>&1
    $result | Tee-Object -FilePath $LogFile -Append
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output "$(Get-Date): ✅ Inventario completado exitosamente" | Tee-Object -FilePath $LogFile -Append
        
        # Opcional: Enviar notificación Teams/Slack
        # Invoke-RestMethod -Uri $TeamsWebhookUrl -Method Post -Body $TeamsMessage
    }
    else {
        $ErrorCount++
        Write-Output "$(Get-Date): ❌ Error en inventario" | Tee-Object -FilePath $LogFile -Append
    }
}
catch {
    $ErrorCount++
    Write-Output "$(Get-Date): ❌ Excepción: $($_.Exception.Message)" | Tee-Object -FilePath $LogFile -Append
}

# Deactivate virtual environment
deactivate

# Enviar email si hay errores
if ($ErrorCount -gt 0) {
    $EmailParams = @{
        To = "admin@company.com"
        From = "proxmox-inventory@company.com"
        Subject = "⚠️ Error en Inventario Proxmox"
        Body = "Se produjo un error en la ejecución del inventario. Ver log: $LogFile"
        SmtpServer = "smtp.company.com"
    }
    Send-MailMessage @EmailParams
}

# Limpiar logs antiguos (más de 30 días)
Get-ChildItem $LogPath -Filter "inventory-*.log" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```

### Programación en Task Scheduler (Windows)

1. **Abrir Task Scheduler**
2. **Create Basic Task**:
   ```
   Name: Proxmox Inventory Update
   Description: Actualización automática del inventario de VMs
   Trigger: Daily at 6:00 AM
   Action: Start a program
   Program: PowerShell.exe
   Arguments: -ExecutionPolicy Bypass -File "C:\Scripts\Update-ProxmoxInventory.ps1"
   ```

### Programación en Cron (Linux)

Crear `/etc/cron.d/proxmox-inventory`:
```bash
# Inventario Proxmox - Ejecución diaria
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Todos los días a las 6:00 AM
0 6 * * * proxmox-user /opt/proxmox-inventory/run_inventory.sh

# Primer lunes de cada mes - Reporte mensual detallado
0 8 * * 1 proxmox-user [ $(date +\%d) -le 7 ] && /opt/proxmox-inventory/monthly_report.sh
```

## 🚨 Solución de Problemas Avanzados

### Error: "Insufficient privileges to complete the operation"

**Causa**: Permisos insuficientes en Azure AD

**Solución**:
1. **Azure Portal** → **App registrations** → **Tu app**
2. **API permissions** → Verificar que tengas:
   ```
   Sites.ReadWrite.All ✅ Granted
   Files.ReadWrite.All ✅ Granted
   Sites.Manage.All    ✅ Granted
   ```
3. **Grant admin consent** si hay alguno sin checkmark verde

### Error: "Site not found" o 404

**Causa**: URL de sitio SharePoint incorrecta

**Solución**:
1. **Verificar URL manualmente**:
   - Ve a tu sitio SharePoint en el navegador
   - Copia la URL exacta
   - Formato correcto: `https://tuempresa.sharepoint.com/sites/IT-Operations`

2. **Actualizar .env**:
   ```env
   SHAREPOINT_URL=https://tuempresa.sharepoint.com
   SHAREPOINT_SITE_NAME=IT-Operations  # Solo el nombre después de /sites/
   ```

### Error: "The resource you are attempting to access is locked" (423)

**Causa**: Archivo abierto en Excel Online o Desktop

**Soluciones**:
1. **Cerrar archivo** en todas las instancias de Excel
2. **Esperar 5 minutos** para que SharePoint libere el bloqueo
3. **Usar nombre de archivo diferente temporalmente**:
   ```bash
   python3 main.py --output sharepoint --sharepoint-filename "inventory_backup.xlsx"
   ```

### Error: "Token expired" o "Authentication failed"

**Causa**: Token Azure AD expirado o credenciales incorrectas

**Solución**:
1. **Regenerar Client Secret**:
   - Azure Portal → App registrations → Tu app → Certificates & secrets
   - Delete old secret → New client secret
   - Actualizar `SHAREPOINT_CLIENT_SECRET` en .env

2. **Verificar IDs**:
   ```bash
   # Test manual de autenticación
   curl -X POST https://login.microsoftonline.com/[TENANT_ID]/oauth2/v2.0/token \
   -H "Content-Type: application/x-www-form-urlencoded" \
   -d "client_id=[CLIENT_ID]&client_secret=[CLIENT_SECRET]&scope=https://graph.microsoft.com/.default&grant_type=client_credentials"
   ```

### Performance: Archivo Excel muy lento

**Causa**: Muchas VMs (500+) con formato complejo

**Optimizaciones**:
1. **Deshabilitar formato en archivos grandes**:
   ```python
   # En sharepoint_uploader.py, línea ~200
   if len(inventory) > 500:
       # Saltar colores y formato fancy
       pass
   ```

2. **Separar por clusters**:
   ```bash
   # Usar carpetas separadas por cluster
   python3 main.py --output sharepoint --sharepoint-folder "Production" --env-file .env.prod
   python3 main.py --output sharepoint --sharepoint-folder "Development" --env-file .env.dev
   ```

## 📈 Métricas y Monitoring

### Dashboard de Monitoreo

Agregar hoja "Métricas" al Excel con:

```
📊 Estadísticas del Inventario

Última Actualización: =MAX(Datos[Fecha Actualizacion])
Total VMs: =COUNTA(Datos[Vmid])
VMs Running: =COUNTIF(Datos[Status],"running")
VMs Stopped: =COUNTIF(Datos[Status],"stopped")
% Disponibilidad: =Datos[@[VMs Running]]/Datos[@[Total VMs]]

Memoria Total (GB): =SUM(Datos[Memory Gb])
Almacenamiento Total (TB): =SUM(Datos[Total Disk Gb])/1024
VMs con QEMU Agent: =COUNTIF(Datos[Agent Enabled],"Sí")
% Agentes Instalados: =Datos[@[VMs con QEMU Agent]]/Datos[@[Total VMs]]

Clusters Monitoreados: =COUNTA(UNIQUE(Datos[Cluster Name]))
Nodos Totales: =COUNTA(UNIQUE(Datos[Node]))
```

### Alertas y Notificaciones

Integrar con Teams/Slack agregando al script:

```python
# En main.py, después del inventario exitoso
def send_teams_notification(inventory_stats):
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
    if webhook_url:
        message = {
            "text": f"✅ Inventario Proxmox actualizado: {len(inventory_stats)} VMs procesadas"
        }
        requests.post(webhook_url, json=message)
```

---

## 🎓 Próximos Pasos

Una vez configurado SharePoint:

1. **Configurar dashboards** siguiendo los ejemplos de arriba
2. **Automatizar ejecución** con scripts y programación
3. **Compartir con el equipo** configurando permisos SharePoint
4. **Monitorear y optimizar** según el uso real

¿Problemas específicos? Consulta [Issues en GitHub](https://github.com/tu-usuario/proxmox-inventory/issues) o la [documentación principal](README.md).
