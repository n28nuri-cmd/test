import { renderPeople, renderContact } from "./render.js?v=esea0925d";

const doc = document.documentElement;
doc.classList.add("js");
const lang = document.body.dataset.lang || "tr";
const base = document.body.dataset.base || "";
const header = document.querySelector("[data-header]");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// --- header: kaydırınca küçülür ---
const onScroll = () => header?.classList.toggle("scrolled", window.scrollY > 30);
onScroll();
window.addEventListener("scroll", onScroll, { passive: true });

// --- mobil menü ---
const toggle = document.querySelector("[data-nav-toggle]");
if (toggle && header) {
  const setOpen = (open) => {
    header.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
  };
  toggle.addEventListener("click", () => setOpen(!header.classList.contains("nav-open")));
  header.querySelectorAll(".main-nav a, .main-nav button").forEach((a) => a.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", (e) => e.key === "Escape" && setOpen(false));
}

// --- aktif menü bölümü (ana sayfa) ---
const anchors = [...document.querySelectorAll(".main-nav a[data-anchor]")];
if (anchors.length && "IntersectionObserver" in window) {
  const map = new Map(anchors.map((a) => [a.hash.slice(1), a]));
  const spy = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting && map.has(e.target.id)) { anchors.forEach((a) => a.removeAttribute("aria-current")); map.get(e.target.id).setAttribute("aria-current", "true"); }
  }), { rootMargin: "-45% 0px -50% 0px" });
  map.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });
}

// --- görünür olunca belirme ---
const io = "IntersectionObserver" in window
  ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -8% 0px", threshold: 0.06 })
  : null;
const observe = (root = document) => root.querySelectorAll(".reveal:not(.in)").forEach((el) => (io ? io.observe(el) : el.classList.add("in")));
observe();

// --- liman bölgesi listesi ↔ harita vurgusu ---
const trMap = document.querySelector(".tr-map");
if (trMap) document.querySelectorAll("[data-region]").forEach((r) => {
  const on = () => (trMap.dataset.hl = r.dataset.region), off = () => delete trMap.dataset.hl;
  r.addEventListener("mouseenter", on); r.addEventListener("mouseleave", off);
  r.addEventListener("focus", on); r.addEventListener("blur", off);
});

// --- slider (SAS tarzı) ---
const slider = document.querySelector("[data-slider]");
if (slider) {
  const slides = [...slider.querySelectorAll("[data-slide]")];
  const dots = [...slider.querySelectorAll("[data-dot]")];
  let idx = 0, timer = null;
  const go = (n) => {
    idx = (n + slides.length) % slides.length;
    slides.forEach((s, i) => { s.classList.toggle("is-active", i === idx); s.setAttribute("aria-hidden", String(i !== idx)); });
    dots.forEach((d, i) => d.setAttribute("aria-selected", String(i === idx)));
  };
  const play = () => { if (reduceMotion) return; stop(); timer = setInterval(() => go(idx + 1), 7000); };
  const stop = () => clearInterval(timer);
  slider.querySelector("[data-prev]")?.addEventListener("click", () => { go(idx - 1); play(); });
  slider.querySelector("[data-next]")?.addEventListener("click", () => { go(idx + 1); play(); });
  dots.forEach((d, i) => d.addEventListener("click", () => { go(i); play(); }));
  slider.addEventListener("mouseenter", stop);
  slider.addEventListener("mouseleave", play);
  slider.addEventListener("focusin", stop);
  slider.addEventListener("keydown", (e) => { if (e.key === "ArrowLeft") { go(idx - 1); play(); } if (e.key === "ArrowRight") { go(idx + 1); play(); } });
  let x0 = null;
  slider.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  slider.addEventListener("touchend", (e) => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) { go(idx + (dx < 0 ? 1 : -1)); play(); } x0 = null; });
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : play()));
  play();
}

// --- kişi detay penceresi (Zeymarine "View details") ---
const pm = document.querySelector("[data-person-modal]");
const bindPeople = (root = document) => {
  if (!pm || typeof pm.showModal !== "function") { root.querySelectorAll("[data-person]").forEach((b) => b.remove()); return; }
  root.querySelectorAll("[data-person]").forEach((b) => b.addEventListener("click", () => {
    const tpl = b.closest(".pp").querySelector("template[data-person-detail]");
    const bodyEl = pm.querySelector("[data-person-body]");
    bodyEl.replaceChildren(tpl.content.cloneNode(true));
    pm.showModal();
  }));
};
if (pm) {
  pm.querySelector("[data-person-close]").addEventListener("click", () => pm.close());
  pm.addEventListener("click", (e) => e.target === pm && pm.close());
}
bindPeople();

// --- site-bilgileri.json: cPanel'den yapılan düzenlemeler derleme gerektirmeden yansır ---
if (document.querySelector("[data-people], [data-contact]")) {
  fetch(`${base}assets/data/site-bilgileri.json`, { cache: "no-cache" })
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then((data) => {
      document.querySelectorAll("[data-people]").forEach((el) => {
        el.innerHTML = renderPeople(data, lang, base, el.dataset.heading || "h3", Number(el.dataset.limit) || 0);
        el.querySelectorAll(".reveal").forEach((r) => r.classList.add("in"));
        bindPeople(el);
      });
      const ct = document.querySelector("[data-contact]");
      if (ct) ct.innerHTML = renderContact(data, lang);
    })
    .catch(() => {});
}

// --- iletişim / proforma formu ---
const form = document.querySelector("[data-form]");
if (form) {
  const status = form.querySelector(".form-status");
  const btn = form.querySelector('button[type="submit"]');
  const setStatus = (msg, cls) => { status.textContent = msg; status.className = `form-status ${cls || ""}`; };
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    let firstBad = null;
    form.querySelectorAll("[required]").forEach((el) => {
      const bad = el.type === "checkbox" ? !el.checked : !el.value.trim() || (el.type === "email" && !el.checkValidity());
      (el.closest(".fg") || el.closest(".consent"))?.classList.toggle("invalid", bad);
      if (bad && !firstBad) firstBad = el;
    });
    if (firstBad) { setStatus(status.dataset.req, "err"); firstBad.focus(); return; }
    if (form.dataset.preview) { setStatus(form.dataset.preview, "ok"); return; }
    btn.disabled = true; btn.textContent = btn.dataset.sending; setStatus("");
    try {
      const res = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } });
      const json = await res.json().catch(() => ({}));
      if (!res.ok || !json.ok) throw new Error(json.error || res.status);
      form.reset();
      setStatus(status.dataset.ok, "ok");
    } catch {
      setStatus(status.dataset.err, "err");
    } finally {
      btn.disabled = false; btn.textContent = btn.dataset.label;
    }
  });
  form.addEventListener("input", (e) => (e.target.closest(".fg") || e.target.closest(".consent"))?.classList.remove("invalid"));
  const q = new URLSearchParams(location.search).get("form");
  if (q) setStatus(q === "ok" ? status.dataset.ok : status.dataset.err, q === "ok" ? "ok" : "err");
}
