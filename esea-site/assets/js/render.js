// Ekip ve iletişim blokları için ortak HTML üreticisi.
// Hem build.mjs (ön-işleme) hem de tarayıcı (site-bilgileri.json canlı okuma) bu modülü kullanır.

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const tel = (s) => String(s).replace(/[^\d+]/g, "");
// Veri dosyasından gelen dış bağlantılar yalnızca https olabilir (javascript: vb. engellenir).
const url = (s) => (/^https:\/\//i.test(String(s ?? "").trim()) ? esc(String(s).trim()) : "#");

export const ICON = {
  phone: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.46.57 3.6a1 1 0 0 1-.25 1z"/></svg>',
  mail: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zm0 2v.4l8 5 8-5V7H4zm16 2.8-7.47 4.67a1 1 0 0 1-1.06 0L4 9.8V17h16V9.8z"/></svg>',
  linkedin: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4V21H3zM9.5 9.75h3.8v1.54h.05c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.78 2.65 4.78 6.1V21h-4v-4.99c0-1.19-.02-2.72-1.66-2.72-1.66 0-1.91 1.3-1.91 2.63V21h-4z"/></svg>',
  pin: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 1 7 7c0 5.25-7 13-7 13S5 14.25 5 9a7 7 0 0 1 7-7zm0 4.5A2.5 2.5 0 1 0 12 11.5 2.5 2.5 0 0 0 12 6.5z"/></svg>',
  clock: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 1 0 20 10 10 0 0 1 0-20zm0 2a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm1 3v4.59l3.2 3.2-1.4 1.42L11 12.4V7z"/></svg>',
  anchor: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a3 3 0 0 1 1 5.83V9h3v2h-3v8.9A7 7 0 0 0 18.9 14H17l3-4 3 4h-2.08A9 9 0 0 1 3.08 14H1l3-4 3 4H5.1A7 7 0 0 0 11 19.9V11H8V9h3V7.83A3 3 0 0 1 12 2zm0 2a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/></svg>',
};

const T = {
  tr: { details: "Detaylar", call: "Ara", mail: "E-posta", li: "LinkedIn", soon: "Fotoğraf yakında", ops: "7/24 Operasyon Hattı", email: "E-posta", opsMail: "Operasyon", address: "Merkez Ofis", map: "Haritada aç", office: "Telefon" },
  en: { details: "View details", call: "Call", mail: "Email", li: "LinkedIn", soon: "Photo coming soon", ops: "24/7 Operations Line", email: "Email", opsMail: "Operations", address: "Head Office", map: "Open in maps", office: "Phone" },
};

const initials = (name) => name.split(/\s+/).filter(Boolean).map((p) => p[0]).slice(0, 2).join("").toLocaleUpperCase("tr");
const title = (m, lang) => m[`unvan_${lang}`] || m.unvan_tr || "";
// yer tutucu (henüz isimsiz) kadrolar sitede gösterilmez
export const people = (data) => (data.ekip || []).filter((m) => !m.yer_tutucu);

function photo(m, lang, base, cls = "") {
  return m.foto
    ? `<img class="${cls}" src="${base}assets/img/ekip/${esc(m.foto)}" alt="${esc(m.ad)} – ${esc(title(m, lang))}" loading="lazy" decoding="async" width="720" height="900">`
    : `<div class="ph ${cls}" aria-hidden="true"><span>${esc(initials(m.ad))}</span></div>`;
}

// Zeymarine tarzı kişi kartı: dikey portre · isim · unvan · yuvarlak ikonlar · kısa tanıtım · "Detaylar"
// Detay içeriği <template> içinde durur; main.js ortak pencerede gösterir.
export function renderPeople(data, lang, base = "", headingTag = "h3", limit = 0) {
  const t = T[lang];
  const list = people(data);
  return (limit > 0 ? list.slice(0, limit) : list).map((m, i) => {
    const icons = [
      m.eposta && `<a href="mailto:${esc(m.eposta)}" aria-label="${t.mail}: ${esc(m.ad)}" title="${esc(m.eposta)}">${ICON.mail}</a>`,
      m.telefon && `<a href="tel:${tel(m.telefon)}" aria-label="${t.call}: ${esc(m.ad)}" title="${esc(m.telefon)}">${ICON.phone}</a>`,
      m.linkedin && `<a href="${url(m.linkedin)}" target="_blank" rel="noopener" aria-label="${t.li}: ${esc(m.ad)}">${ICON.linkedin}</a>`,
    ].filter(Boolean).join("");
    const bio = m[`tanitim_${lang}`] || m.tanitim_tr || "";
    const long = m[`detay_${lang}`] || m.detay_tr || bio;
    const H = headingTag;
    return `<article class="pp reveal" style="--d:${(i % 3) * 90}ms">
  <div class="pp-photo">${photo(m, lang, base)}</div>
  <div class="pp-body">
    <${H} class="pp-name">${esc(m.ad)}</${H}>
    <p class="pp-title">${esc(title(m, lang))}</p>
    ${icons ? `<div class="pp-icons">${icons}</div>` : ""}
    ${bio ? `<p class="pp-bio">${esc(bio)}</p>` : ""}
    <button class="pp-more" type="button" data-person>${t.details} <span aria-hidden="true">›</span></button>
  </div>
  <template data-person-detail>
    <div class="pd-photo">${photo(m, lang, base)}</div>
    <div class="pd-body">
      <p class="pd-title">${esc(title(m, lang))}</p>
      <h2 class="pd-name">${esc(m.ad)}</h2>
      ${long ? `<p class="pd-bio">${esc(long)}</p>` : ""}
      <ul class="pd-contact">
        ${m.eposta ? `<li>${ICON.mail}<a href="mailto:${esc(m.eposta)}">${esc(m.eposta)}</a></li>` : ""}
        ${m.telefon ? `<li>${ICON.phone}<a href="tel:${tel(m.telefon)}">${esc(m.telefon)}</a></li>` : ""}
        ${m.linkedin ? `<li>${ICON.linkedin}<a href="${url(m.linkedin)}" target="_blank" rel="noopener">LinkedIn</a></li>` : ""}
      </ul>
    </div>
  </template>
</article>`;
  }).join("\n");
}

// İletişim bilgileri (SAS tarzı: adres · e-posta · telefon)
export function renderContact(data, lang) {
  const t = T[lang];
  const f = data.firma || {};
  const hq = (data.ofisler || []).find((o) => o.goster !== false) || {};
  const addr = hq[`adres_${lang}`] || hq.adres_tr;
  return [
    addr && `<li>${ICON.pin}<div><small>${t.address}</small><span>${esc(addr)}</span>${hq.harita ? `<a href="${url(hq.harita)}" target="_blank" rel="noopener">${t.map} →</a>` : ""}</div></li>`,
    hq.telefon && hq.telefon !== f.operasyon_telefon_7_24 && `<li>${ICON.phone}<div><small>${t.office}</small><a href="tel:${tel(hq.telefon)}">${esc(hq.telefon)}</a></div></li>`,
    f.eposta && `<li>${ICON.mail}<div><small>${t.email}</small><a href="mailto:${esc(f.eposta)}">${esc(f.eposta)}</a></div></li>`,
    f.operasyon_eposta && `<li>${ICON.mail}<div><small>${t.opsMail}</small><a href="mailto:${esc(f.operasyon_eposta)}">${esc(f.operasyon_eposta)}</a></div></li>`,
    f.operasyon_telefon_7_24 && `<li class="ci-ops">${ICON.clock}<div><small>${t.ops}</small><a href="tel:${tel(f.operasyon_telefon_7_24)}">${esc(f.operasyon_telefon_7_24)}</a></div></li>`,
  ].filter(Boolean).join("\n");
}
