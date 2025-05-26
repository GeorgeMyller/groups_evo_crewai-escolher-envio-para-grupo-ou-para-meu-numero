\
#!/bin/sh
# load_env.sh
# Carrega variáveis do .env e executa o comando passado como argumento

# Navega para o diretório do aplicativo onde .env está localizado
cd /app

# Exporta as variáveis do .env para o ambiente atual
export $(grep -v '^#' .env | xargs)

# Executa o comando original passado para este script
exec "$@"
