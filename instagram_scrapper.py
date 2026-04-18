from pathlib import Path

BASE_PATH = Path(__file__).parent

class InstagramScrapper:

    def __init__(self, page):
        self.page = page
        self.list_functions = [
            self.extract_profile,
        ]

    def abrir_perfil(self, url):
        self.page.goto(url, timeout=50000)
        self._cerrar_popup()

    def _cerrar_popup(self):
        try:
            self.page.click('svg[aria-label="Cerrar"]', timeout=3000)
        except:
            pass

    # def to_ecuador_time(self, iso):
    #     if not iso:
    #         return None

    #     try:
    #         utc = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    #         ecu = utc - timedelta(hours=5)
    #         return ecu.strftime("%Y-%m-%d %H:%M:%S")
    #     except:
    #         return None

    def get_user_info(self):     
        result = {}
        
        for func in self.list_functions:
            try:
                data = func(self.page)
                if data is not None:
                    result.update(data)
            except Exception as e:
                print(f"❌ Error en {func.__name__}: {e}")
                continue
            
        return result

    def extract_profile(self, page, data=None):
        js_path = BASE_PATH / "content_extractors/extract_profile.js"

        try:
            # Cargar archivo extract_profile.js 
            with open(js_path, "r", encoding="utf-8") as f:
                js_script = f.read()
            
            page.wait_for_load_state("domcontentloaded") #Probar uno de estos 2
            page.wait_for_timeout(1500)
            
            data = page.evaluate(js_script)

            if not data:
                print("No se extrajo información.")
                return None

            return data

        except Exception as e:
            print(f"\nError: {e}")

