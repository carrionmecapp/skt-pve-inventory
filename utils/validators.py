"""
Utilidades para validar datos y configuraciones
"""

import os
import re
import socket
from urllib.parse import urlparse


class ConfigValidator:
    """Validador de configuraciones"""
    
    @staticmethod
    def validate_host(host):
        """Validar que un host sea válido"""
        if not host:
            return False, "Host vacío"
        
        # Remover protocolo si existe
        clean_host = host.replace('https://', '').replace('http://', '')
        
        # Validar formato IP o hostname
        try:
            socket.gethostbyname(clean_host)
            return True, "Host válido"
        except socket.gaierror:
            return False, f"No se puede resolver el host: {clean_host}"
    
    @staticmethod
    def validate_port(port):
        """Validar puerto"""
        try:
            port_num = int(port)
            if 1 <= port_num <= 65535:
                return True, "Puerto válido"
            else:
                return False, "Puerto fuera del rango válido (1-65535)"
        except (ValueError, TypeError):
            return False, "Puerto debe ser un número"
    
    @staticmethod
    def validate_credentials(username, password):
        """Validar credenciales básicas"""
        if not username:
            return False, "Usuario requerido"
        if not password:
            return False, "Contraseña requerida"
        if len(password) < 3:
            return False, "Contraseña muy corta"
        return True, "Credenciales válidas"
    
    @staticmethod
    def validate_proxmox_config(config):
        """Validar configuración completa de Proxmox"""
        errors = []
        
        # Validar host
        is_valid, message = ConfigValidator.validate_host(config.get('host'))
        if not is_valid:
            errors.append(f"Host: {message}")
        
        # Validar credenciales
        is_valid, message = ConfigValidator.validate_credentials(
            config.get('username'), 
            config.get('password')
        )
        if not is_valid:
            errors.append(f"Credenciales: {message}")
        
        # Validar nombre
        if not config.get('name'):
            errors.append("Nombre del cluster requerido")
        
        return len(errors) == 0, errors


