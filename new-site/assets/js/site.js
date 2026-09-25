// ESEA Agency – harita ve proforma formu

const form = document.querySelector("[data-form]");
const limanSec = document.getElementById("f-liman");

// Haritada bir limana tıklanınca: formdaki liman seçilir, forma gidilir.
function limaniSec(ad, odakla) {
  if (!limanSec || !ad) return;
  const opt = [...limanSec.options].find((o) => o.text === ad);
  if (!opt) return;
  limanSec.value = opt.text;
  limanSec.classList.remove("flash");
  void limanSec.offsetWidth; // animasyonu yeniden başlat
  limanSec.classList.add("flash");
  if (odakla) limanSec.focus({ preventScroll: true });
}

document.querySelectorAll(".port[data-liman]").forEach((a) => {
  a.addEventListener("click", (e) => {
    e.preventDefault();
    limaniSec(a.dataset.liman, true);
    document.getElementById("proforma").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    history.replaceState(null, "", `?liman=${encodeURIComponent(a.dataset.liman)}#proforma`);
  });
});
limaniSec(new URLSearchParams(location.search).get("liman"), false);

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
