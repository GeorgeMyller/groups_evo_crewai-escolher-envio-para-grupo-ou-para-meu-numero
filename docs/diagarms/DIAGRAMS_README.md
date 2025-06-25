# 📊 Diagramas de Fluxo - Sistema WhatsApp Manager

Este diretório contém scripts para gerar diagramas de fluxo visuais que representam o funcionamento do sistema WhatsApp Manager.

## 🎯 Versões Disponíveis

### 1. **flowchart_diagram_enhanced.py** *(Recomendado)*
Versão melhorada e otimizada do diagrama de fluxo.

**Características:**
- ✨ Ícones SVG personalizados e representativos
- 🎨 Layout vertical organizado em clusters temáticos
- 🔧 **Configuração e Inicialização**
- ✅ **Validação**
- 📊 **Processamento de Dados**
- 🤖 **Geração de Resumo (CrewAI)**
- 📱 **Envio de Mensagens**
- 📝 **Finalização**
- 🌈 Cores temáticas para diferentes seções
- 📐 Melhor espaçamento e legibilidade

### 2. **flowchart_diagram.py** *(Original)*
Versão original baseada nos ícones Base64.

## 🚀 Como Executar

```bash
# Navegar para o diretório de scripts
cd scripts/

# Executar a versão melhorada (recomendado)
/path/to/.venv/bin/python flowchart_diagram_enhanced.py

# Ou executar a versão original
/path/to/.venv/bin/python flowchart_diagram.py
```

## 📁 Arquivos Gerados

### Diagramas PNG
- `flowchart_diagram_enhanced.png` - Diagrama melhorado
- `flowchart_diagram_v6.png` - Diagrama original

### Ícones SVG Personalizados
Salvos no diretório `custom_icons/`:

| Ícone | Arquivo | Descrição |
|-------|---------|-----------|
| 🚀 | `start_task.svg` | Início da tarefa agendada |
| ⚙️ | `env_vars.svg` | Carregamento de variáveis de ambiente |
| 📋 | `arguments.svg` | Argumentos da linha de comando |
| 🔍 | `extract_id.svg` | Extração do ID do grupo |
| 👥 | `group_data.svg` | Dados do grupo |
| ❌ | `error_end.svg` | Fim por erro |
| 📊 | `calculate.svg` | Cálculo de intervalo |
| 💬 | `messages.svg` | Mensagens recuperadas |
| 🔄 | `format.svg` | Formatação para CrewAI |
| 🤖 | `crewai.svg` | Geração de resumo com AI |
| 📱 | `whatsapp.svg` | Envio via WhatsApp |
| ✅ | `success.svg` | Sucesso/Log |
| 🏁 | `end.svg` | Fim do processo |

## 🎨 Fluxo do Sistema

O diagrama representa o fluxo completo do sistema:

1. **Início**: Tarefa agendada é iniciada
2. **Configuração**: Carrega variáveis de ambiente e argumentos
3. **Validação**: Verifica se o grupo existe e tem resumo habilitado
4. **Processamento**: Calcula intervalo, recupera e formata mensagens
5. **IA**: Gera resumo usando CrewAI
6. **Envio**: Envia para grupo e/ou número pessoal (conforme configuração)
7. **Finalização**: Registra sucesso no log

## 🔧 Dependências

O script utiliza a biblioteca `diagrams` para gerar os diagramas:

```bash
# Já incluída no ambiente virtual do projeto
pip install diagrams
```

## 📝 Personalização

### Modificar Cores
Edite os atributos `graph_attr` nos clusters:

```python
with Cluster("🔧 Configuração", graph_attr={"bgcolor": "#e3f2fd", "style": "rounded"}):
    # Seus nodos aqui
```

### Adicionar Novos Ícones
1. Crie o SVG no formato apropriado
2. Use a função `create_svg_icon()`:

```python
NOVO_ICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg">...</svg>'''
novo_icon_path = create_svg_icon("novo_icon.svg", NOVO_ICON_SVG)
```

### Modificar Layout
Ajuste os parâmetros em `graph_attr`:

```python
graph_attr = {
    "splines": "ortho",        # Tipo de conexões
    "rankdir": "TD",           # Direção do fluxo
    "nodesep": "1.2",          # Espaçamento entre nodos
    "ranksep": "1.8",          # Espaçamento entre ranks
    "bgcolor": "#f8f9fa",      # Cor de fundo
}
```

## 📊 Estrutura Visual

O diagrama enhanced utiliza:

- **Clusters temáticos** com cores distintas
- **Ícones representativos** para cada ação
- **Setas coloridas** (verde=sucesso, vermelho=erro, laranja=opcional)
- **Labels descritivos** com emojis
- **Layout vertical** para melhor leitura

## 🎯 Benefícios

- 📈 **Visualização Clara**: Facilita o entendimento do fluxo
- 🔍 **Debugging**: Ajuda a identificar pontos de falha
- 📚 **Documentação**: Serve como documentação visual
- 🎨 **Apresentação**: Ideal para demonstrações e reuniões
- 🔧 **Manutenção**: Facilita modificações futuras no sistema

---

*Gerado automaticamente pelo Sistema WhatsApp Manager* 🤖
