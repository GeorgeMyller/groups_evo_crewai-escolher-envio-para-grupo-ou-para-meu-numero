# Guia de Gerenciamento via Portainer 🐳

Este guia fornece instruções detalhadas sobre como gerenciar o aplicativo WhatsApp Group Resumer utilizando o Portainer, uma interface gráfica para Docker.

## O que é o Portainer?

O Portainer é uma solução leve de gerenciamento para Docker que permite administrar facilmente seus containers, imagens, redes e volumes através de uma interface web amigável. Em vez de usar comandos de terminal, você pode realizar a maioria das tarefas com alguns cliques.

## Pré-requisitos

- Raspberry Pi com Docker instalado
- Portainer já instalado e rodando (geralmente na porta 9000)
- Acesso à interface web do Portainer

## Instalação do Portainer (se ainda não estiver instalado)

Se você ainda não tem o Portainer instalado no seu Raspberry Pi, execute o seguinte comando:

```sh
ssh pi@192.168.1.205 "docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest"
```

Após a instalação, acesse `http://192.168.1.205:9000` e defina uma senha de administrador.

## Implantação do Aplicativo via Portainer

### 1. Preparação dos Arquivos

Primeiro, transfira os arquivos necessários para o Raspberry Pi:

```sh
# Configure as variáveis de ambiente
./setup_raspberry_env.sh

# Transfira os arquivos para o Raspberry Pi
./deploy_compose_to_raspberry.sh
```

### 2. Acesso ao Portainer

1. Abra seu navegador e acesse: `http://192.168.1.205:9000`
2. Faça login com suas credenciais do Portainer

### 3. Criação de um Stack

Um "Stack" no Portainer é equivalente a um projeto Docker Compose.

1. No menu lateral, clique em **Stacks**
2. Clique no botão **+ Add stack**
3. Preencha o formulário:
   - **Name**: `whatsapp-summarizer`
   - **Build method**: Escolha uma das opções:
     - **Web editor**: Para digitar ou colar o código do docker-compose.yml
     - **Upload**: Para fazer upload do arquivo docker-compose.yml
     - **Repository**: Para buscar de um repositório Git
4. Para usar o web editor:
   - Acesse o Raspberry Pi via SSH
   - Copie o conteúdo do arquivo docker-compose.yml:
     ```sh
     ssh pi@192.168.1.205 "cat ~/whatsapp-summarizer/docker-compose.yml"
     ```
   - Cole o conteúdo no editor
5. Clique em **Deploy the stack**

## Gerenciamento do Aplicativo

### Visualizar e Gerenciar Containers

1. No menu lateral, clique em **Containers**
2. Você verá uma lista com todos os containers em execução
3. Para cada container, você pode:
   - Ver o status (rodando, parado, etc.)
   - Ver o uso de CPU e memória
   - Acessar ações rápidas (parar, reiniciar, remover)

### Ações com o Container

Ao clicar em um container específico, você terá acesso a diversas opções:

1. **Logs**: Visualize os logs em tempo real
2. **Stats**: Monitore o uso de recursos
3. **Console**: Acesse o terminal do container
4. **Inspect**: Veja informações detalhadas do container
5. **Restart/Stop/Kill**: Gerencie o estado do container

### Atualização do Aplicativo

Para atualizar o aplicativo após mudanças no código:

1. Vá até o menu **Stacks**
2. Encontre o stack "whatsapp-summarizer"
3. Clique no botão de edição (ícone de lápis)
4. Atualize o conteúdo do docker-compose.yml se necessário
5. Clique em **Update the stack**

## Dicas de Uso

### Monitoramento de Recursos

O Portainer permite monitorar o uso de recursos de forma visual:

1. Acesse o container do aplicativo
2. Clique na aba **Stats**
3. Você verá gráficos em tempo real do uso de CPU, memória e rede

### Backup de Configurações

Para fazer backup das configurações do aplicativo:

1. Vá em **Volumes**
2. Localize o volume usado pelo aplicativo
3. Use a opção **Browse** para explorar os arquivos
4. Faça download dos arquivos importantes como `.env` ou dados persistentes

### Resolução de Problemas

Se o aplicativo apresentar problemas:

1. Verifique os **Logs** do container para identificar erros
2. Use o **Console** para acessar o terminal do container e executar comandos de diagnóstico
3. Verifique se as variáveis de ambiente estão configuradas corretamente (usando a aba **Inspect**)

## Conclusão

O Portainer facilita significativamente o gerenciamento da sua aplicação Docker, oferecendo uma interface visual intuitiva que elimina a necessidade de memorizar comandos Docker complexos. Use-o para monitorar, manter e solucionar problemas do seu aplicativo WhatsApp Group Resumer de forma eficiente.
