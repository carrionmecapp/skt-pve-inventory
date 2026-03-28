"""
Módulo para manejar el inventario de VMs de Proxmox
"""

import re
from datetime import datetime
from .proxmox_api import ProxmoxAPI


class ProxmoxInventory:
    """Clase para obtener inventario de VMs de Proxmox"""
    
    def __init__(self, host, username, password, verify_ssl=True):
        self.api = ProxmoxAPI(host, username, password, verify_ssl)
        self.host = host
        
    def get_cluster_info(self):
        """Obtener información del cluster"""
        cluster_data = self.api.get("/cluster/status")
        
        if not cluster_data or 'data' not in cluster_data:
            return {'type': 'Servidor standalone', 'name': self.host}
        
        cluster_nodes = [item for item in cluster_data['data'] if item['type'] == 'node']
        
        if len(cluster_nodes) > 1:
            return {'type': f'Cluster con {len(cluster_nodes)} nodos', 'name': 'cluster'}
        else:
            return {'type': 'Servidor standalone', 'name': self.host}
    
    def get_nodes(self):
        """Obtener lista de nodos"""
        nodes_data = self.api.get("/nodes")
        if nodes_data and 'data' in nodes_data:
            return nodes_data['data']
        return []
    
    def get_vms_from_node(self, node):
        """Obtener VMs de un nodo específico"""
        vms_data = self.api.get(f"/nodes/{node}/qemu")
        if vms_data and 'data' in vms_data:
            return vms_data['data']
        return []
    
    def get_vm_config(self, node, vmid):
        """Obtener configuración de una VM"""
        config_data = self.api.get(f"/nodes/{node}/qemu/{vmid}/config")
        if config_data and 'data' in config_data:
            return config_data['data']
        return {}
    
    def get_vm_status(self, node, vmid):
        """Obtener estado actual de una VM"""
        status_data = self.api.get(f"/nodes/{node}/qemu/{vmid}/status/current")
        if status_data and 'data' in status_data:
            return status_data['data']
        return {}
    
    def get_vm_agent_info(self, node, vmid):
        """Obtener información del agente QEMU"""
        try:
            agent_data = self.api.get(f"/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces")
            if agent_data and 'data' in agent_data:
                interfaces = agent_data['data']['result']
                ips = []
                for interface in interfaces:
                    if 'ip-addresses' in interface:
                        for ip_info in interface['ip-addresses']:
                            ip = ip_info.get('ip-address', '')
                            if ip and not ip.startswith('127.') and '::' not in ip:
                                ips.append(ip)
                return ips
        except:
            pass
        return []
    
    def parse_disk_info(self, config):
        """Parsear información de discos desde configuración"""
        disks = []
        total_size_gb = 0
        
        for key, value in config.items():
            if key.startswith(('scsi', 'ide', 'sata', 'virtio')):
                try:
                    # Parsear formato: storage:size,format=qcow2
                    parts = str(value).split(',')
                    if ':' in parts[0]:
                        storage_part = parts[0].split(':')
                        if len(storage_part) >= 2:
                            storage_name = storage_part[0]
                            size_str = storage_part[1]
                            
                            # Convertir tamaño a GB
                            size_gb = self.convert_size_to_gb(size_str)
                            
                            disk_info = {
                                'device': key,
                                'storage': storage_name,
                                'size_gb': size_gb,
                                'raw_config': value
                            }
                            
                            disks.append(disk_info)
                            total_size_gb += size_gb
                            
                except Exception as e:
                    continue
        
        return disks, total_size_gb
    
    def convert_size_to_gb(self, size_str):
        """Convertir tamaño a GB (base 1024)"""
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
    
    def get_vm_details(self, node, vmid):
        """Obtener detalles completos de una VM"""
        try:
            # Obtener configuración y estado
            config = self.get_vm_config(node, vmid)
            status = self.get_vm_status(node, vmid)
            
            if not config:
                return None
            
            # Información básica
            vm_info = {
                'vmid': vmid,
                'name': config.get('name', f'VM-{vmid}'),
                'status': status.get('status', 'unknown'),
                'node': node
            }
            
            # Información de CPU
            vm_info['cpu_cores'] = config.get('cores', 1)
            vm_info['cpu_sockets'] = config.get('sockets', 1)
            
            # Información de memoria (convertir a GB)
            memory_mb = config.get('memory', 0)
            # Asegurar que memory_mb sea numérico
            try:
                memory_mb = int(memory_mb) if memory_mb else 0
                vm_info['memory_gb'] = round(memory_mb / 1024, 2) if memory_mb else 0
            except (ValueError, TypeError):
                vm_info['memory_gb'] = 0
            
            # Información de discos
            disks, total_disk_gb = self.parse_disk_info(config)
            vm_info['total_disk_gb'] = round(total_disk_gb, 2)
            vm_info['disk_count'] = len(disks)
            
            # Información de red
            network_interfaces = len([k for k in config.keys() if k.startswith('net')])
            vm_info['network_interfaces'] = network_interfaces
            
            # Obtener IPs via agente
            ips = self.get_vm_agent_info(node, vmid)
            vm_info['ips'] = ', '.join(ips) if ips else 'No disponible'
            vm_info['ip_count'] = len(ips)
            
            # Información adicional
            vm_info['os_type'] = config.get('ostype', 'No especificado')
            vm_info['agent_enabled'] = 'Sí' if config.get('agent') else 'No'
            vm_info['template'] = 'Sí' if config.get('template') else 'No'
            vm_info['protection'] = 'Sí' if config.get('protection') else 'No'
            vm_info['tags'] = config.get('tags', '')
            vm_info['description'] = config.get('description', '')
            
            return vm_info
            
        except Exception as e:
            print(f"❌ Error obteniendo detalles de VM {vmid}: {e}")
            return None
    
    def get_full_inventory(self):
        """Obtener inventario completo de todas las VMs"""
        vm_inventory = []
        
        try:
            # Obtener información del cluster
            cluster_info = self.get_cluster_info()
            
            # Obtener todos los nodos
            nodes = self.get_nodes()
            if not nodes:
                print("❌ No se encontraron nodos")
                return vm_inventory
            
            print(f"Tipo de instalación: {cluster_info['type']}")
            print(f"Nodos encontrados: {len(nodes)}")
            for i, node in enumerate(nodes, 1):
                status = "online" if node.get('status') == 'online' else "offline"
                print(f"  {i}. Nodo: {node['node']} (Estado: {status})")
            
            # Procesar cada nodo
            for node in nodes:
                if node.get('status') != 'online':
                    print(f"⚠️ Saltando nodo {node['node']} (estado: {node.get('status')})")
                    continue
                
                print(f"\n--- Procesando nodo: {node['node']} ---")
                
                try:
                    # Obtener VMs del nodo
                    vms = self.get_vms_from_node(node['node'])
                    if not vms:
                        print(f"  - Sin VMs en el nodo {node['node']}")
                        continue
                    
                    print(f"  - Encontradas {len(vms)} VMs en este nodo")
                    
                    # Procesar cada VM
                    for vm in vms:
                        try:
                            print(f"    Procesando VM {vm['vmid']} ({vm.get('name', 'Sin nombre')})...")
                            
                            vm_details = self.get_vm_details(node['node'], vm['vmid'])
                            if vm_details:
                                # Agregar información del cluster y nodo
                                vm_details['cluster_type'] = cluster_info['type']
                                vm_details['node'] = node['node']
                                
                                # Agregar fecha de actualización
                                vm_details['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                vm_inventory.append(vm_details)
                                print(f"      ✓ VM {vm['vmid']} procesada correctamente")
                            else:
                                print(f"      ⚠️ No se pudieron obtener detalles de VM {vm['vmid']}")
                                
                        except Exception as e:
                            print(f"      ❌ Error procesando VM {vm['vmid']}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"❌ Error procesando nodo {node['node']}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error en get_full_inventory: {e}")
            
        return vm_inventory
