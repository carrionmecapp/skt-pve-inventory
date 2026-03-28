"""
Módulo para gestionar múltiples clusters Proxmox
"""

import traceback
from .inventory_manager import ProxmoxInventory


class ProxmoxClusterManager:
    """Gestiona inventario de múltiples clusters Proxmox"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.hosts = config_manager.get_proxmox_hosts()
    
    def get_inventory_from_all_hosts(self):
        """Obtener inventario de todos los hosts configurados"""
        all_vms = []
        
        if not self.hosts:
            print("❌ No se encontraron hosts configurados")
            return all_vms
        
        for host_id, config in self.hosts.items():
            print(f"\n{'='*60}")
            print(f"Procesando: {config['name']} ({config['host']})")
            print(f"{'='*60}")
            
            try:
                inventory_manager = ProxmoxInventory(
                    host=config['host'],
                    username=config['username'],
                    password=config['password'],
                    verify_ssl=config['verify_ssl']
                )
                
                host_inventory = inventory_manager.get_full_inventory()
                
                # Agregar información del cluster a cada VM
                for vm in host_inventory:
                    vm['cluster_name'] = config['name']
                    vm['cluster_host'] = config['host']
                
                all_vms.extend(host_inventory)
                print(f"✓ Completado {config['name']}: {len(host_inventory)} VMs encontradas")
                
            except Exception as e:
                print(f"❌ Error procesando {config['name']}: {e}")
                traceback.print_exc()
                continue
        
        return all_vms
    
    def get_cluster_summary(self, inventory):
        """Obtener resumen por clusters"""
        if not inventory:
            return {}
        
        summary = {}
        
        for vm in inventory:
            cluster_name = vm.get('cluster_name', 'Unknown')
            
            if cluster_name not in summary:
                summary[cluster_name] = {
                    'total_vms': 0,
                    'running_vms': 0,
                    'stopped_vms': 0,
                    'total_memory_gb': 0,
                    'total_disk_gb': 0,
                    'total_cpu_cores': 0,
                    'cluster_type': vm.get('cluster_type', 'Unknown'),
                    'cluster_host': vm.get('cluster_host', 'Unknown')
                }
            
            # Contar VMs por estado
            summary[cluster_name]['total_vms'] += 1
            if vm.get('status') == 'running':
                summary[cluster_name]['running_vms'] += 1
            elif vm.get('status') == 'stopped':
                summary[cluster_name]['stopped_vms'] += 1
            
            # Sumar recursos
            summary[cluster_name]['total_memory_gb'] += vm.get('memory_gb', 0)
            summary[cluster_name]['total_disk_gb'] += vm.get('total_disk_gb', 0)
            summary[cluster_name]['total_cpu_cores'] += vm.get('cpu_cores', 0)
        
        return summary
    
    def print_summary(self, inventory):
        """Imprimir resumen del inventario"""
        if not inventory:
            print("❌ No hay VMs en el inventario")
            return
        
        summary = self.get_cluster_summary(inventory)
        
        print(f"\n{'='*60}")
        print("📊 RESUMEN DEL INVENTARIO")
        print(f"{'='*60}")
        
        total_vms = len(inventory)
        total_running = len([vm for vm in inventory if vm.get('status') == 'running'])
        total_stopped = len([vm for vm in inventory if vm.get('status') == 'stopped'])
        
        print(f"🖥️  Total de VMs: {total_vms}")
        print(f"🟢 VMs en ejecución: {total_running}")
        print(f"🔴 VMs detenidas: {total_stopped}")
        
        print(f"\n📋 Resumen por clusters:")
        for cluster_name, data in summary.items():
            print(f"\n  📍 {cluster_name} ({data['cluster_type']})")
            print(f"     Host: {data['cluster_host']}")
            print(f"     VMs: {data['total_vms']} (▶️ {data['running_vms']} | ⏹️ {data['stopped_vms']})")
            print(f"     CPU: {data['total_cpu_cores']} cores")
            print(f"     RAM: {data['total_memory_gb']:.1f} GB")
            print(f"     Disk: {data['total_disk_gb']:.1f} GB")
