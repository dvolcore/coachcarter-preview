/* MOTION PLATES — playback. Markup: tools/motion.py. Styles: motion.css.
   .in   = entrance has played (added once, when 30% of the plate is visible)
   .live = plate is on screen (loops run only then, so six scenes never animate at once off screen) */
(() => {
  "use strict";
  const plates = Array.from(document.querySelectorAll("[data-plate]"));
  if (!plates.length) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // film-strip photographs load when the plate is near, not with the page
  const loadImages = (plate) => plate.querySelectorAll("image[data-href]").forEach((img) => {
    img.setAttribute("href", img.dataset.href);
    img.removeAttribute("data-href");
  });
  const tally = (plate) => plate.querySelectorAll("[data-tally]").forEach((el) => {
    const to = +el.dataset.tally, t0 = performance.now() + 1300, dur = 2300;
    el.textContent = "0";
    const step = (now) => {
      const k = Math.min(1, Math.max(0, (now - t0) / dur));
      el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  if (reduce || !("IntersectionObserver" in window)) {
    plates.forEach((p) => { loadImages(p); p.classList.add("in"); });
    return;
  }
  const near = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (en.isIntersecting) { loadImages(en.target); near.unobserve(en.target); }
  }), { rootMargin: "1400px 0px" });
  const enter = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return;
    en.target.classList.add("in");
    tally(en.target);
    enter.unobserve(en.target);
  }), { threshold: 0.3 });
  const live = new IntersectionObserver((ents) => ents.forEach((en) => en.target.classList.toggle("live", en.isIntersecting)));
  plates.forEach((p) => { near.observe(p); enter.observe(p); live.observe(p); });
})();
