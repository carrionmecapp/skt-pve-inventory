"""
Módulo para manejar la comunicación con la API de Proxmox VE
"""

import requests
import urllib3

# Suprimir warnings SSL para conexiones no verificadas
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProxmoxAPI:
    """Cliente para interactuar con la API de Proxmox VE"""
    
    def __init__(self, host, username, password, verify_ssl=True):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.csrf_token = None
        
        # Configurar verificación SSL
        if not verify_ssl:
            self.session.verify = False
        
        self.base_url = f"https://{self.host}:8006/api2/json"
        
    def authenticate(self):
        """Autenticar con Proxmox"""
        try:
            auth_url = f"{self.base_url}/access/ticket"
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(auth_url, data=auth_data)
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result:
                    ticket = result['data']['ticket']
                    csrf_token = result['data']['CSRFPreventionToken']
                    
                    # Configurar cookies y headers
                    self.session.cookies.set('PVEAuthCookie', ticket)
                    self.session.headers.update({'CSRFPreventionToken': csrf_token})
                    self.csrf_token = csrf_token
                    
                    return True
            
            print(f"❌ Error de autenticación: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Error conectando a Proxmox: {e}")
            return False
    
    def get(self, endpoint):
        """Realizar petición GET a la API"""
        if not self.csrf_token:
            if not self.authenticate():
                return None
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error en GET {endpoint}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error en petición GET: {e}")
            return None
