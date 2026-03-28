#!/usr/bin/env python3
"""
Proxmox Multi-Cluster Inventory Tool
====================================

Herramienta para generar inventarios de VMs desde múltiples clusters Proxmox
y exportar a diferentes formatos (CSV, JSON, Excel, SharePoint).

Autor: [SktCod.ByChisto]
Versión: 1.0.0
Fecha: 2025-06-25
"""

import sys
import argparse
import traceback
from pathlib import Path

# Imports de módulos propios
from config import ConfigManager, create_example_env_file, create_sharepoint_env_example
from modules import ProxmoxClusterManager, FileExporter, SharePointUploader
from utils import SystemValidator


class ProxmoxInventoryApp:
    """Aplicación principal de inventario Proxmox"""
    
    def __init__(self):
        self.version = "2.0.0"
        self.config_manager = None
        self.cluster_manager = None
        self.file_exporter = None
        self.sharepoint_uploader = None
    
    def print_banner(self):
        """Mostrar banner de la aplicación"""
        print("=" * 70)
        print("🚀 PROXMOX MULTI-CLUSTER INVENTORY TOOL")
        print(f"📋 Versión: {self.version}")
        print("🔧 Herramienta para inventario automatizado de VMs")
        print("=" * 70)
    
    def check_system_requirements(self):
        """Verificar requisitos del sistema"""
        print("🔍 Verificando requisitos del sistema...")
        
        # Verificar versión de Python
        is_valid, message = SystemValidator.check_python_version()
        if not is_valid:
            print(f"❌ {message}")
            return False
        print(f"✓ {message}")
        
        # Verificar dependencias
        dependencies = SystemValidator.check_dependencies()
        
        required_missing = []
        optional_missing = []
        
        for module, info in dependencies.items():
            if info['installed']:
                print(f"✓ {module}: Instalado")
            else:
                if module in ['requests', 'dotenv']:
                    required_missing.append(module)
                    print(f"❌ {module}: {info['description']} - REQUERIDO")
                else:
                    optional_missing.append(module)
                    print(f"⚠️  {module}: {info['description']} - OPCIONAL")
        
        if required_missing:
            print(f"\n❌ Dependencias requeridas faltantes: {', '.join(required_missing)}")
            print("💡 Instala con: pip install requests python-dotenv")
            return False
        
        if optional_missing:
            print(f"\n⚠️  Dependencias opcionales faltantes: {', '.join(optional_missing)}")
            print("💡 Para funcionalidad completa: pip install openpyxl msal")
        
        print("✅ Requisitos del sistema verificados\n")
        return True
    
    def initialize_managers(self, env_file):
        """Inicializar gestores de la aplicación"""
        try:
            # Inicializar gestor de configuración
            self.config_manager = ConfigManager(env_file)
            
            if not self.config_manager.get_proxmox_hosts():
                print("❌ No se encontraron configuraciones válidas de Proxmox")
                return False
            
            # Inicializar gestor de clusters
            self.cluster_manager = ProxmoxClusterManager(self.config_manager)
            
            # Inicializar exportador de archivos
            self.file_exporter = FileExporter()
            
            # Inicializar uploader SharePoint (si está configurado)
            self.sharepoint_uploader = SharePointUploader(self.config_manager)
            
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando aplicación: {e}")
            return False
    
    def process_inventory(self):
        """Procesar inventario de todos los clusters"""
        try:
            print("🚀 Iniciando inventario multi-cluster de Proxmox...")
            
            # Obtener inventario de todos los hosts
            inventory = self.cluster_manager.get_inventory_from_all_hosts()
            
            if not inventory:
                print("❌ No se pudo generar el inventario - ninguna VM encontrada")
                return None
            
            # Mostrar resumen
            self.cluster_manager.print_summary(inventory)
            
            return inventory
            
        except Exception as e:
            print(f"❌ Error procesando inventario: {e}")
            traceback.print_exc()
            return None
    
    def export_files(self, inventory, output_format):
        """Exportar inventario a archivos locales"""
        if output_format == 'sharepoint':
            return True  # No exportar archivos locales si solo es SharePoint
        
        try:
            print(f"\n📁 Exportando inventario en formato: {output_format}")
            result = self.file_exporter.save_by_format(inventory, output_format)
            
            if result:
                print("✅ Archivos locales exportados exitosamente")
                return True
            else:
                print("❌ Error exportando archivos locales")
                return False
                
        except Exception as e:
            print(f"❌ Error exportando archivos: {e}")
            return False
    
    def upload_to_sharepoint(self, inventory, sharepoint_folder=None, sharepoint_filename=None):
        """Subir inventario a SharePoint"""
        try:
            if not self.sharepoint_uploader.is_configured():
                print("\n⚠️  Configuración SharePoint no encontrada")
                print("💡 Usa --setup-sharepoint para configurar SharePoint")
                return False
            
            print(f"\n📤 Actualizando inventario en SharePoint...")
            
            # Usar valores por defecto del .env si no se especifican
            folder_path = sharepoint_folder or self.sharepoint_uploader.default_folder
            filename = sharepoint_filename or self.sharepoint_uploader.default_filename
            
            success = self.sharepoint_uploader.upload_to_sharepoint(
                inventory, 
                folder_path=folder_path,
                filename=filename
            )
            
            if success:
                print("✅ SharePoint actualizado exitosamente")
                return True
            else:
                print("❌ Error actualizando SharePoint")
                return False
                
        except Exception as e:
            print(f"❌ Error con SharePoint: {e}")
            return False
    
    def run(self, args):
        """Ejecutar aplicación principal"""
        try:
            # Mostrar banner
            self.print_banner()
            
            # Verificar requisitos del sistema
            if not self.check_system_requirements():
                return 1
            
            # Inicializar gestores
            if not self.initialize_managers(args.env_file):
                return 1
            
            # Procesar inventario
            inventory = self.process_inventory()
            if not inventory:
                return 1
            
            print(f"\n📊 Inventario obtenido: {len(inventory)} VMs")
            
            # Exportar archivos locales
            if not self.export_files(inventory, args.output):
                return 1
            
            # Subir a SharePoint si está configurado
            if args.output in ['sharepoint', 'all']:
                self.upload_to_sharepoint(
                    inventory, 
                    args.sharepoint_folder, 
                    args.sharepoint_filename
                )
            
            # Mensaje final de éxito
            print(f"\n🎉 ¡Inventario completado exitosamente!")
            print(f"📊 Total de VMs procesadas: {len(inventory)}")
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Proceso interrumpido por el usuario")
            return 1
        except Exception as e:
            print(f"\n❌ Error general de la aplicación: {e}")
            traceback.print_exc()
            return 1