class SharePointValidator:
    """Validador específico para SharePoint"""
    
    @staticmethod
    def validate_url(url):
        """Validar URL de SharePoint"""
        if not url:
            return False, "URL requerida"
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "URL mal formateada"
            
            if 'sharepoint.com' not in parsed.netloc:
                return False, "No parece ser una URL de SharePoint"
            
            return True, "URL válida"
        except Exception as e:
            return False, f"Error validando URL: {e}"
    
    @staticmethod
    def validate_guid(guid):
        """Validar formato GUID"""
        if not guid:
            return False, "GUID requerido"
        
        guid_pattern = re.compile(
	    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if guid_pattern.match(guid):
            return True, "GUID válido"
        else:
            return False, "Formato de GUID inválido"
    
    @staticmethod
    def validate_sharepoint_config(config):
        """Validar configuración completa de SharePoint"""
        errors = []
        
        # Validar IDs requeridos
        tenant_id = config.get('tenant_id')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        sharepoint_url = config.get('sharepoint_url')
        
        if not tenant_id:
            errors.append("Tenant ID requerido")
        else:
            is_valid, message = SharePointValidator.validate_guid(tenant_id)
            if not is_valid:
                errors.append(f"Tenant ID: {message}")
        
        if not client_id:
            errors.append("Client ID requerido")
        else:
            is_valid, message = SharePointValidator.validate_guid(client_id)
            if not is_valid:
                errors.append(f"Client ID: {message}")
        
        if not client_secret:
            errors.append("Client Secret requerido")
        elif len(client_secret) < 10:
            errors.append("Client Secret muy corto")
        
        if not sharepoint_url:
            errors.append("SharePoint URL requerida")
        else:
            is_valid, message = SharePointValidator.validate_url(sharepoint_url)
            if not is_valid:
                errors.append(f"SharePoint URL: {message}")
        
        return len(errors) == 0, errors


class FileValidator:
    """Validador de archivos y rutas"""
    
    @staticmethod
    def validate_file_path(filepath):
        """Validar ruta de archivo"""
        if not filepath:
            return False, "Ruta de archivo requerida"
        
        # Verificar caracteres válidos
        invalid_chars = '<>:"|?*'
        if any(char in filepath for char in invalid_chars):
            return False, f"Ruta contiene caracteres inválidos: {invalid_chars}"
        
        # Verificar longitud
        if len(filepath) > 260:  # Límite Windows
            return False, "Ruta muy larga (máximo 260 caracteres)"
        
        return True, "Ruta válida"
    
    @staticmethod
    def validate_directory_writable(directory):
        """Validar que un directorio sea escribible"""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                return True, f"Directorio creado: {directory}"
            except Exception as e:
                return False, f"No se puede crear directorio: {e}"
        
        if not os.access(directory, os.W_OK):
            return False, f"Directorio no escribible: {directory}"
        
        return True, "Directorio escribible"
    
    @staticmethod
    def validate_filename(filename):
        """Validar nombre de archivo"""
        if not filename:
            return False, "Nombre de archivo requerido"
        
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        if any(char in filename for char in invalid_chars):
            return False, f"Nombre contiene caracteres inválidos: {invalid_chars}"
        
        # Nombres reservados en Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            return False, f"Nombre reservado del sistema: {filename}"
        
        return True, "Nombre de archivo válido"


class DataValidator:
    """Validador de datos de inventario"""
    
    @staticmethod
    def validate_vm_data(vm_data):
        """Validar datos básicos de una VM"""
        errors = []
        
        # VMID requerido
        if not vm_data.get('vmid'):
            errors.append("VMID requerido")
        
        # Nombre requerido
        if not vm_data.get('name'):
            errors.append("Nombre de VM requerido")
        
        # Valores numéricos
        numeric_fields = ['cpu_cores', 'cpu_sockets', 'memory_gb', 'disk_count']
        for field in numeric_fields:
            value = vm_data.get(field)
            if value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser numérico")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_inventory_data(inventory):
        """Validar datos completos del inventario"""
        if not inventory:
            return False, ["Inventario vacío"]
        
        if not isinstance(inventory, list):
            return False, ["Inventario debe ser una lista"]
        
        errors = []
        for i, vm in enumerate(inventory):
            is_valid, vm_errors = DataValidator.validate_vm_data(vm)
            if not is_valid:
                errors.extend([f"VM {i+1}: {error}" for error in vm_errors])
        
        return len(errors) == 0, errors


class SystemValidator:
    """Validador de requisitos del sistema"""
    
    @staticmethod
    def check_python_version():
        """Verificar versión de Python"""
        import sys
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            return False, f"Python 3.6+ requerido. Versión actual: {version.major}.{version.minor}"
        
        return True, f"Python {version.major}.{version.minor} - Compatible"
    
    @staticmethod
    def check_dependencies():
        """Verificar dependencias opcionales"""
        dependencies = {
            'requests': 'Requerido para API calls',
            'dotenv': 'Requerido para archivos .env',
            'openpyxl': 'Opcional para Excel',
            'msal': 'Opcional para SharePoint'
        }
        
        results = {}
        for module, description in dependencies.items():
            try:
                __import__(module.replace('-', '_'))
                results[module] = {'installed': True, 'description': description}
            except ImportError:
                results[module] = {'installed': False, 'description': description}
        
        return results
    
    @staticmethod
    def check_disk_space(directory, required_mb=100):
        """Verificar espacio en disco disponible"""
        try:
            statvfs = os.statvfs(directory)
            available_mb = (statvfs.f_bavail * statvfs.f_frsize) / (1024 * 1024)
            
            if available_mb >= required_mb:
                return True, f"Espacio disponible: {available_mb:.1f} MB"
            else:
                return False, f"Espacio insuficiente. Disponible: {available_mb:.1f} MB, Requerido: {required_mb} MB"
        
        except (OSError, AttributeError):
            # Windows no tiene statvfs
            import shutil
            try:
                total, used, free = shutil.disk_usage(directory)
                free_mb = free / (1024 * 1024)
                
                if free_mb >= required_mb:
                    return True, f"Espacio disponible: {free_mb:.1f} MB"
                else:
                    return False, f"Espacio insuficiente. Disponible: {free_mb:.1f} MB, Requerido: {required_mb} MB"
            except Exception as e:
                return False, f"No se puede verificar espacio en disco: {e}"
