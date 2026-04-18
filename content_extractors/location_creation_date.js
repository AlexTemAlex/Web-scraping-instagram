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
    const textSpans = infoDialog.querySelectorAll(
      'span[data-bloks-name="bk.components.Text"]',
    );

    if (textSpans.length >= 2) {
      result.location = textSpans[2].innerText.trim();
      result.creation_date = textSpans[4].innerText.trim();
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
