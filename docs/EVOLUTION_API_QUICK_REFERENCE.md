# Evolution API v2 - Quick Reference Card

## 🔧 Your Configuration
```bash
Base URL: http://<your-server-ip>:<your-port>
Instance: <your-instance-name>
API Key: <your-api-key>
```

## 🚀 Essential Commands

### Check API Status
```bash
curl http://<your-server-ip>:<your-port>
```

### Check Instance Status
```bash
curl -X GET http://<your-server-ip>:<your-port>/instance/fetchInstances \
  -H "apikey: <your-api-key>"
```

### Connect WhatsApp (Generate QR)
```bash
curl -X GET http://<your-server-ip>:<your-port>/instance/connect/<your-instance-name> \
  -H "apikey: <your-api-key>"
```

### Get All Groups
```bash
curl -X GET "http://<your-server-ip>:<your-port>/group/fetchAllGroups/<your-instance-name>?getParticipants=false" \
  -H "apikey: <your-api-key>"
```

### Send Message to Group
```bash
curl -X POST http://<your-server-ip>:<your-port>/message/sendText/<your-instance-name> \
  -H "Content-Type: application/json" \
  -H "apikey: <your-api-key>" \
  -d '{
    "number": "GROUP_ID@g.us",
    "text": "Your message here"
  }'
```

### Get Group Messages
```bash
curl -X GET "http://<your-server-ip>:<your-port>/chat/findMessages/<your-instance-name>?number=GROUP_ID@g.us&limit=10" \
  -H "apikey: <your-api-key>"
```

## 📊 Status Meanings

| Status       | Meaning              | Action           |
|--------------|----------------------|------------------|
| `open`       | Connected & Ready    | ✅ Good to go     |
| `connecting` | Connecting           | 📱 Scan QR code  |
| `close`      | Disconnected         | 🔄 Reconnect     |
| `qr`         | Waiting for QR       | 📱 Scan QR code  |

## 🔗 Important URLs

- **Manager (QR Code)**: http://<your-server-ip>:<your-port>/manager
- **API Documentation**: http://<your-server-ip>:<your-port>/docs
- **Health Check**: http://<your-server-ip>:<your-port>

## 🐍 Python Quick Test

```python
import requests

# Your config
BASE_URL = "http://<your-server-ip>:<your-port>"
API_KEY = "<your-api-key>"
INSTANCE = "<your-instance-name>"

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
1. Visit: http://<your-server-ip>:<your-port>/manager
2. Find your instance `<your-instance-name>`
3. Scan QR code with WhatsApp

### API not responding?
1. Check if the server is running
2. Verify network connectivity
3. Check firewall settings

### Groups not loading?
1. Ensure WhatsApp is connected (status = "open")
2. Check API key permissions
3. Verify instance name is correct

## 📝 Common Group ID Format
- Individual: `<phone-number>@s.whatsapp.net`
- Group: `<group-id>@g.us`

## 🔐 Security Notes
- Keep your API key secret
- Use HTTPS in production
- Regularly rotate tokens
- Monitor API usage

---
💡 **Tip**: Use the `evolution_api_examples.py` script for interactive testing!

