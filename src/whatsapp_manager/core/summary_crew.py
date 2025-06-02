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
import os # For PROJECT_ROOT

# Third-party library imports
from dotenv import load_dotenv
from crewai import Agent
from crewai import Task
from crewai import Crew
from crewai import Process
from crewai import LLM


# Define Project Root assuming this file is src/whatsapp_manager/core/summary_crew.py
# Navigate three levels up to reach the project root from core.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class SummaryCrew:
    def __init__(self):
        """
        PT-BR:
        Inicializa o gerador de resumos.
        Configura o modelo de linguagem e cria a equipe de agentes.

        EN:
        Initializes the summary generator.
        Sets up the language model and creates the agent crew.
        """
        env_path = os.path.join(PROJECT_ROOT, '.env')
        load_dotenv(env_path, override=True) # Explicitly load .env from project root
        self.llm = "gemini/gemini-2.0-flash" # This might need to be an environment variable
        self.create_crew()

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
            memory=False,
            llm=self.llm
        )

        # Task Definition / Definição da Tarefa
        self.task = Task(
            description=r"""
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
            """,
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

    def kickoff(self, inputs):
        """
        PT-BR:
        Executa o processo de geração do resumo.
        
        Parâmetros:
            inputs (str): Mensagens do WhatsApp para processar
            
        Retorna:
            str: Resumo formatado seguindo o template

        EN:
        Executes the summary generation process.
        
        Parameters:
            inputs (str): WhatsApp messages to process
            
        Returns:
            str: Formatted summary following the template
        """
        result = self.crew.kickoff(inputs=inputs).raw
        # Remove 'text' do início, se existir
        if result.strip().startswith('text'):
            result = result.strip()[4:].lstrip('\n: ')
        return result
    

