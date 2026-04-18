from playwright.sync_api import sync_playwright
import os


class Browser:
    def __init__(self, cookies_path=None, headless=False):
        self.cookies_path = cookies_path    # Ruta opcional donde se guardan/cargan cookies (storage_state)      
        self.headless = headless            # Navegador visible (False) o en segundo plano (True)
        self.playwright = None              # Motor de Playwright
        self.browser = None                 # Tipo de navegador
        self.context = None

    # Inicia Playwright y abre el navegador
    def start(self):
        self.playwright = sync_playwright().start()         # Inicializa el Motor de Playwright

        self.browser = self.playwright.chromium.launch(     # Lanza el navegador Chromium embebido, si se quiere el instalado en host usar channel="chrome",
            headless=self.headless
        )

        # Si existe un archivo de cookies, lo carga como estado del contexto
        if self.cookies_path and os.path.exists(self.cookies_path):
            self.context = self.browser.new_context(
                storage_state=self.cookies_path             # Sesión guardada
            )
        else:   # Si no hay cookies, crea un contexto limpio
            self.context = self.browser.new_context()

        self.page = self.context.new_page()                 # Crea la primera pagina (page)

        return self.page

    # Abre una nueva pestaña dentro del mismo contexto, sino crea y devuelve una nueva página
    def new_page(self):
        if self.context is None:
            raise Exception("El navegador no ha sido iniciado. Llama a start() primero.")
        return self.context.new_page()

    # Cierra todo correctamente (browser + playwright)
    def close(self):
        # Cierra el navegador si está abierto
        if self.browser:
            self.browser.close()

        # Detiene el motor de Playwright
        if self.playwright:
            self.playwright.stop()