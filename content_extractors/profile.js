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
  result.private = !!document
    .querySelector("h2, span")
    ?.innerText.toLowerCase()
    .match(/privad|private/);

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
