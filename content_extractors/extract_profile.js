async () => {
  const result = {
    username: null,
    category: null,
    bio: null,
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // HEADER
  const header = document.querySelector("main header");

  if (!header) return result;

  // USERNAME
  const usernameEl = header.querySelector("h1, h2");

  if (usernameEl) result.username = usernameEl.innerText.trim();

  // CLICK EN USERNAME (ABRIR PANEL INFO)
  let usernameLink = null;

  if (usernameEl) {
    usernameLink = usernameEl.closest("a");
  }

  if (!usernameLink) {
    usernameLink = Array.from(document.querySelectorAll('a[role="link"]')).find(
      (a) => a.querySelector("h2"),
    );
  }

  if (usernameLink) {
    usernameLink.scrollIntoView({ block: "center" });
    await sleep(500);
    usernameLink.click();
    await sleep(1500);
  }

  // ============================
  // CATEGORY
  // ============================
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

  const bioContainer = header.querySelector("section:last-of-type");

  if (bioContainer) {
    const seen = new Set();

    let lines = Array.from(
      bioContainer.querySelectorAll("div[dir='auto'], span"),
    )
      .map((el) => el.innerText.trim())
      .filter((text) => {
        if (!text) return false;

        const lower = text.toLowerCase();

        if (lower === "más") return false;
        if (seen.has(text)) return false;
        if (/^\d+$/.test(text)) return false;
        if (lower.match(/publicaciones|seguidores|seguidos/)) return false;

        seen.add(text);

        return true;
      });

    let bio = lines.join(". ");

    bio = bio.replace(
      /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu,
      "",
    );

    bio = bio.replace(/\.+/g, ".");
    bio = bio.replace(/\s+/g, " ").trim();
    result.bio = bio || null;
  }

  return result;
};
