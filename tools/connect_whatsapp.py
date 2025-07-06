#!/usr/bin/env python3
"""
Utilitário para verificar e gerenciar conexão WhatsApp via Evolution API
"""
import os
import requests
import json
from io import BytesIO
import base64
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path, override=True)

def get_connection_state():
    """Verifica o estado da conexão da instância"""
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    
    headers = {"Content-Type": "application/json", "apikey": api_token}
    
    try:
        url = f"{base_url}/instance/connectionState/{instance_name}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("instance", {})
        else:
            return {"error": f"Status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def connect_instance():
    """Tenta conectar a instância ao WhatsApp"""
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    
    headers = {"Content-Type": "application/json", "apikey": api_token}
    
    try:
        url = f"{base_url}/instance/connect/{instance_name}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def get_qr_code():
    """Obtém o QR code para conectar ao WhatsApp"""
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    
    headers = {"Content-Type": "application/json", "apikey": api_token}
    
    try:
        url = f"{base_url}/instance/qrcode/{instance_name}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("📱 GERENCIADOR DE CONEXÃO WHATSAPP - EVOLUTION API")
    print("=" * 60)
    
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    print(f"Instância: {instance_name}")
    
    # 1. Verificar estado atual
    print("\n🔍 1. Verificando estado da conexão...")
    state = get_connection_state()
    
    if "error" in state:
        print(f"❌ Erro ao verificar estado: {state['error']}")
        return
    
    current_state = state.get("state", "unknown")
    print(f"Estado atual: {current_state}")
    
    if current_state == "open":
        print("✅ WhatsApp já está conectado!")
        print("✅ A API deveria estar funcionando normalmente.")
        return
    elif current_state == "connecting":
        print("🔄 WhatsApp está tentando conectar...")
        print("📱 Você pode precisar escanear um QR code.")
    elif current_state == "close":
        print("❌ WhatsApp está desconectado.")
        print("🔄 Tentando iniciar conexão...")
    else:
        print(f"⚠️ Estado desconhecido: {current_state}")
    
    # 2. Tentar conectar
    print("\n🔗 2. Tentando conectar instância...")
    connect_result = connect_instance()
    
    if "error" in connect_result:
        print(f"❌ Erro ao conectar: {connect_result['error']}")
    else:
        print("✅ Comando de conexão enviado!")
        print(f"Resultado: {connect_result}")
    
    # 3. Obter QR code se necessário
    print("\n📱 3. Obtendo QR code...")
    qr_result = get_qr_code()
    
    if "error" in qr_result:
        print(f"❌ Erro ao obter QR code: {qr_result['error']}")
    else:
        if "base64" in qr_result:
            print("✅ QR code obtido!")
            print("📱 ESCANEIE ESTE QR CODE COM SEU WHATSAPP:")
            print("-" * 50)
            print(f"QR Code Base64: {qr_result['base64'][:100]}...")
            print("(Para ver o QR code, acesse o manager da API ou use uma ferramenta para converter base64)")
        elif "qrcode" in qr_result:
            print("✅ QR code obtido!")
            print(f"QR Code: {qr_result['qrcode']}")
        else:
            print(f"QR Code result: {qr_result}")
    
    # 4. Instruções
    print("\n" + "=" * 60)
    print("📋 INSTRUÇÕES PARA CONECTAR:")
    print("-" * 30)
    print("1. Abra o WhatsApp no seu celular")
    print("2. Vá em Configurações > Aparelhos conectados")
    print("3. Toque em 'Conectar um aparelho'")
    print("4. Escaneie o QR code mostrado acima")
    print("5. Aguarde a conexão ser estabelecida")
    
    # Constrói a URL do manager dinamicamente a partir da EVO_BASE_URL
    base_url = os.getenv("EVO_BASE_URL")
    manager_url = "Não foi possível determinar a URL do manager."
    if base_url:
        try:
            parsed_url = urlparse(base_url)
            # Assume que o manager está no mesmo host, na porta 8081
            manager_url = f"{parsed_url.scheme}://{parsed_url.hostname}:8081/manager"
        except Exception as e:
            manager_url = f"Erro ao construir a URL do manager: {e}"

    print(f"\n🌐 Manager URL: {manager_url}")
    print("   (Acesse esta URL no navegador para ver o QR code visualmente)")
    
    print("\n🔄 Após conectar, execute novamente o sistema!")

if __name__ == "__main__":
    main()
