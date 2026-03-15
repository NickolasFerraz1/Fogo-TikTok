import time
import requests
import traceback  # Ajuda a capturar a mensagem de erro exata
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES DO TELEGRAM ---
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para a memória
load_dotenv()

# Puxa as chaves de forma segura
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_TELEGRAM = os.getenv("CHAT_ID_TELEGRAM")

# Se esquecer de criar o .env, o programa avisa em vez de quebrar silenciosamente
if not TOKEN_TELEGRAM or not CHAT_ID_TELEGRAM:
    raise ValueError("🚨 ERRO: As chaves do Telegram não foram encontradas no arquivo .env!")

def enviar_aviso_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao tentar mandar mensagem pro Telegram: {e}")

def enviar_foguinhos_em_massa(lista_contatos):
    # O TRY GERAL: Captura qualquer erro fatal que aconteça no processo
    try:
        with sync_playwright() as p:
            # headless=True para rodar invisível no fundo!
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(storage_state="estado_tiktok.json", viewport={"width": 1920, "height": 1080})
            pagina = contexto.new_page()

            pagina.goto("https://www.tiktok.com/messages")
            pagina.wait_for_load_state("networkidle")
            time.sleep(5)

            # 1. VERIFICAÇÃO DE SESSÃO EXPIRADA
            if "login" in pagina.url:
                enviar_aviso_telegram("⚠️ ALERTA: A sessão do TikTok expirou! Gere um novo estado_tiktok.json.")
                navegador.close()
                return 

            total = len(lista_contatos)

            # 2. O LOOP DOS FOGUINHOS
            for i, contato in enumerate(lista_contatos, 1):
                try:
                    elementos_contato = pagina.get_by_text(contato, exact=True)
                    quantidade = elementos_contato.count()
                    
                    elemento_clicavel = None
                    for j in range(quantidade):
                        if elementos_contato.nth(j).is_visible():
                            elemento_clicavel = elementos_contato.nth(j)
                            break
                    
                    if not elemento_clicavel:
                        continue
                    
                    elemento_clicavel.click()
                    time.sleep(2)

                    caixa_texto = pagina.get_by_placeholder("Enviar mensagem", exact=False).first
                    if not caixa_texto.is_visible():
                        caixa_texto = pagina.locator('div[contenteditable="true"]').first
                    
                    caixa_texto.click()
                    time.sleep(1)

                    pagina.keyboard.type("🔥")
                    time.sleep(1)
                    pagina.keyboard.press("Enter")
                    time.sleep(3) 

                except Exception as e:
                    # Erro em um contato específico (não para o programa)
                    print(f"Erro no contato {contato}: {e}")
                    continue

            navegador.close()
            
            # 3. NOTIFICAÇÃO DE SUCESSO!
            enviar_aviso_telegram("✅ Foguinhos do TikTok enviados com sucesso hoje!")

    except Exception as erro_fatal:
        # Se o navegador fechar sozinho, a internet cair, ou o site mudar, cai aqui!
        mensagem_erro = f"🚨 ERRO CRÍTICO no Bot do TikTok!\n\nO robô travou. Motivo:\n{str(erro_fatal)}"
        enviar_aviso_telegram(mensagem_erro)
        print("Erro fatal enviado para o Telegram.")

if __name__ == "__main__":
    # Coloque aqui os nomes exatamente como aparecem no seu TikTok
    meus_amigos = [
        "enzo",
        "Heloísa Biazotti",
        "Enzo Carvalho",
        "Otávio Gasque"
    ]
    
    enviar_foguinhos_em_massa(meus_amigos)