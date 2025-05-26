"""
Testes unitários para MessageSandeco / Unit tests for MessageSandeco class
"""
import pytest
import sys
import os
import base64

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from message_sandeco import MessageSandeco


class TestMessageSandeco:
    """Testes para a classe MessageSandeco"""
    
    def test_message_creation_with_text(self):
        """Teste de criação de mensagem de texto"""
        raw_data = {
            "key": {
                "remoteJid": "120363398170141701@g.us",
                "participant": "5511999999999@s.whatsapp.net"
            },
            "messageTimestamp": 1640995200,
            "pushName": "Test User",
            "message": {
                "conversation": "Olá, teste de mensagem"
            }
        }
        
        message = MessageSandeco(raw_data)
        
        assert message.message_type == MessageSandeco.TYPE_TEXT
        assert message.scope == MessageSandeco.SCOPE_GROUP
        assert message.group_id == "120363398170141701"
        assert message.phone == "5511999999999"
        assert message.get_text() == "Olá, teste de mensagem"
        assert message.get_name() == "Test User"
    
    def test_message_creation_with_private_text(self):
        """Teste de criação de mensagem privada"""
        raw_data = {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net"
            },
            "messageTimestamp": 1640995200,
            "pushName": "Private User",
            "message": {
                "conversation": "Mensagem privada"
            }
        }
        
        message = MessageSandeco(raw_data)
        
        assert message.message_type == MessageSandeco.TYPE_TEXT
        assert message.scope == MessageSandeco.SCOPE_PRIVATE
        assert message.group_id is None
        assert message.phone == "5511999999999"
    
    def test_decode_base64(self):
        """Teste de decodificação base64"""
        message = MessageSandeco({})
        test_string = "Hello World"
        encoded = base64.b64encode(test_string.encode()).decode()
        
        decoded = message.decode_base64(encoded)
        assert decoded == test_string
    
    def test_get_data_from_audio_message(self):
        """Teste de mensagem de áudio"""
        raw_data = {
            "key": {
                "remoteJid": "120363398170141701@g.us",
                "participant": "5511999999999@s.whatsapp.net"
            },
            "messageTimestamp": 1640995200,
            "pushName": "Audio User",
            "message": {
                "audioMessage": {
                    "url": "https://example.com/audio.mp3",
                    "mimetype": "audio/mpeg",
                    "seconds": 30
                }
            }
        }
        
        message = MessageSandeco(raw_data)
        
        assert message.message_type == MessageSandeco.TYPE_AUDIO
        assert message.scope == MessageSandeco.SCOPE_GROUP
        assert message.get_text() == "🎵 Áudio"
    
    def test_unknown_scope(self):
        """Teste de escopo desconhecido"""
        raw_data = {
            "key": {
                "remoteJid": "unknown@unknown.format"
            },
            "messageTimestamp": 1640995200,
            "pushName": "Unknown User",
            "message": {
                "conversation": "Test"
            }
        }
        
        message = MessageSandeco(raw_data)
        
        assert message.scope == "unknown"
        assert message.group_id is None
        assert message.phone is None


if __name__ == "__main__":
    pytest.main([__file__])