def create_argument_parser():
    """Crear parser de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Generar inventario de VMs en múltiples clusters Proxmox',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --output excel
  python main.py --output all
  python main.py --output sharepoint --sharepoint-folder "IT-Infrastructure"
  python main.py --create-example
  python main.py --setup-sharepoint
        """
    )
    
    # Argumentos principales
    parser.add_argument(
        '--env-file', 
        default='.env',
        help='Archivo de configuración .env (por defecto: .env)'
    )
    
    parser.add_argument(
        '--output', 
        choices=['csv', 'json', 'excel', 'sharepoint', 'all'], 
        default='all',
        help='Formato de salida (por defecto: all)'
    )
    
    # Argumentos SharePoint
    parser.add_argument(
        '--sharepoint-folder',
        help='Carpeta en SharePoint donde subir el archivo (por defecto: del .env)'
    )
    
    parser.add_argument(
        '--sharepoint-filename',
        help='Nombre fijo del archivo en SharePoint (por defecto: del .env)'
    )
    
    # Argumentos de configuración
    parser.add_argument(
        '--setup-sharepoint', 
        action='store_true',
        help='Agregar configuración SharePoint a .env.example'
    )
    
    parser.add_argument(
        '--create-example', 
        action='store_true',
        help='Crear archivo .env.example con configuración de muestra'
    )
    
    # Argumentos informativos
    parser.add_argument(
        '--version', 
        action='version', 
        version='Proxmox Inventory Tool v2.0.0'
    )
    
    parser.add_argument(
        '--check-system', 
        action='store_true',
        help='Verificar requisitos del sistema y salir'
    )
    
    return parser


def main():
    """Función principal"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Manejar comandos especiales que no requieren la aplicación completa
    if args.create_example:
        create_example_env_file()
        return 0
    
    if args.setup_sharepoint:
        create_sharepoint_env_example()
        print("💡 Ahora edita .env con tu configuración SharePoint")
        return 0
    
    if args.check_system:
        app = ProxmoxInventoryApp()
        if app.check_system_requirements():
            print("✅ Sistema listo para ejecutar la aplicación")
            return 0
        else:
            print("❌ Sistema no cumple los requisitos")
            return 1
    
    # Verificar que existe el archivo .env
    if not Path(args.env_file).exists():
        print(f"❌ Archivo {args.env_file} no encontrado")
        print("💡 Usa --create-example para crear un archivo de configuración")
        return 1
    
    # Ejecutar aplicación principal
    app = ProxmoxInventoryApp()
    return app.run(args)


if __name__ == "__main__":
    sys.exit(main())
