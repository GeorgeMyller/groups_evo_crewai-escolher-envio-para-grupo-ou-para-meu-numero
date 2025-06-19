"""
Módulo para sumarização de mensagens de grupos - versão leve sem crewai
"""

import re
from typing import List

def clean_text(text: str) -> str:
    """Remove caracteres especiais, links e outros elementos indesejados"""
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove emojis e caracteres especiais
    text = re.sub(r'[^\w\s]', '', text)
    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def summarize_messages(messages: List[str], max_length: int = 100) -> str:
    """
    Versão leve de sumarização que não usa crewai.
    Retorna as primeiras max_length palavras das mensagens.
    """
    if not messages:
        return "Não há mensagens para sumarizar."
    
    # Juntar todas as mensagens
    all_text = " ".join([clean_text(msg) for msg in messages])
    
    # Obter as primeiras palavras
    words = all_text.split()
    if len(words) <= max_length:
        return all_text
    
    # Retornar as primeiras max_length palavras
    summary = " ".join(words[:max_length]) + "..."
    
    return summary

def summarize_by_topic(messages: List[str]) -> dict:
    """
    Versão simplificada de sumarização por tópico sem IA.
    Apenas conta ocorrências de palavras e retorna as mais frequentes.
    """
    if not messages:
        return {"Sem mensagens": "Nenhuma mensagem encontrada"}
    
    # Processar todas as mensagens
    all_text = " ".join([clean_text(msg.lower()) for msg in messages])
    
    # Separar em palavras
    words = all_text.split()
    
    # Remover palavras comuns (stop words em português)
    stop_words = {'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 
                 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 
                 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 
                 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 
                 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 
                 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 
                 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 
                 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 
                 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 
                 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 
                 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 
                 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 
                 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 
                 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 
                 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 
                 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 
                 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 
                 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 
                 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 
                 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 
                 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 
                 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 
                 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 
                 'terão', 'teria', 'teríamos', 'teriam'}
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Contar frequência das palavras
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Pegar as 5 palavras mais frequentes
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Criar resumo simples baseado nas palavras mais frequentes
    topics = {}
    for word, freq in top_words:
        topics[word.capitalize()] = f"Mencionado {freq} vezes"
    
    if not topics:
        topics["Geral"] = "Não foi possível identificar tópicos claros nas mensagens."
    
    return topics
