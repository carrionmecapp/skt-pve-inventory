"""
Utilidades para formatear y transformar datos
"""

import re
from datetime import datetime


class DataFormatter:
    """Utilidades para formatear datos del inventario"""
    
    @staticmethod
    def format_memory_gb(memory_mb):
        """Convertir memoria de MB a GB con formato seguro"""
        try:
            memory_mb = int(memory_mb) if memory_mb else 0
            return round(memory_mb / 1024, 2) if memory_mb else 0
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def format_disk_size(size_str):
        """Convertir tamaño de disco a GB (base 1024)"""
        try:
            size_str = str(size_str).upper().strip()
            
            # Remover caracteres no numéricos al final para obtener la unidad
            match = re.match(r'(\d+(?:\.\d+)?)\s*([KMGT]?)', size_str)
            
            if not match:
                return 0
            
            number = float(match.group(1))
            unit = match.group(2) if match.group(2) else ''
            
            # Conversión a GB usando base 1024
            if unit == 'T':
                return number * 1024  # TB a GB
            elif unit == 'G' or unit == '':
                return number  # Ya está en GB o sin unidad (asumir GB)
            elif unit == 'M':
                return number / 1024  # MB a GB
            elif unit == 'K':
                return number / (1024 * 1024)  # KB a GB
            else:
                return number  # Por defecto asumir GB
                
        except:
            return 0
    
    @staticmethod
    def format_boolean_field(value):
        """Convertir valores booleanos a Sí/No"""
        if isinstance(value, bool):
            return 'Sí' if value else 'No'
        elif isinstance(value, str):
            return 'Sí' if value.lower() in ['true', '1', 'yes', 'sí'] else 'No'
        elif value:
            return 'Sí'
        else:
            return 'No'
    
    @staticmethod
    def format_ip_list(ips):
        """Formatear lista de IPs"""
        if not ips:
            return 'No disponible'
        if isinstance(ips, list):
            return ', '.join(ips)
        return str(ips)
    
    @staticmethod
    def format_timestamp():
        """Generar timestamp actual formateado"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def clean_string_field(value):
        """Limpiar campos de texto"""
        if not value:
            return ''
        return str(value).strip()
    
    @staticmethod
    def format_numeric_field(value, default=0):
        """Formatear campos numéricos con valor por defecto"""
        try:
            return int(value) if str(value).isdigit() else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def format_float_field(value, decimals=2, default=0.0):
        """Formatear campos flotantes con decimales específicos"""
        try:
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return default


class VMDataFormatter:
    """Formateador específico para datos de VMs"""
    
    def __init__(self):
        self.formatter = DataFormatter()
    
    def format_vm_data(self, vm_config, vm_status, vm_ips=None):
        """Formatear datos completos de una VM"""
        formatted_data = {
            # Información básica
            'vmid': vm_config.get('vmid', 0),
            'name': self.formatter.clean_string_field(vm_config.get('name', f"VM-{vm_config.get('vmid', 0)}")),
            'status': self.formatter.clean_string_field(vm_status.get('status', 'unknown')),
            
            # CPU y Memoria
            'cpu_cores': self.formatter.format_numeric_field(vm_config.get('cores', 1)),
            'cpu_sockets': self.formatter.format_numeric_field(vm_config.get('sockets', 1)),
            'memory_gb': self.formatter.format_memory_gb(vm_config.get('memory', 0)),
            
            # Red
            'network_interfaces': len([k for k in vm_config.keys() if k.startswith('net')]),
            'ips': self.formatter.format_ip_list(vm_ips),
            'ip_count': len(vm_ips) if vm_ips else 0,
            
            # Sistema
            'os_type': self.formatter.clean_string_field(vm_config.get('ostype', 'No especificado')),
            'agent_enabled': self.formatter.format_boolean_field(vm_config.get('agent')),
            'template': self.formatter.format_boolean_field(vm_config.get('template')),
            'protection': self.formatter.format_boolean_field(vm_config.get('protection')),
            
            # Metadatos
            'tags': self.formatter.clean_string_field(vm_config.get('tags', '')),
            'description': self.formatter.clean_string_field(vm_config.get('description', '')),
            
            # Timestamp
            'fecha_actualizacion': self.formatter.format_timestamp()
        }
        
        return formatted_data
    
    def add_cluster_info(self, vm_data, cluster_name, cluster_host, cluster_type, node_name):
        """Agregar información del cluster a los datos de la VM"""
        vm_data.update({
            'cluster_name': cluster_name,
            'cluster_host': cluster_host,
            'cluster_type': cluster_type,
            'node': node_name
        })
        return vm_data


class ReportFormatter:
    """Formateador para reportes y resúmenes"""
    
    @staticmethod
    def format_bytes(bytes_value):
        """Formatear bytes a unidades legibles"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    @staticmethod
    def format_percentage(value, total):
        """Calcular y formatear porcentaje"""
        if total == 0:
            return "0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    
    @staticmethod
    def format_uptime_summary(inventory):
        """Generar resumen de estado de VMs"""
        if not inventory:
            return {}
        
        total = len(inventory)
        running = len([vm for vm in inventory if vm.get('status') == 'running'])
        stopped = len([vm for vm in inventory if vm.get('status') == 'stopped'])
        other = total - running - stopped
        
        return {
            'total_vms': total,
            'running': running,
            'stopped': stopped,
            'other_status': other,
            'running_percentage': ReportFormatter.format_percentage(running, total),
            'stopped_percentage': ReportFormatter.format_percentage(stopped, total)
        }
