from playwright.sync_api import sync_playwright

def salvar_sessao_cdp():
    with sync_playwright() as p:
        print("Conectando ao Edge aberto...")
        # Conecta na porta que abrimos no Passo 1
        navegador = p.chromium.connect_over_cdp("http://localhost:9222")
        
        # Pega a primeira aba aberta
        contexto = navegador.contexts[0]
        pagina = contexto.new_page()

        print("Acessando o TikTok...")
        pagina.goto("https://www.tiktok.com/login")
        
        print("\n--- ATENÇÃO ---")
        print("Vá para a janela do Chrome que abriu e faça o login.")
        print("Pode usar o QR Code, e-mail, o que preferir.")
        
        # Em vez de esperar a janela fechar, vamos usar um input no terminal
        input("\n>>> Pressione ENTER aqui no terminal APÓS concluir o login no navegador... <<<")
        
        # Salva a sessão
        contexto.storage_state(path="estado_tiktok.json")
        print("Sessão salva com sucesso em 'estado_tiktok.json'!")

if __name__ == "__main__":
    salvar_sessao_cdp()