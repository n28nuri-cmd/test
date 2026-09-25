# Yeni site

Yeni sitenin çalışma alanı. Yayındaki site `../eski-site/` klasöründe saklanıyor.

## Yapı
- `index.html` – ana sayfa (Türkçe). İngilizce ve diğer sayfalar sonra eklenecek.
- `assets/css/site.css`, `assets/js/site.js` – tasarım ve etkileşim
- `assets/img/harita.svg` – deniz haritası zemini; `python3 tools/harita.py <natural-earth-klasörü>` ile üretilir
- `tools/limanlar.py` – liman listesini ve haritadaki konumlarını index.html'e yazar (liman eklemek/çıkarmak için burayı düzenleyin)
