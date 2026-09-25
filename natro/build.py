"""esea-site klasöründen Natro'ya yüklenecek canlı sürüm paketini üretir.

Önizlemeye özel ayarları kaldırır (noindex, robots engeli, form önizleme uyarısı),
Netlify dosyasını çıkarır, iletisim.php ve .htaccess ekler, sonucu zip'ler.

Kullanım:  python3 natro/build.py [çıktı.zip]
"""
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "esea-site"
EXTRA = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else EXTRA / "esea-natro.zip"
SKIP = {"netlify.toml"}

# Hiçbir sayfada, CSS/JS'de veya veri dosyasında adı geçmeyen görseller pakete alınmaz.
refs = "".join(
    f.read_text(encoding="utf-8")
    for pat in ("*.html", "en/*.html", "assets/css/*.css", "assets/js/*.js", "assets/data/*.json")
    for f in SRC.glob(pat)
)
UNUSED = {f.relative_to(SRC).as_posix() for f in (SRC / "assets/img").rglob("*") if f.is_file() and f.name not in refs}

def info(name: str) -> zipfile.ZipInfo:
    """Metinden yazılan dosyalar da web sunucusunun okuyabileceği 0644 izniyle çıkarılsın."""
    zi = zipfile.ZipInfo(name, date_time=time.localtime()[:6])
    zi.external_attr = 0o100644 << 16
    zi.compress_type = zipfile.ZIP_DEFLATED
    return zi


with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(SRC.rglob("*")):
        rel = f.relative_to(SRC).as_posix()
        if f.is_dir() or rel in SKIP or rel in UNUSED:
            continue
        if f.suffix == ".html":
            s = f.read_text(encoding="utf-8")
            if rel != "404.html":  # 404 sayfası dizine girmemeli
                s = re.sub(r'<meta name="robots" content="noindex[^"]*">\n?', "", s)
            s = re.sub(r' data-preview="[^"]*"', "", s)
            z.writestr(info(rel), s)
        elif rel == "robots.txt":
            z.writestr(info(rel), "User-agent: *\nAllow: /\n\nSitemap: https://eseaagency.com/sitemap.xml\n")
        else:
            z.write(f, rel)
    for name in ("iletisim.php", ".htaccess"):
        z.write(EXTRA / name, name)

print(OUT, f"{OUT.stat().st_size / 1e6:.1f} MB", f"({len(UNUSED)} kullanılmayan görsel hariç)")
