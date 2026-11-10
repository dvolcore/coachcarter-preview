/* Store directory. */
(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  const hachette = "https://www.hachettebookgroup.com/titles/coach-carter/yes-maam-no-sir/";
  const coverPath = "assets/img/books/yes-maam-no-sir-";
  const hardcover = { src: coverPath + "hardcover.webp", width: 563, height: 850, alt: "Yes Ma’am, No Sir hardcover cover by Coach Carter" };
  const audiobook = { src: coverPath + "audiobook.webp", width: 850, height: 850, alt: "Yes Ma’am, No Sir audiobook cover by Coach Carter" };
  const ebook = { src: coverPath + "ebook.webp", width: 563, height: 850, alt: "Yes Ma’am, No Sir eBook cover by Coach Carter" };
  const commitmentCard = { src: "academy-studio/team-pack/commitment-card-front.svg", width: 500, height: 700, alt: "Coach Carter Team Pack Commitment Card" };
  const editions = [
    { cat: "books", name: "Yes Ma’am, No Sir", status: "Hardcover", description: "Business Plus · ISBN 9781455502349", art: [hardcover], url: hachette + "9781455502349/", action: "Find at Hachette", amazon: { url: "https://www.amazon.com/dp/1455502340", label: "Find at Amazon" } },
    { cat: "books", name: "Yes Ma’am, No Sir", status: "Audiobook", description: "Hachette Audio · read by Coach Carter and Vince Bailey", art: [audiobook], url: hachette + "9781611137279/", action: "Find at Hachette" },
    { cat: "books", name: "Yes Ma’am, No Sir", status: "eBook", description: "Business Plus · digital edition", art: [ebook], url: hachette + "9781455502332/", action: "Find at Hachette", amazon: { url: "https://www.amazon.com/dp/B004RD84X6", label: "Find on Kindle" } },
    { cat: "books", name: "Team Pack", status: "In development", description: "Published books, printable Commitment Cards and a 60-minute guide for 25 participants", art: [hardcover, commitmentCard], url: "#team-pack", action: "Explore the materials" },
    { cat: "collectibles", name: "Signed Game Ball", status: "In development", description: "Full-size basketball with a numbered signing record", url: "#signed-ball", action: "See edition details" },
    { cat: "collectibles", name: "The Contract — Collector Edition", status: "In development", description: "Numbered reproduction pending authentication of the original", url: "#collector-edition", action: "See edition details" },
    { cat: "film", name: "Coach Carter", status: "2005 film", description: "The film starring Samuel L. Jackson", url: "https://www.paramount.com/movies/coach-carter", action: "See viewing options" },
  ];

  const grid = $("#product-grid");
  if (grid) {
    const draw = (category) => {
      grid.innerHTML = editions.filter(({ cat }) => category === "all" || cat === category).map((edition) => `
        <article class="edition-card">
          ${edition.art ? `<div class="edition-art">
            ${edition.art.map(({ src, width, height, alt }) =>
              `<img src="${src}" width="${width}" height="${height}" alt="${alt}" loading="lazy" decoding="async">`
            ).join("")}
          </div>` : ""}
          <p class="store-label">${edition.status}</p>
          <h3>${edition.name}</h3>
          <p class="edition-description">${edition.description}</p>
          <div class="edition-links">
            <a class="store-text-link" href="${edition.url}">${edition.action} <span aria-hidden="true">→</span></a>
            ${edition.amazon ? `<a class="store-text-link" href="${edition.amazon.url}">${edition.amazon.label} <span aria-hidden="true">→</span></a>` : ""}
          </div>
        </article>`).join("");
    };
    const chips = $$(".filters .chip");
    const select = (category) => {
      chips.forEach((chip) => {
        const active = chip.dataset.cat === category;
        chip.classList.toggle("on", active);
        chip.setAttribute("aria-pressed", String(active));
      });
      draw(category);
    };
    chips.forEach((chip) => chip.addEventListener("click", () => select(chip.dataset.cat)));
    const category = new URLSearchParams(location.search).get("cat");
    select(chips.some((chip) => chip.dataset.cat === category) ? category : "all");
    const section = ["academy", "apparel"].includes(category)
      ? $("#academy-store-title")
      : chips.some((chip) => chip.dataset.cat === category && category !== "all") ? $("#editions") : null;
    if (section && !location.hash) section.scrollIntoView();
  }
})();
