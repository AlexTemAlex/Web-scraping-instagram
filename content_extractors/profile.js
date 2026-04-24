async () => {
  const result = {
    username: null,
    private: null,
    num_followers: null,
    num_following: null,
    category: null,
    bio: null,
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const header = document.querySelector("main header");
  if (!header) return result;

  // USERNAME
  const usernameEl = header.querySelector("h1, h2");
  if (usernameEl) result.username = usernameEl.innerText.trim();

  // PRIVATE ACCOUNT
  result.private = (() => {
    const spans = document.querySelectorAll("main span");

    const text = Array.from(spans)
      .map((s) => s.innerText?.toLowerCase() || "")
      .join(" ");

    return /privad|private/.test(text);
  })();
  // ============================
  // FOLLOWERS / FOLLOWING
  // ============================
  const stats = header.querySelectorAll("div div header section span");

  const parseNumber = (text) => {
    if (!text) return null;

    text = text
      .toLowerCase()
      .replace(/\s/g, "") // quita espacios (109mil)
      .replace(",", "."); // coma decimal

    let multiplier = 1;

    // detectar unidades primero
    if (text.includes("mil")) {
      multiplier = 1_000;
      text = text.replace("mil", "");
    } else if (text.includes("k")) {
      multiplier = 1_000;
      text = text.replace("k", "");
    } else if (text.includes("mill") || text.includes("m")) {
      multiplier = 1_000_000;
      text = text.replace(/millones?|m/, "");
    }

    const num = parseFloat(text);

    if (isNaN(num)) return null;

    return Math.round(num * multiplier);
  };

  stats.forEach((li) => {
    const text = li.innerText.toLowerCase();

    // usamos keywords pero múltiples idiomas
    if (text.match(/followers|seguidores/)) {
      const num = text.split(" ")[0];
      result.num_followers = parseNumber(num);
    }

    if (text.match(/following|seguidos/)) {
      const num = text.split(" ")[0];
      result.num_following = parseNumber(num);
    }
  });

  // CATEGORY
  const categoryEl = Array.from(
    header.querySelectorAll("div[dir='auto']"),
  ).find((el) => {
    const text = el.innerText.trim();

    if (!text) return false;
    if (text === result.username) return false;
    if (text.match(/seguir|mensaje|publicaciones|seguidores|seguidos/i))
      return false;
    return true;
  });

  if (categoryEl) result.category = categoryEl.innerText.trim();

  // ============================
  // BIO
  // ============================
  const moreBtn = Array.from(header.querySelectorAll("span, button")).find(
    (el) => el.innerText && el.innerText.trim().toLowerCase() === "más",
  );

  if (moreBtn) {
    moreBtn.click();
    await sleep(800);
  }

  const bioContainer = document.querySelectorAll(
    "main header section > div > div",
  );

  let bios = [];

  if (bioContainer && bioContainer.length > 0) {
    bioContainer.forEach((container) => {
      const elements = Array.from(container.querySelectorAll("span")).filter(
        (el) => !el.closest('div[role="menu"]'),
      );
      // 🔥 FILTRO: descarta contenedores pobres (ruido)
      if (elements.length < 2) return;

      const seen = new Set();
      let lines = [];
      let links = [];

      // 🔗 EXTRAER HREF (filtrados)
      const anchors = container.querySelectorAll("a");
      anchors.forEach((a) => {
        const href = a.getAttribute("href");
        if (!href) return;

        const clean = href.trim().toLowerCase();

        // 🔥 FILTROS CLAVE
        if (clean.includes("/followers")) return;
        if (clean.includes("/following")) return;
        if (clean.startsWith("/") && !clean.includes("http")) return; // evita internos tipo /user/

        if (!links.includes(href)) {
          links.push(href);
        }
      });

      Array.from(elements)
        .map((el) => el.innerText.trim())
        .forEach((text) => {
          if (!text) return;

          // 🔥 separar textos pegados
          const parts = text.split(".").map((t) => t.trim());

          parts.forEach((part) => {
            if (!part) return;

            const lower = part.toLowerCase();

            if (lower === "más") return;
            if (seen.has(part)) return;
            if (/^\d+$/.test(part)) return;
            if (lower.match(/publicaciones|seguidores|seguidos/)) return;

            // 🔥 evitar cosas tipo "497 mil"
            if (part.match(/^\d+\s*(mil|k|m)?$/i)) return;

            seen.add(part);
            lines.push(part);
          });
        });

      // 🔥 FILTRO FINAL
      if (lines.length >= 2 || links.length > 0) {
        bios.push({
          text: lines,
          links: links,
        });
      }
    });
  }

  // resultado por secciones
  result.bio = bios.length > 0 ? bios : null;
  return result;
};
