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
    document.querySelector("#product-price").textContent = product.price;
    const photo = document.querySelector("#product-image");
    photo.src = product.image;
    photo.alt = product.alt;
    document.querySelector("#product-flat").src = product.flat;
    document.querySelector("#product-flat-download").href = product.flat;

    const specs = document.querySelector("#product-specs");
    specs.replaceChildren(...product.specs.map((spec) => {
      const item = document.createElement("li");
      item.textContent = spec;
      return item;
    }));

    document.querySelector("#product-artwork").src = product.artwork;
    document.querySelector("#product-artwork-label").textContent = product.artwork_label;
    const companion = products.find(({ id }) => id !== product.id);
    const link = document.querySelector("#product-companion");
    link.href = "?product=" + encodeURIComponent(companion.id);
    link.textContent = "Complete the look · " + companion.name + " ↗";
    document.querySelector(".academy-product-layout").hidden = false;
    status.hidden = true;
  } catch {
    status.firstChild.textContent = "This piece could not be loaded. ";
  }
}

showProduct();
