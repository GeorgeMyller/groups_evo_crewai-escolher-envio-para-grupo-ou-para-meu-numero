# MANUAL_DEV.md

## 1. Scripts de Manutenção em `fixes`

A pasta `scripts/fixes/` contém scripts utilitários para manutenção e ajustes na estrutura do projeto, como correção de imports, caminhos de arquivos e organização de diretórios. Para executar um script de manutenção:

```sh
python3 scripts/fixes/<nome_do_script>.py
```

- Consulte o arquivo `FIXES_COMPLETED.md` para ver quais correções já foram aplicadas.
- Use esses scripts sempre que houver mudanças estruturais ou problemas de compatibilidade entre ambientes.

## 2. Modo Offline

O sistema possui um modo offline para operar sem conexão com APIs externas. Esse modo é útil para testes locais, demonstrações ou quando a API está indisponível.

- O modo offline pode ser ativado por variável de ambiente ou parâmetro de configuração (verifique os docstrings dos scripts principais para detalhes).
- No modo offline, dados simulados são usados em vez de chamadas reais à API.
- Útil para desenvolvimento, debugging e testes sem dependências externas.

## 3. Rodando os Testes

Os testes estão localizados na pasta `tests/`. Para rodar todos os testes:

```sh
python3 -m unittest discover tests
```

### Descrição dos principais scripts de teste:
- `test_alternative_urls.py`: Testa URLs alternativas da API.
- `test_api_connectivity.py`: Verifica a conectividade com a API principal.
- `test_api_detailed.py`: Testes detalhados de endpoints e respostas da API.
- `test_check_api_status.py`: Checa o status geral da API.
- `test_connect_whatsapp.py`: Testa a conexão com o WhatsApp.
- `test_connection.py`: Testa conexões básicas do sistema.
- `test_imports_and_functionality.py`: Valida imports e funcionalidades principais.
- `test_offline_mode.py`: Testa o funcionamento do modo offline.
- `test_structure.py`: Verifica a estrutura de arquivos e diretórios.
- `test_validate_migration.py`: Testa migrações e compatibilidade de dados.
- `test_whatsapp_status.py`: Checa o status do WhatsApp.

## 4. Fallback de Caminhos de Arquivos

O sistema implementa fallback de caminhos para garantir que arquivos essenciais (como caches, CSVs e configs) sejam encontrados mesmo se movidos ou reestruturados:
- Os módulos utilitários buscam arquivos em múltiplos diretórios padrão (ex: `data/`, `src/whatsapp_manager/core/`, etc).
- Se um arquivo não for encontrado no caminho principal, o sistema tenta localizar em caminhos alternativos.
- Isso facilita a portabilidade e manutenção do projeto entre diferentes ambientes.

## 5. Dicas Rápidas para Desenvolvedores

- **Estrutura:**
  - Scripts principais: `src/whatsapp_manager/core/`
  - Interface web: `src/whatsapp_manager/ui/`
  - Utilitários: `src/whatsapp_manager/utils/`
  - Dados e caches: `data/`
  - Scripts de manutenção: `scripts/fixes/`
  - Testes: `tests/`
- **Entry points:**
  - CLI: scripts em `src/whatsapp_manager/core/` e `scripts/`
  - Web: consulte o `README.md` para execução via Docker
- **Principais módulos:**
  - `group_controller.py`, `summary.py`, `task_scheduler.py`, `groups_util.py`
- **Dica:** Sempre consulte os docstrings e comentários dos scripts para detalhes de uso e parâmetros.

---

**Atualizado em: 20/06/2025**
