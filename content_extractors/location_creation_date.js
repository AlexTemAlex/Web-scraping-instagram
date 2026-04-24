async () => {
  const result = {
    location: null,
    creation_date: null,
  };
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const header = document.querySelector("main header");
  if (!header) return result;

  const profileLink = header.querySelector("h2")?.closest("a");

  if (profileLink) {
    profileLink.scrollIntoView({ block: "center" });
    await delay(500);
    profileLink.click();
    await delay(1500);
  }

  for (let i = 0; i < 20; i++) {
    const dialogs = document.querySelectorAll('div[role="dialog"]');

    if (dialogs.length) {
      infoDialog = dialogs[dialogs.length - 1];
      break;
    }

    await delay(300);
  }

  if (infoDialog) {
    const blocks = infoDialog.querySelectorAll(
      'div[data-bloks-name="bk.components.Flexbox"]',
    );

    const locationLabels = ["ubicación", "location", "localización"];
    const dateLabels = ["fecha", "joined", "unió", "desde"];

    for (let block of blocks) {
      const spans = block.querySelectorAll(
        'span[data-bloks-name="bk.components.Text"]',
      );

      if (spans.length < 2) continue;

      const label = spans[0].innerText.trim().toLowerCase(); // 👈 IMPORTANTE
      const value = spans[1].innerText.trim();

      // 📍 ubicación
      if (!result.location && locationLabels.some((l) => label.includes(l))) {
        result.location = value;
      }

      // 📅 fecha
      if (!result.creation_date && dateLabels.some((l) => label.includes(l))) {
        result.creation_date = value;
      }
    }

    const closeButton = Array.from(document.querySelectorAll("button")).find(
      (button) => /cerrar|close/i.test(button.innerText),
    );

    if (closeButton) {
      closeButton.click();
      await delay(500);
    }
  }

  return result;
};
