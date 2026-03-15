# 🤖 TikTok Streak Automation Bot

Este projeto consiste em uma automação robusta desenvolvida em **Python** para gerenciar e manter "foguinhos" (streaks) no TikTok de forma totalmente autônoma. O sistema foi projetado para rodar silenciosamente em segundo plano, com um sistema de monitoramento ativo via **Telegram**.

## 🎯 Objetivo
Automatizar a interação diária com contatos específicos, eliminando a tarefa manual e garantindo que os streaks de mensagens não sejam perdidos, utilizando notificações push para manter o usuário informado sobre o status da execução.

## 🚀 Tecnologias e Conceitos Utilizados

- **Python 3.x**: Linguagem base para o desenvolvimento da lógica.
- **Playwright**: Framework de última geração para automação web, permitindo interações rápidas e estáveis com o DOM.
- **Telegram Bot API**: Integração para monitoramento remoto e alertas em tempo real.
- **Dotenv (.env)**: Gerenciamento seguro de variáveis de ambiente para proteção de tokens e IDs.
- **Persistência de Estado**: Uso de `storage_state` para reaproveitamento de sessões, evitando logins repetitivos e desafios de captcha.
- **Windows Task Scheduler**: Integração com o sistema operacional para execução automática no logon.

## 🛠️ Diferenciais Técnicos e Desafios Resolvidos

- **Execução Headless com Viewport Customizado**: O bot opera em modo invisível, mas força uma resolução Full HD (1920x1080) para garantir que o layout responsivo do TikTok não esconda elementos críticos da interface.
- **Arquitetura de Notificação**:
    - ✅ **Sucesso**: Notifica ao concluir os envios diários.
    - ⚠️ **Sessão Expirada**: Alerta caso os cookies percam a validade, solicitando intervenção manual.
    - 🚨 **Erro Fatal**: Captura e envia o Traceback detalhado de qualquer exceção não tratada via Telegram.
- **Segurança da Informação**: Implementação rigorosa de `.gitignore` para impedir o vazamento de credenciais e estados de sessão no controle de versão.

## 📂 Estrutura do Repositório

- `app.py`: O coração da automação e lógica de disparos.
- `.env.example`: Modelo para configuração das chaves de API (o arquivo `.env` original é ignorado por segurança).
- `.gitignore`: Filtro de segurança para arquivos sensíveis e ambiente virtual.
- `rodar_bot.bat`: Script de automação para inicialização do ambiente e execução do script Python.

## 🔧 Como Replicar

1. **Clone o repositório:**
   ```bash
    git clone https://github.com/NickolasFerraz1/Fogo-TikTok.git

2. **Configure o Ambiente:**
    ```bash
    python -m venv venv
    source venv/Scripts/activate # No Windows: venv\Scripts\activate
    pip install playwright python-dotenv requests
    playwright install chromium
   ```
3. **Variáveis de Ambiente:**
   Crie um arquivo `.env` e preencha com seu `TOKEN_TELEGRAM` e `CHAT_ID_TELEGRAM`.

---

Desenvolvido por Nickolas como projeto de portfólio em Automação e Engenharia de Software.

---
