async function showProduct() {
  const status = document.querySelector("#product-error");
  try {
    const response = await fetch("assets/data/academy-products.json?v=4");
    if (!response.ok) throw new Error("Catalog unavailable");
    const { products } = await response.json();
    const requestedKey = new URLSearchParams(location.search).get("product") || "court-tee";
    const aliases = { "court-short": "kc-reversible-short" };
    const key = aliases[requestedKey] || requestedKey;
    const product = products.find(({ id }) => id === key);
    if (!product) throw new Error("Product unavailable");

    document.title = product.name + " — Coach Carter Academy";
    document.querySelector("#product-name").textContent = product.name;
    document.querySelector("#product-kind").textContent = product.kind;
    document.querySelector("#product-price").textContent = product.status || product.price;
    if (product.status && product.price) {
      const estimate = document.querySelector("#product-estimate");
      estimate.textContent = product.price;
      estimate.hidden = false;
    }

    const photo = document.querySelector("#product-image");
    const caption = document.querySelector("#product-image-caption");
    const mainView = {
      id: "front", label: product.view_label || "Front", image: product.image, alt: product.alt,
      width: product.image_width || 900, height: product.image_height || 1350,
      caption: product.image_caption || caption.textContent,
    };
    const setPhoto = (view) => {
      photo.src = view.image;
      photo.alt = view.alt;
      photo.width = view.width;
      photo.height = view.height;
      caption.textContent = view.caption || view.label + " · " + (product.view_credit || "AI garment rendering");
    };
    if (product.views?.length) {
      const overview = product.overview;
      const views = [mainView, ...(overview ? [overview] : []), ...product.views];
      if (overview) photo.closest("article").classList.add("academy-product-with-overview");
      const gallery = document.querySelector("#product-views");
      photo.closest("figure").classList.add("product-visual-gallery");
      const buttons = views.map((view) => {
        const button = document.createElement("button");
        button.type = "button";
        const preview = new Image(view.width, view.height);
        preview.src = view.image;
        preview.alt = "";
        const label = document.createElement("span");
        label.textContent = view.label;
        button.append(preview, label);
        button.addEventListener("click", () => {
          history.replaceState(null, "", "#" + view.id);
          selectView();
        });
        return button;
      });
      const editions = document.querySelector("#product-editions");
      const editionLinks = (product.editions || []).map(({ view, name }) => {
        const edition = views.find(({ id }) => id === view);
        const link = document.createElement("a");
        link.href = "#" + view;
        const preview = new Image(edition.width, edition.height);
        preview.src = edition.image;
        preview.alt = "";
        const label = document.createElement("span");
        label.textContent = name;
        link.append(preview, label);
        link.addEventListener("click", (event) => {
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          history.replaceState(null, "", link.hash);
          selectView();
          photo.scrollIntoView({ block: "nearest" });
        });
        return link;
      });
      if (editionLinks.length) {
        editions.querySelector("div").replaceChildren(...editionLinks);
        editions.hidden = false;
      }
      const defaultView = views.find(({ id }) => id === product.default_view) || mainView;
      function selectView() {
        const selected = views.find((view) => "#" + view.id === location.hash) || defaultView;
        setPhoto(selected);
        buttons.forEach((button, index) => button.setAttribute("aria-pressed", String(views[index] === selected)));
        editionLinks.forEach((link) => link.setAttribute("aria-current", String(link.hash === "#" + selected.id)));
      }
      gallery.replaceChildren(...buttons);
      gallery.hidden = false;
      selectView();
      window.addEventListener("hashchange", selectView);
    } else {
      setPhoto(mainView);
    }

    if (product.flat) {
      const flat = document.querySelector("#product-flat");
      flat.src = product.flat;
      flat.closest("figure").hidden = false;
      if (product.flat_alt) flat.alt = product.flat_alt;
      if (product.flat_width) flat.width = product.flat_width;
      if (product.flat_height) flat.height = product.flat_height;
      if (product.flat_caption) {
        document.querySelector("#product-flat-caption").textContent = product.flat_caption;
      } else {
        document.querySelector("#product-flat-download").href = product.flat;
      }
    }

    if (product.pieces?.length) {
      const pieces = document.querySelector("#product-pieces");
      for (const id of product.pieces) {
        const piece = products.find((entry) => entry.id === id);
        const item = document.createElement("li");
        const pieceLink = document.createElement("a");
        pieceLink.href = "?product=" + encodeURIComponent(piece.id);
        pieceLink.className = "store-text-link";
        pieceLink.textContent = piece.name + " ↗";
        item.append(pieceLink);
        pieces.querySelector("ul").append(item);
      }
      pieces.hidden = false;
    }

    const specs = document.querySelector("#product-specs");
    specs.replaceChildren(...product.specs.map((spec) => {
      const item = document.createElement("li");
      item.textContent = spec;
      return item;
    }));

    const campaign = document.querySelector("#product-campaign");
    if (product.campaign) {
      campaign.href = product.campaign;
      if (product.group === "last-bell") campaign.textContent = "See it styled ↗";
      campaign.hidden = false;
    } else {
      campaign.remove();
    }

    const link = document.querySelector("#product-companion");
    const artwork = document.querySelector("#product-artwork");
    if (product.artwork) {
      artwork.src = product.artwork;
      document.querySelector("#product-artwork-label").textContent = product.artwork_label;
      const companion = products.find(({ id }) => id === product.companion);
      if (companion) {
        link.href = "?product=" + encodeURIComponent(companion.id);
        link.textContent = companion.name + " ↗";
      } else {
        link.remove();
      }
    } else {
      artwork.closest("figure").hidden = true;
      link.remove();
    }
    if (product.id === "front-row-letterman") {
      document.querySelector("#front-row-composite").hidden = false;
    }
    const lifestyleId = {
      "front-row-letterman": "front-row-lifestyle",
      "warm-up-zip-jacket": "warm-up-editorial",
    }[product.id];
    const lifestyle = lifestyleId && document.getElementById(lifestyleId);
    if (lifestyle) {
      lifestyle.hidden = false;
      const lifestyleLink = document.querySelector("#product-lifestyle-link");
      lifestyleLink.href = "#" + lifestyle.id;
      if (lifestyle.id === "warm-up-editorial") lifestyleLink.textContent = "See the game-night editorial ↓";
      lifestyleLink.hidden = false;

      const lightbox = document.querySelector("#product-lifestyle-lightbox");
      const expandedImage = lightbox.querySelector("img");
      lifestyle.querySelectorAll(".front-row-lifestyle-card").forEach((card) => {
        card.addEventListener("click", (event) => {
          if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          expandedImage.src = card.href;
          expandedImage.alt = card.querySelector("img").alt;
          lightbox.showModal();
        });
      });
      lightbox.querySelector("button").addEventListener("click", () => lightbox.close());
      lightbox.addEventListener("click", (event) => {
        if (event.target === lightbox) lightbox.close();
      });
    }
    document.querySelector(".academy-product-layout").hidden = false;
    status.hidden = true;
    if (lifestyle && location.hash === "#" + lifestyle.id) lifestyle.scrollIntoView();
  } catch {
    status.firstChild.textContent = "This piece could not be loaded. ";
  }
}

showProduct();
