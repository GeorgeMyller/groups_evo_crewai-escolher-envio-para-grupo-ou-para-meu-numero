# Evolution API v2 - Quick Reference Card

## 🔧 Your Configuration
```bash
Base URL: http://192.168.1.151:8081
Instance: AgentGeorgeMyller
API Key: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n
```

## 🚀 Essential Commands

### Check API Status
```bash
curl http://192.168.1.151:8081
```

### Check Instance Status
```bash
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
```

### Connect WhatsApp (Generate QR)
```bash
curl -X GET http://192.168.1.151:8081/instance/connect/AgentGeorgeMyller \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
```

### Get All Groups
```bash
curl -X GET "http://192.168.1.151:8081/group/fetchAllGroups/AgentGeorgeMyller?getParticipants=false" \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
```

### Send Message to Group
```bash
curl -X POST http://192.168.1.151:8081/message/sendText/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n" \
  -d '{
    "number": "GROUP_ID@g.us",
    "text": "Your message here"
  }'
```

### Get Group Messages
```bash
curl -X GET "http://192.168.1.151:8081/chat/findMessages/AgentGeorgeMyller?number=GROUP_ID@g.us&limit=10" \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
```

## 📊 Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| `open` | Connected & Ready | ✅ Good to go |
| `connecting` | Connecting | 📱 Scan QR code |
| `close` | Disconnected | 🔄 Reconnect |
| `qr` | Waiting for QR | 📱 Scan QR code |

## 🔗 Important URLs

- **Manager (QR Code)**: http://192.168.1.151:8081/manager
- **API Documentation**: http://192.168.1.151:8081/docs
- **Health Check**: http://192.168.1.151:8081

## 🐍 Python Quick Test

```python
import requests

# Your config
BASE_URL = "http://192.168.1.151:8081"
API_KEY = "3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
INSTANCE = "AgentGeorgeMyller"

headers = {"apikey": API_KEY}

# Check instance status
response = requests.get(f"{BASE_URL}/instance/fetchInstances", headers=headers)
print(response.json())

# Get groups
response = requests.get(
    f"{BASE_URL}/group/fetchAllGroups/{INSTANCE}?getParticipants=false", 
    headers=headers
)
print(response.json())
```

## 🛠️ Troubleshooting

### Instance not connecting?
1. Visit: http://192.168.1.151:8081/manager
2. Find your instance "AgentGeorgeMyller"
3. Scan QR code with WhatsApp

### API not responding?
1. Check if Docker container is running
2. Verify network connectivity
3. Check firewall settings

### Groups not loading?
1. Ensure WhatsApp is connected (status = "open")
2. Check API key permissions
3. Verify instance name is correct

## 📝 Common Group ID Format
- Individual: `5511999999999@s.whatsapp.net`
- Group: `120363295648424210@g.us`

## 🔐 Security Notes
- Keep your API key secret
- Use HTTPS in production
- Regularly rotate tokens
- Monitor API usage

---
💡 **Tip**: Use the `evolution_api_examples.py` script for interactive testing!
