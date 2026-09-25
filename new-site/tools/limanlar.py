"""Liman listesini haritadaki konumlarıyla index.html'e yazar.

index.html içindeki <!-- limanlar --> ... <!-- /limanlar --> (harita işaretleri) ve
<!-- liman-secenek --> ... <!-- /liman-secenek --> (formdaki seçenekler) arası yeniden üretilir.
Konumlar tools/harita.py'nin kullandığı projeksiyonla hesaplanır (assets/img/harita.json).

Kullanım: python3 tools/limanlar.py
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "assets/img/harita.json").read_text())

# ad, enlem, boylam, bölge, etiket yönü (r/l/t/b), sürekli etiketli mi
LIMANLAR = [
    ("İstanbul Boğazı", 41.12, 29.06, "Marmara ve Boğazlar", "r", True),
    ("Çanakkale Boğazı", 40.15, 26.41, "Marmara ve Boğazlar", "b", True),
    ("Ambarlı", 40.97, 28.69, "Marmara ve Boğazlar", "", False),
    ("Tuzla", 40.82, 29.29, "Marmara ve Boğazlar", "", False),
    ("Dilovası", 40.77, 29.53, "Marmara ve Boğazlar", "", False),
    ("İzmit Körfezi", 40.75, 29.83, "Marmara ve Boğazlar", "", False),
    ("Yalova", 40.66, 29.28, "Marmara ve Boğazlar", "", False),
    ("Gemlik", 40.43, 29.11, "Marmara ve Boğazlar", "", False),
    ("Bandırma", 40.36, 27.97, "Marmara ve Boğazlar", "", False),
    ("Tekirdağ", 40.97, 27.51, "Marmara ve Boğazlar", "", False),
    ("Marmara Ereğlisi", 40.97, 27.95, "Marmara ve Boğazlar", "", False),
    ("Gelibolu", 40.41, 26.67, "Marmara ve Boğazlar", "", False),
    ("Karabiga", 40.40, 27.31, "Marmara ve Boğazlar", "", False),
    ("Karadeniz Ereğli", 41.28, 31.42, "Karadeniz", "", False),
    ("Zonguldak", 41.46, 31.79, "Karadeniz", "", False),
    ("Filyos", 41.57, 32.03, "Karadeniz", "br", True),
    ("Bartın", 41.69, 32.23, "Karadeniz", "", False),
    ("İnebolu", 41.98, 33.76, "Karadeniz", "", False),
    ("Sinop", 42.02, 35.15, "Karadeniz", "", False),
    ("Samsun", 41.29, 36.34, "Karadeniz", "b", True),
    ("Ordu", 40.98, 37.88, "Karadeniz", "", False),
    ("Giresun", 40.92, 38.39, "Karadeniz", "", False),
    ("Trabzon", 41.00, 39.73, "Karadeniz", "b", True),
    ("Rize", 41.03, 40.52, "Karadeniz", "l", False),
    ("Hopa", 41.41, 41.42, "Karadeniz", "l", False),
    ("Dikili", 39.07, 26.89, "Ege", "", False),
    ("Aliağa", 38.80, 26.97, "Ege", "r", True),
    ("İzmir", 38.44, 27.15, "Ege", "r", True),
    ("Çeşme", 38.32, 26.30, "Ege", "", False),
    ("Kuşadası", 37.86, 27.26, "Ege", "", False),
    ("Güllük", 37.24, 27.60, "Ege", "", False),
    ("Bodrum", 37.03, 27.43, "Ege", "", False),
    ("Marmaris", 36.85, 28.27, "Akdeniz", "", False),
    ("Fethiye", 36.62, 29.10, "Akdeniz", "", False),
    ("Antalya", 36.83, 30.61, "Akdeniz", "t", True),
    ("Alanya", 36.54, 32.00, "Akdeniz", "", False),
    ("Taşucu", 36.32, 33.88, "Akdeniz", "", False),
    ("Mersin", 36.79, 34.63, "Akdeniz", "t", True),
    ("Yumurtalık", 36.77, 35.79, "Akdeniz", "", False),
    ("Ceyhan (BOTAŞ)", 36.88, 35.93, "Akdeniz", "", False),
    ("İskenderun", 36.59, 36.18, "Akdeniz", "r", True),
]
# Özel noktalar: merkez ofis ve operasyon üssü
OFIS = {"İstanbul Boğazı": "Merkez ofis: Beykoz, İstanbul", "Filyos": "Operasyon üssü"}

def pos(lat, lon):
    x = (lon - P["LON0"]) * P["K"] * P["SC"] / P["W"] * 100
    y = (P["LAT1"] - lat) * P["SC"] / P["H"] * 100
    return x, y

isaret, secenek, bolge = [], [], None
for i, (ad, lat, lon, b, yon, sabit) in enumerate(LIMANLAR):
    x, y = pos(lat, lon)
    cls = ["port"] + ([f"lbl-{yon}"] if yon else []) + (["sabit"] if sabit else []) + (["ofis"] if ad in OFIS else [])
    not_ = f'<span class="port-not">{html.escape(OFIS[ad])}</span>' if ad in OFIS else ""
    isaret.append(
        f'<a class="{" ".join(cls)}" href="?liman={html.escape(ad)}#proforma" data-liman="{html.escape(ad)}" '
        f'style="--x:{x:.2f}%;--y:{y:.2f}%;--i:{i}"><span class="port-ad">{html.escape(ad)}{not_}</span></a>'
    )
    if b != bolge:
        if bolge:
            secenek.append("</optgroup>")
        secenek.append(f'<optgroup label="{b}">'); bolge = b
    secenek.append(f"<option>{html.escape(ad)}</option>")
secenek.append("</optgroup>")

f = ROOT / "index.html"
s = f.read_text(encoding="utf-8")
def yaz(s, etiket, icerik, girinti):
    return re.sub(rf"(<!-- {etiket} -->).*?(\s*<!-- /{etiket} -->)",
                  lambda m: m.group(1) + "".join(f"\n{girinti}{c}" for c in icerik) + m.group(2), s, flags=re.S)
s = yaz(s, "limanlar", isaret, "        ")
s = yaz(s, "liman-secenek", secenek, "              ")
f.write_text(s, encoding="utf-8")
print(len(LIMANLAR), "liman yazıldı")
