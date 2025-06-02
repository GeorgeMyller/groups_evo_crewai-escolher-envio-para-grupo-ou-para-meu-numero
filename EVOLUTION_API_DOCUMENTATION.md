# Evolution API v2 - Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Instance Management](#instance-management)
3. [Group Management](#group-management)
4. [Message Handling](#message-handling)
5. [Your Current Setup](#your-current-setup)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)

## Introduction

Evolution API v2 is a robust platform for WhatsApp automation that supports:
- **WhatsApp Business API** (official)
- **Baileys** (open source)
- **Multiple instances** per server
- **Real-time webhooks**
- **Group management**
- **Message automation**

### Key Features
- 🔄 Real-time message handling
- 📱 Multiple WhatsApp instances
- 👥 Complete group management
- 🤖 Bot integrations (ChatGPT, Typebot, Chatwoot)
- 📊 Webhook support
- 🔐 Authentication & security

## Instance Management

### 1. Create Instance

**Endpoint:** `POST /instance/create`

```bash
curl -X POST http://192.168.1.151:8081/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "instanceName": "AgentGeorgeMyller",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Parameters:**
- `instanceName` (required): Unique name for the instance
- `qrcode` (optional): Generate QR code automatically (default: true)
- `integration` (optional): "WHATSAPP-BAILEYS" or "WHATSAPP-BUSINESS"
- `token` (optional): Custom token for the instance
- `number` (optional): Phone number with country code
- `webhook` (optional): Webhook URL for events

### 2. Connect Instance

**Endpoint:** `GET /instance/connect/{instance}`

```bash
curl -X GET http://192.168.1.151:8081/instance/connect/AgentGeorgeMyller \
  -H "apikey: YOUR_API_KEY"
```

**Response:**
```json
{
  "pairingCode": "WZYEH1YY",
  "code": "2@y8eK+bjtEjUWy9/FOM...",
  "count": 1
}
```

### 3. Check Instance Status

**Endpoint:** `GET /instance/fetchInstances`

```bash
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: YOUR_API_KEY"
```

**Response:**
```json
[
  {
    "instance": {
      "instanceName": "AgentGeorgeMyller",
      "owner": "351912331561@s.whatsapp.net",
      "profileName": "George Myller",
      "profilePictureUrl": "https://...",
      "status": "open"
    }
  }
]
```

**Status Values:**
- `"open"`: Connected and ready
- `"connecting"`: Attempting to connect
- `"close"`: Disconnected
- `"qr"`: Waiting for QR scan

### 4. Restart Instance

**Endpoint:** `PUT /instance/restart/{instance}`

```bash
curl -X PUT http://192.168.1.151:8081/instance/restart/AgentGeorgeMyller \
  -H "apikey: YOUR_API_KEY"
```

### 5. Delete Instance

**Endpoint:** `DELETE /instance/delete/{instance}`

```bash
curl -X DELETE http://192.168.1.151:8081/instance/delete/AgentGeorgeMyller \
  -H "apikey: YOUR_API_KEY"
```

## Group Management

### 1. Fetch All Groups

**Endpoint:** `GET /group/fetchAllGroups/{instance}`

```bash
curl -X GET "http://192.168.1.151:8081/group/fetchAllGroups/AgentGeorgeMyller?getParticipants=false" \
  -H "apikey: YOUR_API_KEY"
```

**Parameters:**
- `getParticipants` (required): Include group members (true/false)

**Response:**
```json
[
  {
    "id": "120363295648424210@g.us",
    "subject": "Example Group",
    "subjectOwner": "553198296801@s.whatsapp.net",
    "subjectTime": 1714769954,
    "pictureUrl": null,
    "size": 10,
    "creation": 1714769954,
    "owner": "553198296801@s.whatsapp.net",
    "desc": "Group description",
    "descId": "BAE57E16498982ED",
    "restrict": false,
    "announce": false
  }
]
```

### 2. Find Group by ID

**Endpoint:** `GET /group/findGroupByJid/{instance}`

```bash
curl -X GET "http://192.168.1.151:8081/group/findGroupByJid/AgentGeorgeMyller?groupJid=120363295648424210@g.us" \
  -H "apikey: YOUR_API_KEY"
```

### 3. Get Group Members

**Endpoint:** `GET /group/participants/{instance}`

```bash
curl -X GET "http://192.168.1.151:8081/group/participants/AgentGeorgeMyller?groupJid=120363295648424210@g.us" \
  -H "apikey: YOUR_API_KEY"
```

### 4. Create Group

**Endpoint:** `POST /group/create/{instance}`

```bash
curl -X POST http://192.168.1.151:8081/group/create/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "subject": "New Group",
    "description": "Group description",
    "participants": ["5511999999999@s.whatsapp.net"]
  }'
```

### 5. Update Group Settings

**Endpoint:** `PUT /group/updateGroupSettings/{instance}`

```bash
curl -X PUT http://192.168.1.151:8081/group/updateGroupSettings/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "groupJid": "120363295648424210@g.us",
    "action": "announcement",
    "value": true
  }'
```

**Actions:**
- `announcement`: Only admins can send messages
- `restrict`: Only admins can edit group info
- `locked`: Only admins can change settings

## Message Handling

### 1. Send Text Message

**Endpoint:** `POST /message/sendText/{instance}`

```bash
curl -X POST http://192.168.1.151:8081/message/sendText/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "number": "120363295648424210@g.us",
    "text": "Hello group!"
  }'
