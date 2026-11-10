async function showProduct() {
  const status = document.querySelector("#product-error");
  try {
    const response = await fetch("assets/data/academy-products.json");
    if (!response.ok) throw new Error("Catalog unavailable");
    const { products } = await response.json();
    const key = new URLSearchParams(location.search).get("product") || "court-tee";
    const product = products.find(({ id }) => id === key);
    if (!product) throw new Error("Product unavailable");

    document.title = product.name + " — Coach Carter Academy";
    document.querySelector("#product-name").textContent = product.name;
    document.querySelector("#product-kind").textContent = product.kind;
    document.querySelector("#product-price").textContent = product.status || product.price;
    const photo = document.querySelector("#product-image");
    photo.src = product.image;
    photo.alt = product.alt;
    if (product.image_caption) {
      photo.width = product.image_width;
      photo.height = product.image_height;
      document.querySelector("#product-image-caption").textContent = product.image_caption;
    }
    const flat = document.querySelector("#product-flat");
    flat.src = product.flat;
    if (product.flat_caption) {
      flat.alt = product.flat_alt;
      flat.width = product.flat_width;
      flat.height = product.flat_height;
      document.querySelector("#product-flat-caption").textContent = product.flat_caption;
    } else {
      document.querySelector("#product-flat-download").href = product.flat;
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
    document.querySelector(".academy-product-layout").hidden = false;
    status.hidden = true;
  } catch {
    status.firstChild.textContent = "This piece could not be loaded. ";
  }
}

showProduct();
