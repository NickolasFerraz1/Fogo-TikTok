import os
import time
import logging
import sys
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Console do Windows costuma usar cp1252, que não representa emojis.
# Sem isso, todo log com emoji dispara UnicodeEncodeError no console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_TELEGRAM = os.getenv("CHAT_ID_TELEGRAM")

# 1. CONFIGURAÇÃO DO MONITORAMENTO
def setup_logger():
    logger = logging.getLogger("FogoTikTok")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler('logs_execucao.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Rodando via pythonw.exe (sem console, para o agendamento diário
    # não abrir janela de terminal) sys.stdout é None, então o handler
    # de console precisa ser pulado nesse caso.
    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

# 1.1 NOTIFICAÇÃO VIA TELEGRAM
def enviar_aviso_telegram(mensagem):
    if not TOKEN_TELEGRAM or not CHAT_ID_TELEGRAM:
        logger.warning("⚠️ TOKEN_TELEGRAM/CHAT_ID_TELEGRAM não configurados no .env — pulando notificação.")
        return
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        resposta = requests.post(url, json={"chat_id": CHAT_ID_TELEGRAM, "text": mensagem}, timeout=10)
        resposta.raise_for_status()
    except Exception as e:
        logger.warning(f"⚠️ Falha ao enviar aviso pro Telegram: {e}")

# 2. FUNÇÃO DE LIMPEZA DE POPUPS (Versão Robusta)
def fechar_popups_e_esperar(page):
    logger.info("⏳ Aguardando estabilização e limpando sobreposições...")
    page.wait_for_timeout(5000)
    
    textos_alvo = ["Talvez mais tarde", "Mais tarde", "Agora não", "Not now"]
    
    for texto in textos_alvo:
        try:
            # Busca específica por botão para evitar cliques em textos de fundo
            botao = page.get_by_role("button", name=texto, exact=False)
            
            if botao.is_visible():
                logger.info(f"🎯 Botão '{texto}' detectado. Tentando clicar...")
                botao.click(force=True, timeout=5000)
                logger.info(f"🛡️ Popup '{texto}' removido com sucesso.")
                page.wait_for_timeout(2000)
                return 
        except Exception:
            continue
    
    logger.debug("Siga em frente: Nenhum popup impeditivo detectado.")

# 3. FUNÇÃO DE BUSCA DE CONTATO (Lógica de Produção)
def buscar_e_abrir_conversa(page, nome_contato):
    try:
        logger.info(f"🔎 Localizando conversa com: {nome_contato}")

        # O TikTok removeu o campo de busca dessa tela de mensagens.
        # Como o bot roda diariamente, os contatos alvo sempre aparecem
        # entre as conversas recentes na lista lateral, então clicamos
        # direto no nome em vez de tentar buscar.
        # OBS: existe um <a aria-label="Perfil de ..."> oculto no DOM com
        # o mesmo texto (usado só pra acessibilidade/preview), então não
        # dá pra confiar em ".first" puro — é preciso pular os ocultos.
        candidatos = page.get_by_text(nome_contato, exact=False)
        candidatos.first.wait_for(state="attached", timeout=10000)

        item_contato = None
        for candidato in candidatos.all():
            if candidato.is_visible():
                item_contato = candidato
                break

        if item_contato is None:
            raise Exception("Contato não apareceu (visível) na lista de conversas.")

        item_contato.click()

        logger.info(f"✅ Conversa com {nome_contato} aberta!")
        page.wait_for_timeout(1000) # Estabilização após abrir a conversa
        return True

    except Exception as e:
        logger.warning(f"⚠️ Falha ao processar {nome_contato}: {e}")
        # Tira print do erro específico do contato
        page.screenshot(path=f"erro_busca_{nome_contato}.png")
        return False

# 3.1 FUNÇÃO DE ENVIO DO FOGUINHO
def enviar_foguinho(page, nome_contato):
    try:
        caixa_texto = page.get_by_placeholder("Enviar mensagem", exact=False).first
        if not caixa_texto.is_visible():
            caixa_texto = page.locator('div[contenteditable="true"]').first

        caixa_texto.click()
        page.wait_for_timeout(1000)
        page.keyboard.type("🔥")
        page.wait_for_timeout(1000)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        logger.info(f"🔥 Foguinho enviado para {nome_contato}!")
        return True

    except Exception as e:
        logger.warning(f"⚠️ Falha ao enviar foguinho para {nome_contato}: {e}")
        page.screenshot(path=f"erro_envio_{nome_contato}.png")
        return False

# 4. FLUXO PRINCIPAL
def rodar_bot_tiktok():
    CAMINHO_ESTADO = "estado_tiktok.json"
    NOMES_PARA_ENVIAR = ["Heloísa Biazotti", "Enzo Carvalho", "Otávio Gasque"]
    
    # Viewport fixo em Full HD: headless usa um viewport pequeno por padrão,
    # o que esconde elementos da lista de mensagens no layout responsivo do TikTok.
    VIEWPORT = {"width": 1920, "height": 1080}

    with sync_playwright() as p:
        browser = None
        try:
            logger.info("🔥 Iniciando o motor do Chromium...")
            browser = p.chromium.launch(headless=True)

            # Carregamento da Sessão
            if os.path.exists(CAMINHO_ESTADO):
                logger.info(f"📂 Arquivo de estado encontrado! Carregando sessão...")
                context = browser.new_context(storage_state=CAMINHO_ESTADO, viewport=VIEWPORT)
            else:
                logger.warning(f"⚠️ {CAMINHO_ESTADO} NÃO ENCONTRADO!")
                context = browser.new_context(viewport=VIEWPORT)

            page = context.new_page()

            # Navegação
            logger.info("🌐 Navegando para as mensagens...")
            page.goto("https://www.tiktok.com/messages", wait_until="networkidle")

            # Sessão expirada: o TikTok redireciona pra tela de login
            if "login" in page.url:
                logger.warning("⚠️ Sessão expirada! Redirecionado para a tela de login.")
                enviar_aviso_telegram(
                    "⚠️ ALERTA: A sessão do TikTok expirou! Rode o script-login.py de novo para gerar um novo estado_tiktok.json."
                )
                return

            # Limpeza de Popups (PIN, Notificações, etc)
            fechar_popups_e_esperar(page)

            # Loop de Busca
            logger.info(f"🚀 Iniciando processamento de {len(NOMES_PARA_ENVIAR)} contatos...")

            enviados, falhados = [], []
            for nome in NOMES_PARA_ENVIAR:
                sucesso = buscar_e_abrir_conversa(page, nome)

                if sucesso and enviar_foguinho(page, nome):
                    enviados.append(nome)
                    time.sleep(2) # Pausa entre interações
                else:
                    falhados.append(nome)
                    logger.error(f"Pulei {nome} devido a falha no processo.")

            logger.info("🏁 Ciclo de envios finalizado.")

            resumo = f"✅ Foguinhos enviados: {', '.join(enviados) if enviados else 'nenhum'}"
            if falhados:
                resumo += f"\n⚠️ Falharam: {', '.join(falhados)}"
            enviar_aviso_telegram(resumo)

        except Exception as e:
            logger.critical(f"🚨 ERRO FATAL NO SISTEMA: {e}")
            if 'page' in locals():
                page.screenshot(path=f"erro_fatal_{int(time.time())}.png")
            enviar_aviso_telegram(f"🚨 ERRO CRÍTICO no Bot do TikTok!\n\nO robô travou. Motivo:\n{e}")

        finally:
            if browser:
                logger.info("🧹 Encerrando sessão e fechando navegador.")
                browser.close()

if __name__ == "__main__":
    rodar_bot_tiktok()