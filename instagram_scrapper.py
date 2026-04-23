from pathlib import Path
from datetime import datetime, timezone, timedelta
import random

BASE_PATH = Path(__file__).parent

class InstagramScrapper:

    def __init__(self, page):
        self.page = page
        self.dict_functions = [     # Se recomienda mantener la funcion profile primera
            {
                "name": "profile",
                "func": self.extract_profile,
                "args": {},
                "enabled": True
            },
            {
                "name": "location_and_creation_date",
                "func": self.extract_location_creation_date,
                "args": {},
                "enabled": True
            },
            {
                "name": "posts",
                "func": self.extract_posts,
                "args": {"num_post": 5},
                "enabled": True
            },
            {
                "name": "list_following",
                "func": self.extract_list_following,
                "args": {"max_following": 50},
                "enabled": True
            }
        ]

    def abrir_perfil(self, url):
        self.page.goto(url, timeout=50000)
        self._cerrar_popup()

    def _cerrar_popup(self):
        try:
            self.page.click('svg[aria-label="Cerrar"]', timeout=3000)
        except:
            pass

    def to_ecuador_time(self, iso):
        if not iso:
            return None

        try:
            utc = datetime.fromisoformat(iso.replace("Z", "+00:00"))

            ecuador_tz = timezone(timedelta(hours=-5))
            ecu = utc.astimezone(ecuador_tz)

            return ecu.strftime("%Y-%m-%d %H:%M:%S")

        except:
            return None

    def get_user_info(self):
        result = {}

        for item in self.dict_functions:
            if not item.get("enabled", True):
                continue

            func = item["func"]
            args = item.get("args", {})

            try:
                data = func(self.page, **args)

                if data is None:
                    continue

                # actualizar resultado global
                result.update(data)

                # si el perfil es privado
                if data.get("private") is True:

                    for item in self.dict_functions:
                        if item["name"] in ("posts", "list_following"):
                            item["enabled"] = False

            except Exception as e:
                print(f"❌ Error en {item.get('name', func.__name__)}: {e}")

        return result

    def extract_profile(self, page,):
        return self.run_extractor(page, "profile.js")

    def extract_location_creation_date(self, page):
        return self.run_extractor(page, "location_creation_date.js")

    def extract_posts(self, page, num_post):
        posts = {}

        page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=10000)

        for i in range(num_post):
            try:
                # 🔁 re-localizar SIEMPRE
                post_elements = page.locator('a[href*="/p/"], a[href*="/reel/"]')

                if i >= post_elements.count():
                    break

                el = post_elements.nth(i)

                # scroll
                el.scroll_into_view_if_needed()
                page.wait_for_timeout(500)

                # click robusto (fallback incluido)
                try:
                    el.click(timeout=3000)
                except:
                    page.evaluate("(el) => el.click()", el)

                page.wait_for_selector('article time[datetime]', timeout=10000)
                page.wait_for_timeout(1000)
                #             # images: Array.from(d?.querySelectorAll('img') || []).map(img => img.src)

                data = page.evaluate("""
                    () => {
                        const dialog = document.querySelector('div[role="dialog"]');
                        if (!dialog) return null;

                        const article = dialog.querySelector('article[role="presentation"]');
                        if (!article) return null;

                        const imgPost = article.querySelector('div[role="button"] div > img')?.src || null;
                            
                        const datetime = article.querySelector('time')?.getAttribute('datetime') || null;

                        let likes = null;
                        const spans = article.querySelectorAll('span');
                        for (let s of spans) {
                            const text = s.innerText.toLowerCase();
                            if (text.includes('likes') || text.includes('me gusta')) {
                                likes = text
                                    .replace('likes', '')
                                    .replace('me gusta', '')
                                    .trim();
                                break;
                            }
                        }

                        // contenedor comentarios + descripcion
                        const ulDescriptionAndComments = article.querySelector('div[role="presentation"] div div ul');
                        if (!ulDescriptionAndComments) return { datetime, likes, writer: null, text: null, comments: [] };
                        
                        // description
                        const lis = ulDescriptionAndComments.querySelectorAll('div[role="button"] li');

                        let writer = null;
                        let text = null;
                        const comments = [];

                        for (const d of lis) {
                            const tmpWriter = d.querySelector('h2')?.innerText?.trim() || null;
                            const tmpText = d.querySelector('h1')?.innerText?.trim() || null;

                            if (tmpText) {
                                writer = tmpWriter;
                                text = tmpText;
                                break;
                            }
                        }
                        
                        
                        // comments (writer + text)
                        const commentList = ulDescriptionAndComments.querySelectorAll('div div div ul > div[role="button"]');

                        Array.from(commentList).forEach((el, idx) => {
                            const user = el.querySelector('li h3')?.innerText?.trim();
                            let content = el.querySelector('li > div > div > div > div > span')?.innerText?.trim();

                            if (!content) return;

                            // primer elemento = descripción del post
                            if (idx !== 0) {
                                comments.push({
                                    id: comments.length + 1,
                                    writer: user,
                                    text: content
                                });
                            }
                        });

                        return { imgPost, datetime, likes, writer, text, comments };
                    }
                """)

                if not data:
                    data = {
                        "imgPost": None,
                        "datetime": None,
                        "likes": None,
                        "writer": None,
                        "text": None,
                        "comments": []
                    }

                posts[f"post_{i+1}"] = {
                    "url": page.url,
                    "imgPost": data["imgPost"],
                    "datetime_utc": data["datetime"],
                    "likes": data["likes"],
                    "writer": data["writer"],
                    "text": data["text"],
                    "comments": data["comments"]
                }
                
                try:
                    close_btn = page.locator('div[role="button"]:has(svg[aria-label="Cerrar"])').first

                    close_btn.click(force=True, timeout=5000)

                except:
                    pass
                
            except Exception as e:
                print(f"Error en post {i}: {e}")
                
                posts[f"post_{i+1}"] = {
                    "url": None,
                    "datetime_utc": None,
                    "likes": None,
                    "writer": None,
                    "text": None,
                    "comments": []
                }

        return posts

    def extract_list_following(self, page, max_no_change=12, max_following=None):
        page.wait_for_selector("a[href$='/following/']", timeout=40000)
        page.click("a[href$='/following/']")
        page.wait_for_timeout(3000)

        page.wait_for_selector("div[role='dialog']", timeout=30000)

        usernames = []
        seen = set()

        no_change = 0
        last_count = 0
        last_height = 0

        get_container = """
        () => {
            const dialog = document.querySelector('div[role="dialog"]');
            if (!dialog) return null;

            const divs = dialog.querySelectorAll('div');

            for (let el of divs) {
                if (el.scrollHeight > el.clientHeight) {
                    return el;
                }
            }
            return null;
        }
        """

        while True:

            # 🔥 EXTRAER USERS
            nuevos = page.evaluate("""
                () => Array.from(
                    document.querySelectorAll('div[role="dialog"] a[href^="/"]')
                )
                .map(a => a.getAttribute('href'))
                .filter(h => h && /^\\/[a-zA-Z0-9._]+\\/$/.test(h))
                .map(h => h.slice(1, -1))
            """)

            for u in nuevos:
                if u not in seen:
                    seen.add(u)
                    usernames.append(u)

                    if max_following and len(usernames) >= max_following:
                        return {"list_followers": usernames[:max_following]}

            # 🔥 MULTI-SCROLL (CLAVE REAL)
            for _ in range(3):
                page.evaluate(f"""
                {get_container}
                (c => {{
                    if (c) c.scrollTop = c.scrollHeight;
                }})(({get_container})())
                """)
                page.wait_for_timeout(800)

            # ⏳ ESPERA REAL
            page.wait_for_timeout(2500)

            # 🔥 MEDIR ALTURA (NUEVO)
            current_height = page.evaluate(f"""
            {get_container}
            (c => c ? c.scrollHeight : 0)(({get_container})())
            """)

            current_count = len(usernames)

            # 🔥 DETECCIÓN REAL DE FIN
            if current_count == last_count and current_height == last_height:
                no_change += 1
            else:
                no_change = 0
                last_count = current_count
                last_height = current_height

            print(f"   [INFO] Users: {current_count} | Height: {current_height} | NoChange: {no_change}")

            if no_change >= max_no_change:
                print("   [INFO] FIN - NO SE DETECTARON MAS USUARIOS")
                break

        return {
            "list_followers": usernames
        }

    def run_extractor(self, page, js_filename):
        js_path = BASE_PATH / f"content_extractors/{js_filename}"

        try:
            with open(js_path, "r", encoding="utf-8") as f:
                js_script = f.read()

            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1500)

            data = page.evaluate(js_script)

            if not data:
                print(f"No se extrajo información de {js_filename}")
                return None

            return data

        except Exception as e:
            print(f"\nError en {js_filename}: {e}")
            return None