```

### 2. Send Media Message

**Endpoint:** `POST /message/sendMedia/{instance}`

```bash
curl -X POST http://192.168.1.151:8081/message/sendMedia/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "number": "120363295648424210@g.us",
    "mediatype": "image",
    "media": "https://example.com/image.jpg",
    "caption": "Image caption"
  }'
```

### 3. Find Messages

**Endpoint:** `GET /chat/findMessages/{instance}`

```bash
curl -X GET "http://192.168.1.151:8081/chat/findMessages/AgentGeorgeMyller?number=120363295648424210@g.us&limit=50" \
  -H "apikey: YOUR_API_KEY"
```

## Your Current Setup

Based on your configuration in `.env`:

```properties
EVO_API_TOKEN=3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n
EVO_INSTANCE_NAME=AgentGeorgeMyller
EVO_BASE_URL=http://192.168.1.151:8081
WHATSAPP_NUMBER=351912331561
```

### Quick Status Check

```bash
# Check API status
curl http://192.168.1.151:8081

# Check your instance status
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"

# Get your groups
curl -X GET "http://192.168.1.151:8081/group/fetchAllGroups/AgentGeorgeMyller?getParticipants=false" \
  -H "apikey: 3v0lut10n429683C4C977415CAAFCCE10F7D57E113v0lut10n"
```

### Your System Integration

Your `GroupController` class uses these endpoints:

1. **Instance Status**: `/instance/fetchInstances`
2. **Groups**: `/group/fetchAllGroups/{instance}?getParticipants=false`
3. **Messages**: `/chat/findMessages/{instance}`

## Common Operations

### 1. Connect WhatsApp for First Time

```bash
# Step 1: Connect instance
curl -X GET http://192.168.1.151:8081/instance/connect/AgentGeorgeMyller \
  -H "apikey: YOUR_API_KEY"

# Step 2: Scan QR code in WhatsApp
# Go to http://192.168.1.151:8081/manager

# Step 3: Verify connection
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: YOUR_API_KEY"
```

### 2. Monitor Group Activity

```bash
# Get all groups with member count
curl -X GET "http://192.168.1.151:8081/group/fetchAllGroups/AgentGeorgeMyller?getParticipants=false" \
  -H "apikey: YOUR_API_KEY"

# Get recent messages from a group
curl -X GET "http://192.168.1.151:8081/chat/findMessages/AgentGeorgeMyller?number=GROUP_ID@g.us&limit=10" \
  -H "apikey: YOUR_API_KEY"
```

### 3. Send Automated Messages

```bash
# Send text to group
curl -X POST http://192.168.1.151:8081/message/sendText/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "number": "GROUP_ID@g.us",
    "text": "Automated message from bot"
  }'
```

### 4. Webhook Setup

```bash
# Set webhook for instance
curl -X POST http://192.168.1.151:8081/webhook/set/AgentGeorgeMyller \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["messages.upsert", "groups.upsert"]
  }'
```

## Troubleshooting

### Common Issues

1. **Instance not connecting**
   - Status shows "connecting"
   - Solution: Scan QR code at manager URL

2. **API not responding**
   - Check if Evolution API is running
   - Verify network connectivity

3. **Groups not loading**
   - Check WhatsApp connection status
   - Verify API permissions

4. **Messages not sending**
   - Check instance status
   - Verify group ID format

### Debug Commands

```bash
# Check API health
curl http://192.168.1.151:8081

# Check instance details
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: YOUR_API_KEY" | jq '.'

# Check specific instance
curl -X GET http://192.168.1.151:8081/instance/fetchInstances \
  -H "apikey: YOUR_API_KEY" | jq '.[] | select(.instance.instanceName=="AgentGeorgeMyller")'
```

### Status Codes

- **200**: Success
- **400**: Bad request (check parameters)
- **401**: Unauthorized (check API key)
- **404**: Instance not found
- **500**: Server error

## Advanced Features

### 1. Bot Integrations

- **OpenAI/ChatGPT**: AI-powered responses
- **Typebot**: Visual flow builder
- **Chatwoot**: Customer support integration
- **Dify**: AI workflow automation

### 2. Webhook Events

- `messages.upsert`: New messages
- `groups.upsert`: Group updates
- `qr.updated`: QR code updates
- `connection.update`: Connection status
- `status.instance`: Instance status

### 3. Real-time Monitoring

Use WebSocket connection for real-time events:

```javascript
const ws = new WebSocket('ws://192.168.1.151:8081/instance/AgentGeorgeMyller');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};
```

## Best Practices

1. **Keep instances connected**: Monitor connection status regularly
2. **Handle rate limits**: Respect WhatsApp's message limits
3. **Use webhooks**: For real-time message processing
4. **Cache data**: Store group info locally for better performance
5. **Error handling**: Always check response status codes
6. **Security**: Protect your API keys and tokens

## Resources

- **Official Documentation**: https://doc.evolution-api.com/v2
- **GitHub Repository**: https://github.com/EvolutionAPI/evolution-api
- **Postman Collection**: Available on Postman API Network
- **Community**: https://evolution-api.com/

---

*This documentation is based on Evolution API v2.2.3 and your current system configuration.*
