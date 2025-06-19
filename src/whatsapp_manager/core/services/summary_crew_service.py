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
import os
from typing import Dict, Any, Optional

# Third-party library imports
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# Define PROJECT_ROOT dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


class SummaryCrewService:
    """
    CrewAI-based summary generation service following Clean Architecture principles.
    """
    
    def __init__(self, llm_model: Optional[str] = None):
        """
        PT-BR:
        Inicializa o gerador de resumos.
        Configura o modelo de linguagem e cria a equipe de agentes.

        EN:
        Initializes the summary generator.
        Sets up the language model and creates the agent crew.
        """
        # Load environment variables
        env_path = os.path.join(PROJECT_ROOT, '.env')
        load_dotenv(env_path, override=True)
        
        # Configure LLM
        self.llm = llm_model or os.getenv('LLM_MODEL', "gemini/gemini-2.0-flash")
        
        # Initialize crew components
        self._create_crew()

    def _create_crew(self) -> None:
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
        # Agent Configuration / Configuração do Agente
        self.agent = Agent(
            role="Assistente de Resumos / Summary Assistant",
            goal="Criar resumos organizados e objetivos de mensagens de WhatsApp / Create organized and objective summaries of WhatsApp messages",
            backstory=(
                "Você é um assistente de IA especializado em analisar e organizar informações "
                "extraídas de mensagens de WhatsApp, garantindo clareza e objetividade. / "
                "You are an AI assistant specialized in analyzing and organizing information "
                "extracted from WhatsApp messages, ensuring clarity and objectivity."
            ),
            verbose=True,
            llm=self.llm
        )

        # Task Definition / Definição da Tarefa
        self.task = Task(
            description=self._get_task_description(),
            expected_output=(
                "Um resumo segmentado seguindo o template, contendo apenas informações relevantes. / "
                "A segmented summary following the template, containing only relevant information."
            ),
            agent=self.agent,
        )

        # Crew Setup / Configuração da Equipe
        self.crew = Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential,
        )

    def _get_task_description(self) -> str:
        """
        Returns the comprehensive task description template.
        """
        return r"""
PT-BR:
Você é um assistente especializado em criar resumos organizados de conversas do WhatsApp.
Seu objetivo é apresentar as informações de forma clara e segmentada, seguindo o modelo abaixo.

EN:
You are an assistant specialized in creating organized summaries of WhatsApp conversations.
Your goal is to present information clearly and in logical segments, following the template below.

Estrutura do Template / Template Structure
------------------------------------------
Resumo do Grupo 📝 (Data ou Período / Date or Period):
- Tópico Principal / Main Topic <Emoji> – Horário / Time
- Participantes / Participants: <Names>
- Resumo / Summary: <Description>

Dúvidas, Erros e Soluções / Questions, Errors & Solutions ❓ (Horário / Time):
- Solicitado por / Requested by: <Name>
- Respondido por / Answered by: <Names>
- Resumo / Summary: <Description>

Resumo Geral do Período / Period Overview 📊:
- <General summary>

Links do Dia / Daily Links 🔗:
- <Important links with context>

Conclusão / Conclusion 🔚:
- <Insights sobre o ambiente do grupo ou produtividade da interação / Group insights and productivity>

Mensagens para análise / Messages for analysis:
<msgs>
{msgs}
</msgs>
        """

    def generate_summary(self, messages: str) -> str:
        """
        PT-BR:
        Executa o processo de geração do resumo.
        
        Parâmetros:
            messages (str): Mensagens do WhatsApp para processar
            
        Retorna:
            str: Resumo formatado seguindo o template

        EN:
        Executes the summary generation process.
        
        Parameters:
            messages (str): WhatsApp messages to process
            
        Returns:
            str: Formatted summary following the template
        """
        try:
            inputs = {"msgs": messages}
            result = self.crew.kickoff(inputs=inputs).raw
            
            # Clean up result - remove 'text' prefix if present
            if result.strip().startswith('text'):
                result = result.strip()[4:].lstrip('\n: ')
                
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e

    def kickoff(self, inputs: Dict[str, Any]) -> str:
        """
        Legacy method for backward compatibility.
        
        Parameters:
            inputs (dict): Input data containing messages
            
        Returns:
            str: Generated summary
        """
        messages = inputs.get("msgs", "")
        return self.generate_summary(messages)
