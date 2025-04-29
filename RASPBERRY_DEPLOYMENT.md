# Implantação no Raspberry Pi com Docker 🚀

Este guia explica como implantar o sistema de gerenciamento e resumo de grupos do WhatsApp em um Raspberry Pi usando Docker.

## Pré-requisitos

### No Raspberry Pi
- Raspberry Pi com Raspberry Pi OS (anteriormente Raspbian) instalado
- Docker e Docker Compose instalados
- Acesso SSH habilitado
- Conexão à mesma rede que seu computador de desenvolvimento

### No computador de desenvolvimento
- Docker instalado
- Acesso SSH ao Raspberry Pi

## Opções de implantação

Existem três maneiras de implantar este aplicativo no Raspberry Pi:

1. **Método com imagem Docker** - Constrói a imagem localmente e a transfere
2. **Método com Docker Compose** - Transfere os arquivos fonte e constrói no Raspberry Pi
3. **Método com Portainer** - Usa a interface gráfica do Portainer para gerenciar a implantação

Escolha o método que melhor se adapta ao seu caso.

## Método 1: Implantação com imagem Docker

### 1. Preparar o ambiente no Raspberry Pi

Execute o script de configuração de ambiente para criar o arquivo de variáveis de ambiente no Raspberry Pi:

```sh
# Tornar o script executável
chmod +x setup_raspberry_env.sh

# Executar o script
./setup_raspberry_env.sh
```

Em seguida, conecte-se ao Raspberry Pi e edite o arquivo de variáveis de ambiente com suas credenciais reais:

```sh
ssh pi@192.168.1.205
nano ~/.whatsapp_env
```

### 2. Construir e implantar o aplicativo

Execute o script de implantação para construir a imagem Docker, transferi-la para o Raspberry Pi e iniciar o container:

```sh
# Tornar o script executável
chmod +x deploy_to_raspberry.sh

# Executar o script
./deploy_to_raspberry.sh
```

## Método 2: Implantação com Docker Compose

Este método é mais direto e recomendado para a maioria dos casos:

```sh
# Tornar o script executável
chmod +x deploy_compose_to_raspberry.sh

# Executar o script
./deploy_compose_to_raspberry.sh
```

O script irá:
1. Criar um diretório no Raspberry Pi
2. Transferir os arquivos necessários
3. Configurar o ambiente
4. Construir e iniciar o container usando Docker Compose

## Método 3: Implantação com Portainer

Se você já tem o Portainer instalado no seu Raspberry Pi, pode usá-lo para implantar e gerenciar o aplicativo através da interface gráfica.

### 1. Preparar os arquivos

Execute o script para configurar o ambiente e transferir os arquivos necessários:

```sh
# Tornar o script executável
chmod +x setup_raspberry_env.sh

# Executar o script para configurar as variáveis de ambiente
./setup_raspberry_env.sh

# Transferir arquivos para o Raspberry Pi
./deploy_compose_to_raspberry.sh
```

### 2. Acessar o Portainer

1. Acesse o Portainer no seu navegador:
   ```
   http://192.168.1.205:9000
   ```

2. Faça login com suas credenciais.

### 3. Implantar o aplicativo

1. Selecione seu ambiente local na página inicial do Portainer.

2. Navegue até **Stacks** no menu lateral.

3. Clique em **+ Add stack**.

4. Configure o stack:
   - **Name**: `whatsapp-summarizer`
   - **Build method**: Selecione "Upload docker-compose.yml file" ou "Web editor"
   
5. Para o Web editor, acesse o Raspberry Pi via SSH, copie o conteúdo do arquivo docker-compose.yml:
   ```sh
   ssh pi@192.168.1.205 "cat ~/whatsapp-summarizer/docker-compose.yml"
   ```
   
6. Cole o conteúdo no editor do Portainer.

7. Se necessário, ajuste o arquivo docker-compose.yml (principalmente o caminho do env_file).

8. Clique em **Deploy the stack**.

9. O Portainer construirá e iniciará automaticamente o container.

### 4. Gerenciar o aplicativo via Portainer

No Portainer, você pode:

- **Visualizar logs** do container
- **Iniciar, parar, reiniciar** o aplicativo
- **Acessar o terminal** do container se necessário
- **Monitorar o uso de recursos**
- **Visualizar variáveis de ambiente**

## Acesso ao aplicativo

Após a implantação bem-sucedida, você pode acessar o aplicativo em um navegador web:

```
http://192.168.1.205:8501
```

## Gerenciamento do container no Raspberry Pi

### Para implantação com imagem Docker:

```sh
# Verificar o status
ssh pi@192.168.1.205 "docker ps"

# Reiniciar o aplicativo
ssh pi@192.168.1.205 "docker restart whatsapp-summarizer"

# Ver logs
ssh pi@192.168.1.205 "docker logs whatsapp-summarizer"

# Parar o aplicativo
ssh pi@192.168.1.205 "docker stop whatsapp-summarizer"
```

### Para implantação com Docker Compose:

```sh
# Conectar ao Raspberry Pi
ssh pi@192.168.1.205

# Navegar até o diretório do projeto
cd whatsapp-summarizer

# Verificar o status
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar o aplicativo
docker-compose restart

# Parar o aplicativo
docker-compose down

# Atualizar e reiniciar (após alterações)
docker-compose up -d --build
```

### Para implantação com Portainer:

Todas as operações de gerenciamento podem ser realizadas através da interface web do Portainer:

1. Acesse `http://192.168.1.205:9000` e faça login
2. Selecione o ambiente local
3. Navegue até **Containers** ou **Stacks**
4. Use os botões da interface para:
   - Iniciar/parar containers
   - Visualizar logs
   - Reiniciar services
   - Atualizar stacks
   - Remover containers ou stacks

## Solução de problemas

1. **Problema de acesso à API do WhatsApp**: Verifique as variáveis de ambiente no arquivo `.env` ou `~/.whatsapp_env` no Raspberry Pi.

2. **Container não inicia**: Verifique os logs do Docker para identificar o problema.

3. **Erro de permissão**: Certifique-se de que os scripts têm permissão de execução:
   ```sh
   chmod +x *.sh
   ```

4. **Aplicativo inacessível**: Verifique se a porta 8501 está aberta no Raspberry Pi:
   ```sh
   ssh pi@192.168.1.205 "sudo netstat -tulpn | grep 8501"
   ```

5. **Problemas com o Portainer**: 
   - Verifique se o serviço Portainer está rodando:
     ```sh
     ssh pi@192.168.1.205 "docker ps | grep portainer"
     ```
   - Se necessário, reinicie o Portainer:
     ```sh
     ssh pi@192.168.1.205 "docker restart portainer"
     ```
   - Se o Portainer não estiver instalado ou estiver corrompido, você pode reinstalá-lo:
     ```sh
     ssh pi@192.168.1.205 "docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest"
     ```
