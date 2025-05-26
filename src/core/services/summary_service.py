"""
Gerador de Resumos com CrewAI / CrewAI Summary Generator

PT-BR:
Esta classe utiliza a biblioteca CrewAI para criar resumos inteligentes de conversas
do WhatsApp, organizando o conteúdo em seções relevantes e garantindo uma apresentação
clara e estruturada.

EN:
This class uses the CrewAI library to create intelligent summaries of WhatsApp
conversations, organizing content into relevant sections and ensuring clear,
structured presentation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

from config.settings import Settings
from src.core.models import SummaryRequest, SummaryResult, MessageData
from exceptions import SummaryGenerationError
from structured_logger import get_logger

logger = get_logger(__name__)

class SummaryService:
    def __init__(self, settings: Optional[Settings] = None):
        """
        PT-BR:
        Inicializa o gerador de resumos.
        Configura o modelo de linguagem e cria a equipe de agentes.

        EN:
        Initializes the summary generator.
        Sets up the language model and creates the agent crew.
        """
        try:
            self.settings = settings or Settings()
            load_dotenv()
            self.llm = self.settings.llm_model or "gemini/gemini-2.0-flash"
            self.create_crew()
            logger.info("SummaryService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SummaryService: {e}")
            raise SummaryGenerationError(f"Summary service initialization failed: {e}")

    def create_crew(self):
        """
        PT-BR:
        Configura o agente de IA e sua tarefa.
        Define o comportamento e objetivos do assistente de resumos,
        incluindo o template de formatação e regras de processamento.

        EN:
        Sets up the AI agent and its task.
        Defines the behavior and goals of the summary assistant,
        including formatting template and processing rules.
        """
        try:
            # Agent Configuration / Configuração do Agente
            self.agent = Agent(
                role="Assistente de Resumos / Summary Assistant",
                goal="Criar resumos organizados e objetivos de mensagens de WhatsApp / Create organized and objective summaries of WhatsApp messages",
                backstory=(
                    "Você é um assistente de IA especializado em analisar e organizar informações "
                    "de conversas de WhatsApp. Sua função é identificar os tópicos principais, "
                    "eventos importantes e informações relevantes, apresentando-os de forma clara e estruturada. "
                    "Você sempre mantém o contexto cultural brasileiro e adapta o conteúdo conforme necessário.\n\n"
                    "You are an AI assistant specialized in analyzing and organizing WhatsApp conversation information. "
                    "Your role is to identify main topics, important events, and relevant information, "
                    "presenting them in a clear and structured way. You always maintain Brazilian cultural context "
                    "and adapt content as needed."
                ),
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            )

            # Task Template / Template da Tarefa
            self.task_template = (
                "Analise as seguintes mensagens de WhatsApp e crie um resumo organizado:\n\n"
                "MENSAGENS:\n{messages}\n\n"
                "INSTRUÇÕES:\n"
                "1. Identifique os principais tópicos discutidos\n"
                "2. Destaque eventos, decisões ou informações importantes\n"
                "3. Mantenha o contexto e o tom das conversas\n"
                "4. Organize o conteúdo em seções lógicas\n"
                "5. Use formatação em markdown para melhor legibilidade\n"
                "6. Inclua apenas informações relevantes e evite repetições\n"
                "7. Se houver links importantes, liste-os separadamente se solicitado\n"
                "8. Mantenha um tom profissional mas amigável\n\n"
                "FORMATO ESPERADO:\n"
                "## 📋 Resumo do Grupo\n\n"
                "### 🎯 Principais Tópicos\n"
                "- [Liste os tópicos principais]\n\n"
                "### 📌 Destaques Importantes\n"
                "- [Eventos, decisões, informações relevantes]\n\n"
                "### 💬 Atividade do Grupo\n"
                "- Total de mensagens analisadas: {message_count}\n"
                "- Período: {start_date} até {end_date}\n\n"
                "### 🔗 Links Importantes\n"
                "[Apenas se solicitado e se houver links relevantes]\n\n"
                "---\n"
                "*Resumo gerado automaticamente em {generation_time}*"
            )
            
            logger.info("CrewAI agent and task template configured")
            
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            raise SummaryGenerationError(f"Crew creation failed: {e}")

    def generate_summary(self, request: SummaryRequest, messages: List[MessageData]) -> SummaryResult:
        """
        PT-BR:
        Gera um resumo das mensagens usando CrewAI.
        
        EN:
        Generates a summary of messages using CrewAI.
        """
        try:
            if not messages:
                raise SummaryGenerationError("No messages provided for summary")
            
            if len(messages) < request.min_messages:
                raise SummaryGenerationError(
                    f"Insufficient messages for summary. Required: {request.min_messages}, "
                    f"Available: {len(messages)}"
                )
            
            logger.info(f"Generating summary for group {request.group_id} with {len(messages)} messages")
            
            # Prepare message text
            message_text = self._format_messages_for_summary(messages, request)
            
            # Determine date range
            start_date = min(msg.sent_date for msg in messages)
            end_date = max(msg.sent_date for msg in messages)
            
            # Create task
            task_description = self.task_template.format(
                messages=message_text,
                message_count=len(messages),
                start_date=start_date.strftime("%d/%m/%Y %H:%M"),
                end_date=end_date.strftime("%d/%m/%Y %H:%M"),
                generation_time=datetime.now().strftime("%d/%m/%Y às %H:%M")
            )
            
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="Um resumo estruturado em markdown seguindo o formato especificado"
            )
            
            # Execute with Crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            summary_text = str(result)
            
            # Create result object
            summary_result = SummaryResult(
                group_id=request.group_id,
                group_name=f"Group {request.group_id}",  # Should be passed from controller
                summary_text=summary_text,
                message_count=len(messages),
                period_start=start_date,
                period_end=end_date
            )
            
            logger.info(f"Summary generated successfully for group {request.group_id}")
            return summary_result
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise SummaryGenerationError(f"Summary generation failed: {e}")
    
    def _format_messages_for_summary(self, messages: List[MessageData], request: SummaryRequest) -> str:
        """
        PT-BR:
        Formata as mensagens para análise do LLM.
        
        EN:
        Formats messages for LLM analysis.
        """
        try:
            formatted_messages = []
            
            for msg in messages:
                timestamp = msg.sent_date.strftime("%d/%m/%Y %H:%M")
                
                # Format sender name if requested
                if request.include_names:
                    sender = msg.sender
                else:
                    sender = "Usuário"
                
                # Process content for links if requested
                content = msg.content
                if not request.include_links:
                    # Remove or replace links
                    import re
                    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                                   '[link removido]', content)
                
                formatted_messages.append(f"[{timestamp}] {sender}: {content}")
            
            return "\n".join(formatted_messages)
            
        except Exception as e:
            logger.error(f"Failed to format messages: {e}")
            raise SummaryGenerationError(f"Message formatting failed: {e}")
    
    def validate_summary_request(self, request: SummaryRequest) -> bool:
        """
        PT-BR:
        Valida uma requisição de resumo.
        
        EN:
        Validates a summary request.
        """
        try:
            # Request validation is handled by Pydantic model
            # Additional business logic validation can be added here
            
            if request.days_back > 30:
                raise ValueError("Days back cannot exceed 30")
            
            if request.min_messages > 1000:
                raise ValueError("Minimum messages cannot exceed 1000")
            
            return True
            
        except Exception as e:
            logger.error(f"Summary request validation failed: {e}")
            raise SummaryGenerationError(f"Request validation failed: {e}")
    
    def get_summary_stats(self, messages: List[MessageData]) -> Dict[str, Any]:
        """
        PT-BR:
        Retorna estatísticas das mensagens para resumo.
        
        EN:
        Returns message statistics for summary.
        """
        try:
            if not messages:
                return {
                    'total_messages': 0,
                    'unique_senders': 0,
                    'date_range': None,
                    'message_types': {}
                }
            
            unique_senders = len(set(msg.sender for msg in messages))
            start_date = min(msg.sent_date for msg in messages)
            end_date = max(msg.sent_date for msg in messages)
            
            # Count message types
            message_types = {}
            for msg in messages:
                msg_type = msg.message_type
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
            
            return {
                'total_messages': len(messages),
                'unique_senders': unique_senders,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'message_types': message_types
            }
            
        except Exception as e:
            logger.error(f"Failed to get summary stats: {e}")
            return {
                'total_messages': 0,
                'unique_senders': 0,
                'date_range': None,
                'message_types': {},
                'error': str(e)
            }
