"""
Módulo para manejar la configuración de la aplicación
"""

import os
from dotenv import load_dotenv


class ConfigManager:
    """Gestiona la configuración de la aplicación"""
    
    def __init__(self, env_file='.env'):
        self.env_file = env_file
        self.hosts = {}
        self.sharepoint_config = {}
        self._load_config()
    
    def _load_config(self):
        """Cargar configuración desde archivo .env"""
        if not os.path.exists(self.env_file):
            print(f"❌ Archivo {self.env_file} no encontrado")
            return
            
        load_dotenv(self.env_file)
        self._load_proxmox_hosts()
        self._load_sharepoint_config()
    
    def _load_proxmox_hosts(self):
        """Cargar configuraciones de hosts Proxmox"""
        # Buscar todas las configuraciones PROXMOX_HOST
        host_counter = 1
        while True:
            host_key = f'PROXMOX_HOST{host_counter}'
            host = os.getenv(host_key)
            
            if not host:
                break
            
            user = os.getenv(f'PROXMOX_USER{host_counter}')
            password = os.getenv(f'PROXMOX_PASS{host_counter}')
            ssl = os.getenv(f'PROXMOX_SSL{host_counter}', 'true').lower() == 'true'
            name = os.getenv(f'PROXMOX_NAME{host_counter}', f'Proxmox-{host_counter}')
            
            if user and password:
                self.hosts[host_counter] = {
                    'host': host,
                    'username': user,
                    'password': password,
                    'verify_ssl': ssl,
                    'name': name
                }
                print(f"✓ Configuración cargada para {name} ({host})")
            
            host_counter += 1
        
        if not self.hosts:
            print("❌ No se encontraron configuraciones válidas de Proxmox")
    
    def _load_sharepoint_config(self):
        """Cargar configuración SharePoint"""
        self.sharepoint_config = {
            'tenant_id': os.getenv('SHAREPOINT_TENANT_ID'),
            'client_id': os.getenv('SHAREPOINT_CLIENT_ID'),
            'client_secret': os.getenv('SHAREPOINT_CLIENT_SECRET'),
            'sharepoint_url': os.getenv('SHAREPOINT_URL'),
            'site_name': os.getenv('SHAREPOINT_SITE_NAME'),
            'library_name': os.getenv('SHAREPOINT_LIBRARY_NAME', 'Documents'),
            'default_folder': os.getenv('SHAREPOINT_DEFAULT_FOLDER', 'Proxmox-VMs'),
            'default_filename': os.getenv('SHAREPOINT_DEFAULT_FILENAME', 'inventario_proxmox_vms.xlsx')
        }
    
    def get_proxmox_hosts(self):
        """Obtener configuraciones de hosts Proxmox"""
        return self.hosts
    
    def get_sharepoint_config(self):
        """Obtener configuración SharePoint"""
        return self.sharepoint_config
    
    def has_sharepoint_config(self):
        """Verificar si existe configuración SharePoint"""
        return bool(self.sharepoint_config.get('tenant_id') and 
                   self.sharepoint_config.get('client_id'))


