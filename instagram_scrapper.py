from pathlib import Path
from datetime import datetime, timezone, timedelta

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
                "name": "list_followers",
                "func": self.extract_list_followers,
                "args": {"max_followers": 50},
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
                        if item["name"] in ("posts", "followers"):
                            item["enabled"] = False

            except Exception as e:
                print(f"❌ Error en {item.get('name', func.__name__)}: {e}")

        return result

    def extract_profile(self, page,):
        return self.run_extractor(page, "profile.js")

    def extract_location_creation_date(self, page):
        return self.run_extractor(page, "location_creation_date.js")

    def extract_posts(self, page, num_post=10):
        posts = {}
        page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=10000)

        # localizar todos los links en el DOM
        post_elements = page.locator('a[href*="/p/"], a[href*="/reel/"]')

        count = min(post_elements.count(), num_post)

        for i in range(count):
            try:
                el = post_elements.nth(i)

                # scroll + click real
                el.scroll_into_view_if_needed()
                el.click()

                page.wait_for_selector("time", timeout=10000)

                datetime_utc = page.evaluate("""
                    () => document.querySelector('time')?.getAttribute('datetime')
                """)
                likes = page.evaluate("""
                () => {
                    const article = document.querySelector('article[role="presentation"]');
                    if (!article) return null;

                    const text = article.innerText;

                    const match = text.match(/([\\d.,]+)\\s*(likes|me gusta)/i);

                    return match ? match[1] : null;
                }
                """)
                posts[f"post_{i+1}"] = {
                    "url": page.url,
                    "date_ecuador": self.to_ecuador_time(datetime_utc),
                    "likes": likes
                }

                # volver atrás
                page.go_back()
                page.wait_for_load_state("domcontentloaded")

            except Exception:
                posts[f"post_{i+1}"] = {
                    "url": None,
                    "date_ecuador": None,
                    "likes": None
                }

        return posts

    def extract_list_followers(self, page, max_scrolls=20, max_no_change=5, max_followers=None):
        page.wait_for_selector("a[href$='/following/']", timeout=40000)
        page.click("a[href$='/followers/']")
        page.wait_for_timeout(3000)

        dialog = page.wait_for_selector("div[role='dialog']", timeout=30000)

        usernames = []
        seen = set()

        scroll_count = 0
        no_change = 0
        last_count = 0

        while scroll_count < max_scrolls and no_change < max_no_change:
            scroll_count += 1

            nuevos = page.evaluate("""
                () => Array.from(
                    document.querySelectorAll('div[role="dialog"] a[role="link"]')
                )
                .map(a => a.getAttribute('href'))
                .filter(h => h && /^\\/[a-zA-Z0-9._]+\\/$/.test(h))
                .map(h => h.slice(1, -1))
            """)

            for u in nuevos:
                if u not in seen:
                    seen.add(u)
                    usernames.append(u)

                    # Limite de followers
                    if max_followers and len(usernames) >= max_followers:
                        return {
                            "list_followers": usernames[:max_followers]
                        }

            dialog.evaluate("el => el.scrollBy(0, 1200)")
            page.wait_for_timeout(2000)

            if len(usernames) == last_count:
                no_change += 1
            else:
                no_change = 0
                last_count = len(usernames)

        return {
            "list_followers": usernames[:max_followers] if max_followers else usernames
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