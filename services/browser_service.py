import os
import time
from browser import Browser

def ensure_session_instagram(p, storage_path):
    """
    Abre el navegador y crea un archivo de cookies 
    al iniciar sesión manualmente en Instagram
    """
    browser = Browser(p, headless=False)

    try:
        page = browser.start()
        page.goto("https://www.instagram.com/")
        input("Inicia sesión y presiona ENTER...")
        browser.context.storage_state(path=storage_path)
    finally:
        browser.close()

def iniciar_browser(p, storage_path, headless):
    if not os.path.exists(storage_path):
        ensure_session_instagram(p, storage_path)

    browser = Browser(p, cookies_path=storage_path, headless=headless)
    browser.start_browser()

    page = browser.new_page()
    page.goto("https://www.instagram.com/")
    time.sleep(1)

    return browser, page