def create_example_env_file():
    """Crear archivo .env de ejemplo con configuración completa"""
    env_content = """# ==========================================
# CONFIGURACIÓN DE PROXMOX - MÚLTIPLES ENTORNOS
# ==========================================

# Servidor 1 - SKTCOD
PROXMOX_HOST1=ns57.ip-51.net
PROXMOX_USER1=root@pam
PROXMOX_PASS1=password_111
PROXMOX_SSL1=false
PROXMOX_NAME1=SKTCOD

# Servidor 2 - QUBOS
PROXMOX_HOST2=ns58.ip-51.net
PROXMOX_USER2=root@pam
PROXMOX_PASS2=password_222
PROXMOX_SSL2=false
PROXMOX_NAME2=QUBOS

# ==========================================
# CONFIGURACIÓN SHAREPOINT COMPLETA
# ==========================================

# IDs de Azure AD (obtenidos del proceso de registro de aplicación)
SHAREPOINT_TENANT_ID=123456dsdsd789012-1234-1234-123456dsdsd789012-123456dsdsd789012
SHAREPOINT_CLIENT_ID=123456dsdsd789012-4321-4321-123456dsdsd789012-123456dsdsd789012
SHAREPOINT_CLIENT_SECRET=tu_secreto_muy_seguro_aqui

# URLs y configuración del sitio SharePoint
SHAREPOINT_URL=https://TUNOMBRE.sharepoint.com
SHAREPOINT_SITE_NAME=GTI-OP-Proyectos

# Configuración de biblioteca y archivos (OPCIONAL - tienen valores por defecto)
SHAREPOINT_LIBRARY_NAME=Documents
SHAREPOINT_DEFAULT_FOLDER=Proxmox-VMs
SHAREPOINT_DEFAULT_FILENAME=inventario_proxmox_sktcod.xlsx

# ==========================================
# ESTRUCTURA DE CARPETAS AUTOMÁTICA:
# ==========================================
# Todos los archivos se organizan automáticamente en:
# /Inventory/[tu-carpeta]/archivo.xlsx
# 
# Ejemplos de rutas finales:
# /Inventory/Proxmox-VMs/inventario_proxmox_sktcod.xlsx
# /Inventory/Servidores-Produccion/inventario_mensual.xlsx
# /Inventory/IT-Infrastructure/vms_consolidado.xlsx

# ==========================================
# EXPLICACIÓN DE VARIABLES:
# ==========================================
# SHAREPOINT_URL: URL base de tu SharePoint (sin /sites/...)
# SHAREPOINT_SITE_NAME: Nombre del sitio específico (lo que va después de /sites/)
# SHAREPOINT_LIBRARY_NAME: Biblioteca de documentos (por defecto: Documents)
# SHAREPOINT_DEFAULT_FOLDER: Carpeta dentro de la biblioteca donde guardar
# SHAREPOINT_DEFAULT_FILENAME: Nombre del archivo Excel que se sobrescribe

# ==========================================
# EJEMPLOS DE CONFIGURACIÓN:
# ==========================================
# 
# Para sitio raíz:
# SHAREPOINT_URL=https://TUNOMBRE.sharepoint.com
# SHAREPOINT_SITE_NAME=
# 
# Para sitio específico como GTI-OP-Proyectos:
# SHAREPOINT_URL=https://TUNOMBRE.sharepoint.com  
# SHAREPOINT_SITE_NAME=GTI-OP-Proyectos
#
# El archivo final se guardará en:
# https://TUNOMBRE.sharepoint.com/sites/pROYECTO/Shared Documents/Inventory/Proxmox-VMs/inventario_proxmox_sktcod.xlsx
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✓ Archivo .env.example creado con configuración completa")
    print("💡 Incluye configuración Proxmox + SharePoint")
    print("💡 Ahora copia: cp .env.example .env")
    print("💡 Y edita .env con tus credenciales reales")


def create_sharepoint_env_example():
    """Agregar configuración SharePoint a archivo .env.example existente"""
    sharepoint_config = """
# ==========================================
# CONFIGURACIÓN SHAREPOINT ADICIONAL
# ==========================================

# IDs de Azure AD (obtenidos del proceso de registro de aplicación)
SHAREPOINT_TENANT_ID=12345678-1234-1234-1234-123456789012
SHAREPOINT_CLIENT_ID=87654321-4321-4321-4321-210987654321
SHAREPOINT_CLIENT_SECRET=tu_secreto_muy_seguro_aqui

# URLs y configuración del sitio SharePoint
SHAREPOINT_URL=https://sktcod.sharepoint.com
SHAREPOINT_SITE_NAME=GTI-OP-Proyectos

# Configuración de biblioteca y archivos (OPCIONAL)
SHAREPOINT_LIBRARY_NAME=Documents
SHAREPOINT_DEFAULT_FOLDER=Proxmox-VMs
SHAREPOINT_DEFAULT_FILENAME=inventario_proxmox_sktcod.xlsx

# Nota: El archivo se guardará automáticamente en /Inventory/[folder]/[filename]
"""
    
    if os.path.exists('.env.example'):
        # Verificar si ya tiene configuración SharePoint
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'SHAREPOINT_TENANT_ID' in content:
            print("⚠️ El archivo .env.example ya contiene configuración SharePoint")
            return
        
        # Agregar SharePoint al archivo existente
        with open('.env.example', 'a', encoding='utf-8') as f:
            f.write(sharepoint_config)
        print("✓ Configuración SharePoint agregada a .env.example existente")
    else:
        print("❌ Archivo .env.example no existe")
        print("💡 Usa --create-example primero para crear la configuración base")
    
    print("💡 Edita .env.example y luego cópialo a .env")
