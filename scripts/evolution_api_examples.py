#!/usr/bin/env python3
"""
Evolution API - Practical Examples
Exemplos práticos para trabalhar com a Evolution API

This script provides practical examples for common Evolution API operations
based on your current system configuration.
"""

import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EvolutionAPIExamples:
    def __init__(self):
        self.base_url = os.getenv('EVO_BASE_URL', 'http://192.168.1.151:8081')
        self.api_key = os.getenv('EVO_API_TOKEN')
        self.instance_name = os.getenv('EVO_INSTANCE_NAME', 'AgentGeorgeMyller')
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
    
    def check_api_health(self):
        """Check if Evolution API is running"""
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ API is running!")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Manager: {data.get('manager', 'N/A')}")
                print(f"   Swagger: {data.get('swagger', 'N/A')}")
                return True
            else:
                print(f"❌ API returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return False
    
    def get_instance_status(self):
        """Get status of your WhatsApp instance"""
        try:
            url = f"{self.base_url}/instance/fetchInstances"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                instances = response.json()
                for item in instances:
                    instance = item.get('instance', {})
                    if instance.get('instanceName') == self.instance_name:
                        print(f"📱 Instance: {instance.get('instanceName')}")
                        print(f"   Status: {instance.get('status', 'Unknown')}")
                        print(f"   Owner: {instance.get('owner', 'N/A')}")
                        print(f"   Profile: {instance.get('profileName', 'N/A')}")
                        return instance
                
                print(f"❌ Instance '{self.instance_name}' not found")
                return None
            else:
                print(f"❌ Failed to get instances: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting instance status: {e}")
            return None
    
    def connect_instance(self):
        """Connect instance and get QR code"""
        try:
            url = f"{self.base_url}/instance/connect/{self.instance_name}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("📱 QR Code generated!")
                print(f"   Pairing Code: {data.get('pairingCode', 'N/A')}")
                print(f"   Count: {data.get('count', 'N/A')}")
                print(f"🔗 Scan QR at: {self.base_url}/manager")
                return data
            else:
                print(f"❌ Failed to connect: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error connecting instance: {e}")
            return None
    
    def get_all_groups(self, include_participants=False):
        """Get all WhatsApp groups"""
        try:
            url = f"{self.base_url}/group/fetchAllGroups/{self.instance_name}"
            params = {'getParticipants': str(include_participants).lower()}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                groups = response.json()
                print(f"📊 Found {len(groups)} groups:")
                
                for i, group in enumerate(groups, 1):
                    print(f"\n{i}. {group.get('subject', 'No Name')}")
                    print(f"   ID: {group.get('id', 'N/A')}")
                    print(f"   Size: {group.get('size', 0)} members")
                    print(f"   Owner: {group.get('owner', 'N/A')}")
                    print(f"   Created: {self._format_timestamp(group.get('creation'))}")
                    if group.get('desc'):
                        print(f"   Description: {group.get('desc')[:50]}...")
                
                return groups
            else:
                print(f"❌ Failed to get groups: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting groups: {e}")
            return None
    
    def get_group_messages(self, group_id, limit=10):
        """Get recent messages from a group"""
        try:
            url = f"{self.base_url}/chat/findMessages/{self.instance_name}"
            params = {
                'number': group_id,
                'limit': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                messages = response.json()
                print(f"💬 Last {len(messages)} messages from group:")
                
                for i, msg in enumerate(messages[-5:], 1):  # Show last 5
                    key = msg.get('key', {})
                    message = msg.get('message', {})
                    
                    sender = key.get('participant', key.get('remoteJid', 'Unknown'))
                    timestamp = self._format_timestamp(msg.get('messageTimestamp'))
                    
                    # Get message text
                    text = ""
                    if 'conversation' in message:
                        text = message['conversation']
                    elif 'extendedTextMessage' in message:
                        text = message['extendedTextMessage'].get('text', '')
                    
                    print(f"\n{i}. [{timestamp}] {sender}")
                    print(f"   {text[:100]}...")
                
                return messages
            else:
                print(f"❌ Failed to get messages: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return None
    
    def send_message_to_group(self, group_id, message):
        """Send a text message to a group"""
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            data = {
                'number': group_id,
                'text': message
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message sent successfully!")
                print(f"   Key: {result.get('key', {}).get('id', 'N/A')}")
                return result
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def _format_timestamp(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return "Unknown"
        try:
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')
        except:
            return "Invalid date"
    
    def run_diagnostics(self):
        """Run complete diagnostics"""
        print("🔍 Running Evolution API Diagnostics...")
        print("=" * 50)
        
        # 1. Check API health
        print("\n1. Checking API Health...")
        api_ok = self.check_api_health()
        
        if not api_ok:
            print("\n❌ API is not accessible. Check if Evolution API is running.")
            return
        
        # 2. Check instance status
        print("\n2. Checking Instance Status...")
        instance = self.get_instance_status()
        
        if not instance:
            print("\n❌ Instance not found or not accessible.")
            return
        
        status = instance.get('status', 'unknown')
        
        if status == 'open':
            print("✅ WhatsApp is connected and ready!")
            
            # 3. Get groups
            print("\n3. Fetching Groups...")
            groups = self.get_all_groups()
            
            if groups and len(groups) > 0:
                print(f"\n✅ Successfully retrieved {len(groups)} groups")
                
                # 4. Test getting messages from first group
                print("\n4. Testing Message Retrieval...")
                first_group = groups[0]
                messages = self.get_group_messages(first_group['id'], 5)
                
                if messages:
                    print("✅ Message retrieval working!")
                else:
                    print("⚠️  Could not retrieve messages")
            else:
                print("⚠️  No groups found or error retrieving groups")
                
        elif status == 'connecting':
            print("⚠️  WhatsApp is connecting. You may need to scan QR code.")
            print(f"🔗 Visit: {self.base_url}/manager")
            
        elif status == 'close':
            print("❌ WhatsApp is disconnected. Attempting to connect...")
            self.connect_instance()
            
        else:
            print(f"❓ Unknown status: {status}")
        
        print("\n" + "=" * 50)
        print("✅ Diagnostics completed!")

def main():
    """Main function with interactive menu"""
    api = EvolutionAPIExamples()
    
    while True:
        print("\n" + "=" * 50)
        print("🤖 Evolution API - Practical Examples")
        print("=" * 50)
        print("1. Run Complete Diagnostics")
        print("2. Check API Health")
        print("3. Check Instance Status")
        print("4. Connect Instance (Generate QR)")
        print("5. Get All Groups")
        print("6. Get Group Messages")
        print("7. Send Test Message")
        print("0. Exit")
        print("-" * 50)
        
        try:
            choice = input("Choose an option (0-7): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
                
            elif choice == '1':
                api.run_diagnostics()
                
            elif choice == '2':
                api.check_api_health()
                
            elif choice == '3':
                api.get_instance_status()
                
            elif choice == '4':
                api.connect_instance()
                
            elif choice == '5':
                api.get_all_groups()
                
            elif choice == '6':
                groups = api.get_all_groups()
                if groups:
                    print("\nAvailable groups:")
                    for i, group in enumerate(groups, 1):
                        print(f"{i}. {group.get('subject', 'No Name')} ({group.get('size', 0)} members)")
                    
                    try:
                        group_num = int(input("Select group number: ")) - 1
                        if 0 <= group_num < len(groups):
                            api.get_group_messages(groups[group_num]['id'])
                        else:
                            print("❌ Invalid group number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                        
            elif choice == '7':
                groups = api.get_all_groups()
                if groups:
                    print("\nAvailable groups:")
                    for i, group in enumerate(groups, 1):
                        print(f"{i}. {group.get('subject', 'No Name')}")
                    
                    try:
                        group_num = int(input("Select group number: ")) - 1
                        if 0 <= group_num < len(groups):
                            message = input("Enter message to send: ").strip()
                            if message:
                                api.send_message_to_group(groups[group_num]['id'], message)
                            else:
                                print("❌ Message cannot be empty")
                        else:
                            print("❌ Invalid group number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                        
            else:
                print("❌ Invalid option. Please choose 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
