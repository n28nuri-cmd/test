"""Hizmet sayfalarını (Filyos, Boğaz Geçişleri) TR/EN üretir.

Üst menü, footer ve mobil çubuk, mevcut Ekibimiz sayfalarından birebir alınır; böylece
site genelindeki değişiklikler (menü, iletişim bilgileri, sürüm numarası) yeni sayfalara da yansır.
Kullanım:  python3 natro/sayfalar.py
"""
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "esea-site"
BASE_URL = "https://eseaagency.com/"
ARROW = '<svg class="arr" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>'

PAGES = [
    # ---------------------------------------------------------------- FİLYOS
    {
        "key": "filyos",
        "tr": {
            "file": "filyos-liman-acenteligi.html",
            "title": "Filyos Liman Acenteliği | ESEA Agency",
            "desc": "Filyos Limanı'nda gemi acenteliği: offshore destek gemileri, mürettebat değişimi, yedek parça gümrükleme ve 7/24 saha ekibi.",
            "crumb": "Filyos Liman Acenteliği",
            "h1": "Filyos Liman Acenteliği",
            "lead": "Karadeniz enerji projelerinin kıyıdaki merkezinde, sahada kendi ekibimizle 7/24 yanınızdayız.",
            "cover": ("proje/fpu-osman-gazi-filyos", "Filyos Limanı'nda FPU Osman Gazi"),
            "intro_kicker": "Filyos Operasyon Üssü",
            "intro_h2": "Batı Karadeniz'in enerji limanında yerel ekip, tek muhatap",
            "intro": [
                "Zonguldak'ın Çaycuma ilçesinde, Filyos Vadisi Projesi kapsamında 2021'de hizmete giren Filyos Limanı, Sakarya Gaz Sahası'nın kara tesisleriyle birlikte Karadeniz'deki derin deniz enerji projelerinin en önemli lojistik üssü haline geldi.",
                "ESEA Agency olarak Filyos'taki operasyon ofisimiz ve sahadaki ekibimizle sondaj gemileri, yüzer üretim tesisleri ve bunlara hizmet veren offshore destek filoları için liman, gümrük, lojistik ve personel süreçlerini kesintisiz yönetiyoruz.",
            ],
            "intro_img": ("proje/filyos-bakim-merkezi", "Filyos'taki offshore bakım ve lojistik sahası"),
            "svc_kicker": "Filyos'ta Hizmetlerimiz",
            "svc_h2": "Liman uğrağından proje lojistiğine kadar",
            "services": [
                ("Liman Uğrağı Acenteliği", "Varış öncesi bildirimler, rıhtım ve kılavuzluk planlaması, liman ve kamu kurumlarıyla koordinasyon; proformadan (PDA) kesin hesaba (FDA) şeffaf maliyet kontrolü."),
                ("Offshore Destek Filosu", "PSV, AHTS ve ekip botları için sık uğrak yönetimi, rıhtım planlaması, yakıt, su ve kumanya ikmali, saha ile liman arasındaki lojistik akışın koordinasyonu."),
                ("Mürettebat Değişimi", "Vize ve pasaport işlemleri, havalimanı transferleri, konaklama ve offshore transferler; süpervizör, sörvey ve denetim personeli için eksiksiz organizasyon."),
                ("Yedek Parça ve Gümrük", "Yurt dışından gelen kritik yedek parça ve ekipmanın transit ve gümrük işlemleri, antrepodan teslim alma, depolama ve gemiye güvenli teslim."),
                ("Proje Kargo", "Boru, sualtı yapıları ve ağır ekipman için liman elleçlemesi, vinç ve saha planlaması, depolama ve karayolu taşıması."),
                ("Koruyucu Acentelik", "Kiracı acentesi atandığında armatörün bağımsız temsilcisi olarak masraf kontrolü, kaptana nakit ödemesi ve armatör işlerinin takibi."),
            ],
            "why_kicker": "Neden ESEA",
            "why_h2": "Filyos'ta sahada olmanın farkı",
            "why": [
                "Filyos Operasyon Müdürümüz ve saha ekibimizle liman içinde doğrudan temas",
                "DS Fatih, DS Abdülhamid Han ve FPU Osman Gazi projelerindeki sahaya dayalı deneyim",
                "Liman idaresi, gümrük, terminal ve onaylı tedarikçilerle kurulu çalışma düzeni",
                "Zonguldak, Karadeniz Ereğli ve Bartın limanlarında da aynı ekip ve standart",
                "7/24 ulaşılabilir operasyon desteği ve şeffaf proforma",
            ],
            "faq_h2": "Sık sorulan sorular",
            "faq": [
                ("Filyos Limanı nerede?", "Filyos Limanı, Batı Karadeniz'de, Zonguldak'ın Çaycuma ilçesindedir. Filyos Vadisi Projesi kapsamında inşa edilmiş ve 2021'de hizmete girmiştir."),
                ("Filyos'ta hangi gemi tiplerine hizmet veriyorsunuz?", "Sondaj gemileri, yüzer üretim tesisleri (FPU), yarı dalgıç platformlar, PSV/AHTS filoları, boru döşeme ve sualtı inşaat gemileri ile genel yük ve dökme yük gemilerine acentelik hizmeti veriyoruz."),
                ("Proforma (PDA) talebi nasıl iletilir?", "Gemi adı veya IMO numarası, tahmini varış tarihi (ETA) ve talep ettiğiniz hizmetleri iletişim formumuzla ya da agency@eseaagency.com adresine göndermeniz yeterlidir; ekibimiz en kısa sürede dönüş yapar."),
                ("Filyos dışındaki Karadeniz limanlarında da hizmet veriyor musunuz?", "Evet. Zonguldak, Karadeniz Ereğli, Bartın, İnebolu, Sinop, Samsun, Trabzon ve diğer tüm Türk limanlarında hizmet veriyoruz."),
            ],
            "cta": "Filyos'a uğrayacak geminiz için proforma talebinizi iletin; ekibimiz en kısa sürede dönüş yapsın.",
            "cta_btn": "Proforma Talebi",
            "related": ("Boğaz Geçişleri", "bogaz-gecisleri.html"),
            "related_label": "İlgili hizmet",
            "service_type": "Liman acenteliği",
        },
        "en": {
            "file": "en/filyos-port-agency.html",
            "title": "Filyos Port Agency | ESEA Agency",
            "desc": "Ship agency at Filyos Port, Türkiye: offshore support vessels, crew changes, spare parts clearance and a 24/7 local team on site.",
            "crumb": "Filyos Port Agency",
            "h1": "Filyos Port Agency",
            "lead": "At the shore base of the Black Sea energy projects, with our own team on the ground around the clock.",
            "cover": ("proje/fpu-osman-gazi-filyos", "FPU Osman Gazi at Filyos Port"),
            "intro_kicker": "Filyos Operations Base",
            "intro_h2": "A local team and a single point of contact at the Western Black Sea's energy port",
            "intro": [
                "Located in Çaycuma, Zonguldak, and opened in 2021 as part of the Filyos Valley Project, Filyos Port has become — together with the onshore facilities of the Sakarya Gas Field — the key logistics base for the deepwater energy projects in the Black Sea.",
                "From our operations office in Filyos, ESEA Agency manages port, customs, logistics and personnel matters without interruption for drillships, floating production units and the offshore support fleets that serve them.",
            ],
            "intro_img": ("proje/filyos-bakim-merkezi", "Offshore maintenance and logistics yard at Filyos"),
            "svc_kicker": "Our Services at Filyos",
            "svc_h2": "From port calls to project logistics",
            "services": [
                ("Port Call Agency", "Pre-arrival notices, berth and pilotage planning, coordination with the port and authorities, and transparent cost control from proforma (PDA) to final disbursement account (FDA)."),
                ("Offshore Support Fleet", "Management of frequent calls by PSVs, AHTS vessels and crew boats: berth planning, bunkers, fresh water and provisions, and coordination of the logistics flow between field and port."),
                ("Crew Changes", "Visa and immigration formalities, airport transfers, accommodation and offshore transfers, with full arrangements for superintendents, surveyors and inspectors."),
                ("Spare Parts & Customs", "Transit and customs clearance of critical spare parts and equipment arriving from abroad, collection from bonded warehouses, storage and safe delivery on board."),
                ("Project Cargo", "Port handling, crane and yard planning, storage and onward road transport for pipes, subsea structures and heavy equipment."),
                ("Protective Agency", "Where the agent is appointed by charterers, we act as the owner's independent representative: disbursement control, cash to master and owners' matters."),
            ],
            "why_kicker": "Why ESEA",
            "why_h2": "The difference of being on site at Filyos",
            "why": [
                "Direct presence in the port through our Filyos Operations Manager and field team",
                "Hands-on experience from the DS Fatih, DS Abdülhamid Han and FPU Osman Gazi projects",
                "Established working relationships with the harbour master, customs, terminal and approved suppliers",
                "The same team and standards at Zonguldak, Karadeniz Ereğli and Bartın",
                "24/7 operational support and transparent proformas",
            ],
            "faq_h2": "Frequently asked questions",
            "faq": [
                ("Where is Filyos Port?", "Filyos Port is on Türkiye's Western Black Sea coast, in the Çaycuma district of Zonguldak. It was built as part of the Filyos Valley Project and opened in 2021."),
                ("Which vessel types do you serve at Filyos?", "We act as agents for drillships, floating production units (FPU), semi-submersibles, PSV/AHTS fleets, pipelay and subsea construction vessels, as well as general cargo and dry bulk ships."),
                ("How do I request a proforma (PDA)?", "Send us the vessel name or IMO number, the estimated time of arrival (ETA) and the services required via our contact form or to agency@eseaagency.com — our team will respond promptly."),
                ("Do you also cover other Black Sea ports?", "Yes. We serve Zonguldak, Karadeniz Ereğli, Bartın, İnebolu, Sinop, Samsun, Trabzon and every other Turkish port."),
            ],
            "cta": "Send us your proforma request for your vessel's call at Filyos and our team will respond promptly.",
            "cta_btn": "Request a PDA",
            "related": ("Turkish Straits Transit", "turkish-straits-transit.html"),
            "related_label": "Related service",
            "service_type": "Port agency",
        },
    },
    # ---------------------------------------------------------------- BOĞAZ
    {
        "key": "bogaz",
        "tr": {
            "file": "bogaz-gecisleri.html",
            "title": "İstanbul ve Çanakkale Boğazı Geçiş Acenteliği | ESEA Agency",
            "desc": "İstanbul ve Çanakkale Boğazı geçişlerinde acentelik: VTS bildirimleri, kılavuz ve römorkör rezervasyonu, geçişte ikmal ve 7/24 takip.",
            "crumb": "Boğaz Geçişleri",
            "h1": "Boğaz Geçişleri",
            "lead": "İstanbul ve Çanakkale Boğazlarından güvenli ve planlandığı gibi geçiş için baştan sona koordinasyon.",
            "cover": ("foto/px-bogaz-kopru-tanker", "İstanbul Boğazı'nda köprü altından geçen tanker"),
            "intro_kicker": "Türk Boğazları",
            "intro_h2": "Dünyanın en yoğun ve en dar su yollarında deneyimli acente",
            "intro": [
                "Karadeniz'i Marmara üzerinden Akdeniz'e bağlayan Türk Boğazları, yaklaşık 30 km uzunluğundaki ve en dar yerinde 700 metreye kadar daralan İstanbul Boğazı ile 68 km uzunluğundaki Çanakkale Boğazı'ndan oluşur. Ticari gemilerin barış zamanında serbest geçişi 1936 tarihli Montrö Sözleşmesi ile güvence altındadır.",
                "Yoğun trafik, akıntılar ve sıkı trafik düzeni, geçişin dikkatle planlanmasını gerektirir. ESEA Agency olarak bildirimlerden kılavuz ve römorkör rezervasyonuna, bekleme sürecinden geçiş sırasındaki ikmale kadar tüm süreci tek elden yönetiyoruz.",
            ],
            "intro_img": ("foto/istanbul-bogazi", "İstanbul Boğazı ve şehir silüeti"),
            "steps_kicker": "Nasıl Çalışıyoruz",
            "steps_h2": "Geçiş süreci adım adım",
            "steps": [
                ("Proforma ve ön bilgi", "Gemi bilgileri ve seyir planı üzerine geçiş maliyetlerini içeren proformayı (PDA) hazırlar, gerekli belgeleri önceden kontrol ederiz."),
                ("Bildirimler ve VTS koordinasyonu", "Seyir Planı (SP-1 ve SP-2) bildirimlerini zamanında yapar, Türk Boğazları Gemi Trafik Hizmetleri (VTS) ve liman başkanlıklarıyla koordinasyonu sağlarız."),
                ("Kılavuz ve römorkör", "Kılavuz kaptan ve gerektiğinde römorkör rezervasyonlarını yapar, gemi boyutu ve yüküne göre gereken düzenlemeleri takip ederiz."),
                ("Bekleme ve demir yeri", "Sıra ve demir yeri durumunu izler, olası beklemelerde armatörü ve kaptanı düzenli olarak bilgilendiririz."),
                ("Geçiş ve kapanış", "Geçiş boyunca 7/24 operasyon desteği verir, geçiş sonrasında kesin hesabı (FDA) şeffaf şekilde sunarız."),
            ],
            "svc_kicker": "Geçiş Sırasında Hizmetler",
            "svc_h2": "Boğazdan geçerken ihtiyaç duyduğunuz her şey",
            "services": [
                ("Yakıt, Kumanya ve İkmal", "İstanbul ve Çanakkale demir yerlerinde yakıt, tatlı su, kumanya ve kaptan malzemesi ikmali, onaylı tedarikçilerle."),
                ("Mürettebat Değişimi", "Geçiş öncesi veya demir yerinde mürettebat değişimi; vize, transfer ve konaklama organizasyonu."),
                ("Yedek Parça Teslimi", "Yedek parçaların gümrük ve transit işlemleri ile demir yerinde veya geçiş öncesinde gemiye teslimi."),
                ("Koruyucu Acentelik", "Kiracı acentesi atandığında armatörün çıkarlarının korunması, masraf kontrolü ve armatör işlerinin takibi."),
            ],
            "why_kicker": "Neden ESEA",
            "why_h2": "Geçişleriniz neden güvende",
            "why": [
                "İstanbul merkez ofisimizden 7/24 geçiş takibi",
                "Tankerler, dökme yük gemileri ve offshore birimlerde geçiş deneyimi",
                "VTS, liman başkanlıkları, kılavuzluk ve römorkör hizmetleriyle kurulu iletişim",
                "Şeffaf proforma ve kesin hesap; sürprizsiz maliyet",
            ],
            "faq_h2": "Sık sorulan sorular",
            "faq": [
                ("Boğaz geçişi için ne kadar önceden bildirim yapılmalı?", "Seyir planı bildirimleri, Türk Boğazları trafik düzenine göre geçişten önce belirli sürelerde yapılmalıdır. Bu nedenle geminizin tahmini varışını (ETA) mümkün olduğunca erken iletmenizi öneririz; zamanlamayı ve bildirimleri biz takip ederiz."),
                ("Kılavuz kaptan zorunlu mu?", "Kılavuzluk, belirli gemiler için zorunlu, diğerleri için ise güçlü bir şekilde tavsiye edilir. Geminizin tipi, boyu ve yüküne göre gereken düzenlemeyi birlikte planlarız."),
                ("Geçiş sırasında ikmal veya mürettebat değişimi yapılabilir mi?", "Evet. İstanbul ve Çanakkale demir yerlerinde yakıt, kumanya ve su ikmali, yedek parça teslimi ve mürettebat değişimi organize ediyoruz."),
                ("Proforma (PDA) talebi nasıl iletilir?", "Gemi adı veya IMO numarası, tahmini varış tarihi, geçiş yönü ve ihtiyaçlarınızı iletişim formumuzla ya da agency@eseaagency.com adresine göndermeniz yeterlidir."),
            ],
            "cta": "Geminiz Boğazlardan mı geçecek? Proforma talebinizi iletin, geçişinizi birlikte planlayalım.",
            "cta_btn": "Proforma Talebi",
            "related": ("Filyos Liman Acenteliği", "filyos-liman-acenteligi.html"),
            "related_label": "İlgili hizmet",
            "service_type": "Boğaz geçiş acenteliği",
        },
        "en": {
            "file": "en/turkish-straits-transit.html",
            "title": "Bosphorus & Dardanelles Transit Agency | ESEA Agency",
            "desc": "Ship agency for Istanbul and Çanakkale Strait transits: VTS reporting, pilot and tug bookings, supplies during transit and 24/7 monitoring.",
            "crumb": "Turkish Straits Transit",
            "h1": "Turkish Straits Transit",
            "lead": "End-to-end coordination for safe, on-schedule passage through the Bosphorus and the Dardanelles.",
            "cover": ("foto/px-bogaz-kopru-tanker", "Tanker passing under a bridge in the Bosphorus"),
            "intro_kicker": "The Turkish Straits",
            "intro_h2": "An experienced agent in some of the world's busiest and narrowest waterways",
            "intro": [
                "Linking the Black Sea to the Mediterranean via the Sea of Marmara, the Turkish Straits consist of the Istanbul Strait (Bosphorus), about 30 km long and as narrow as 700 metres, and the 68 km Çanakkale Strait (Dardanelles). Free passage for merchant vessels in peacetime is guaranteed by the 1936 Montreux Convention.",
                "Dense traffic, strong currents and a strict traffic regime make careful planning essential. ESEA Agency handles the entire process in one hand — from reporting and pilot and tug bookings to waiting times and supplies during the transit.",
            ],
            "intro_img": ("foto/istanbul-bogazi", "The Bosphorus and the Istanbul skyline"),
            "steps_kicker": "How We Work",
            "steps_h2": "The transit, step by step",
            "steps": [
                ("Proforma and pre-arrival", "Based on the vessel particulars and voyage plan, we prepare a proforma (PDA) covering transit costs and check the required documents in advance."),
                ("Reporting and VTS coordination", "We submit the Sailing Plan reports (SP-1 and SP-2) on time and coordinate with the Turkish Straits Vessel Traffic Service (VTS) and the harbour masters."),
                ("Pilots and tugs", "We book the pilot and, where required, tugs, and follow up the arrangements needed for the vessel's size and cargo."),
                ("Waiting and anchorage", "We monitor queue and anchorage status and keep owners and the master regularly informed during any waiting period."),
                ("Transit and closing", "We provide 24/7 operational support throughout the passage and present a transparent final disbursement account (FDA) afterwards."),
            ],
            "svc_kicker": "Services During Transit",
            "svc_h2": "Everything you need on the way through",
            "services": [
                ("Bunkers, Provisions & Supplies", "Bunkers, fresh water, provisions and master's supplies at the Istanbul and Çanakkale anchorages, through approved suppliers."),
                ("Crew Changes", "Crew changes before transit or at anchorage, with visa, transfer and accommodation arrangements."),
                ("Spare Parts Delivery", "Customs and transit clearance of spare parts and delivery on board at anchorage or before the passage."),
                ("Protective Agency", "Where the agent is appointed by charterers, we safeguard owners' interests: disbursement control and owners' matters."),
            ],
            "why_kicker": "Why ESEA",
            "why_h2": "Why your transits are in safe hands",
            "why": [
                "24/7 transit monitoring from our Istanbul head office",
                "Transit experience with tankers, dry bulk carriers and offshore units",
                "Established communication with VTS, harbour masters, pilotage and towage services",
                "Transparent proforma and final accounts — no surprises on cost",
            ],
            "faq_h2": "Frequently asked questions",
            "faq": [
                ("How far in advance must a straits transit be reported?", "Sailing plan reports must be submitted within set time frames before the transit under the Turkish Straits traffic regime. We therefore recommend sharing your vessel's ETA as early as possible — we take care of the timing and the reports."),
                ("Is pilotage compulsory?", "Pilotage is compulsory for certain vessels and strongly recommended for all others. We plan the right arrangements together, based on your vessel's type, length and cargo."),
                ("Can supplies or crew changes be arranged during transit?", "Yes. We arrange bunkers, provisions and water, spare parts deliveries and crew changes at the Istanbul and Çanakkale anchorages."),
                ("How do I request a proforma (PDA)?", "Send us the vessel name or IMO number, ETA, transit direction and your requirements via our contact form or to agency@eseaagency.com."),
            ],
            "cta": "Is your vessel transiting the Straits? Send us your proforma request and let's plan the passage together.",
            "cta_btn": "Request a PDA",
            "related": ("Filyos Port Agency", "filyos-port-agency.html"),
            "related_label": "Related service",
            "service_type": "Strait transit agency",
        },
    },
]

PAIRS = {  # hreflang eşleşmeleri
    "filyos-liman-acenteligi.html": "en/filyos-port-agency.html",
    "bogaz-gecisleri.html": "en/turkish-straits-transit.html",
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def picture(path: str, alt: str, base: str, eager: bool = False, cls: str = "") -> str:
    """Mevcut 960/1920 (veya -lg) varyantlarıyla <picture> üretir; tek boyut varsa onu kullanır."""
    from PIL import Image
    img = SITE / "assets/img"
    if (img / f"{path}-960.jpg").exists():
        small, large = f"{path}-960", f"{path}-1920"
    elif (img / f"{path}-lg.jpg").exists():
        small, large = path, f"{path}-lg"
    else:
        small, large = path, None
    assert (img / f"{small}.jpg").exists(), path
    w, h = Image.open(img / f"{large or small}.jpg").size
    b = f"{base}assets/img/"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    sizes = "100vw" if eager else "(max-width: 900px) 100vw, 50vw"
    if large:
        src_webp = f'srcset="{b}{small}.webp 960w, {b}{large}.webp 1920w" sizes="{sizes}"'
        src_jpg = f'src="{b}{small}.jpg" srcset="{b}{small}.jpg 960w, {b}{large}.jpg 1920w" sizes="{sizes}"'
    else:
        src_webp = f'srcset="{b}{small}.webp"'
        src_jpg = f'src="{b}{small}.jpg"'
    return (f'<picture{c}><source type="image/webp" {src_webp}>'
            f'<img {src_jpg} alt="{esc(alt)}" width="{w}" height="{h}" {load} decoding="async"></picture>')


def build(page_key: str, lang: str, d: dict, other_file: str) -> str:
    tr = lang == "tr"
    base = "" if tr else "../"
    tpl = (SITE / ("ekibimiz.html" if tr else "en/team.html")).read_text(encoding="utf-8")
    url = BASE_URL + d["file"]
    tr_url = BASE_URL + (d["file"] if tr else other_file)
    en_url = BASE_URL + (other_file if tr else d["file"])

    # ---- <head>
    head_end = tpl.index("</head>")
    head = tpl[:head_end]
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(d['title'])}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(d["desc"])}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = re.sub(r'<link rel="alternate" hreflang="tr" href="[^"]*">', f'<link rel="alternate" hreflang="tr" href="{tr_url}">', head)
    head = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{en_url}">', head)
    head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{tr_url}">', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(d["title"])}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(d["desc"])}">', head)
    head = head.replace('<meta name="twitter:card"', f'<meta property="og:url" content="{url}">\n<meta name="twitter:card"', 1)

    home = BASE_URL + ("" if tr else "en/")
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "name": d["h1"], "serviceType": d["service_type"],
         "description": d["desc"], "url": url, "areaServed": {"@type": "Country", "name": "Türkiye"},
         "provider": {"@type": "ProfessionalService", "@id": BASE_URL + "#org", "name": "ESEA Agency", "url": BASE_URL}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ana Sayfa" if tr else "Home", "item": home},
            {"@type": "ListItem", "position": 2, "name": d["crumb"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]},
    ]
    head += "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)

    rest = tpl[head_end:]
    # ---- body sınıfı, dil bağlantısı, menüde aktif sayfa
    rest = rest.replace('class="page-team"', f'class="page-service page-{page_key}"')
    rest = rest.replace(' aria-current="page"', "")
    lang_href = (other_file if tr else "../" + other_file)
    rest = re.sub(r'(<a class="lang" href=")[^"]*(")', lambda m: m.group(1) + lang_href + m.group(2), rest)
    rest = re.sub(r'(<a href=")[^"]*(" hreflang="(?:en|tr)">(?:English|Türkçe)</a>)', lambda m: m.group(1) + lang_href + m.group(2), rest)
    # kişi penceresi bu sayfada yok
    rest = re.sub(r'<dialog class="person-modal".*?</dialog>\n', "", rest, flags=re.S)

    # ---- içerik
    m = []
    m.append(f'''<section class="page-cover">
  {picture(d["cover"][0], "", base, eager=True, cls="pc-bg")}
  <div class="container pc-inner">
    <nav class="crumbs" aria-label="breadcrumb"><a href="{'./' if tr else '../en/'}">{'Ana Sayfa' if tr else 'Home'}</a><span aria-hidden="true">/</span><span aria-current="page">{esc(d["crumb"])}</span></nav>
    <h1>{esc(d["h1"])}</h1>
    <p>{esc(d["lead"])}</p>
  </div>
</section>''')
    m.append(f'''<section class="section sp-intro">
  <div class="container sp-intro-grid">
    <div class="sp-copy">
      <p class="kicker reveal">{esc(d["intro_kicker"])}</p>
      <h2 class="reveal">{esc(d["intro_h2"])}</h2>
      <span class="sec-bar sp-bar reveal" aria-hidden="true"></span>
      {"".join(f'<p class="reveal">{esc(p)}</p>' for p in d["intro"])}
    </div>
    <figure class="sp-media reveal">{picture(d["intro_img"][0], d["intro_img"][1], base)}</figure>
  </div>
</section>''')
    if "steps" in d:
        steps = "".join(f'<li class="sp-step reveal" style="--d:{i*70}ms"><span class="sp-num" aria-hidden="true">{i+1:02d}</span><div><h3>{esc(t)}</h3><p>{esc(x)}</p></div></li>' for i, (t, x) in enumerate(d["steps"]))
        m.append(f'''<section class="section sp-steps-sec">
  <div class="container">
    <header class="sec-head"><p class="kicker reveal">{esc(d["steps_kicker"])}</p><h2 class="reveal">{esc(d["steps_h2"])}</h2><span class="sec-bar reveal" aria-hidden="true"></span></header>
    <ol class="sp-steps">{steps}</ol>
  </div>
</section>''')
    cards = "".join(f'<li class="sp-card reveal" style="--d:{(i%3)*80}ms"><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for i, (t, x) in enumerate(d["services"]))
    m.append(f'''<section class="section sp-svc-sec">
  <div class="container">
    <header class="sec-head"><p class="kicker reveal">{esc(d["svc_kicker"])}</p><h2 class="reveal">{esc(d["svc_h2"])}</h2><span class="sec-bar reveal" aria-hidden="true"></span></header>
    <ul class="sp-cards">{cards}</ul>
  </div>
</section>''')
    why = "".join(f'<li class="reveal">{CHECK}<span>{esc(w)}</span></li>' for w in d["why"])
    faq = "".join(f'<details class="sp-faq-item reveal"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in d["faq"])
    rel_t, rel_href = d["related"]
    m.append(f'''<section class="section sp-why-sec">
  <div class="container sp-why-grid">
    <div>
      <p class="kicker reveal">{esc(d["why_kicker"])}</p>
      <h2 class="reveal">{esc(d["why_h2"])}</h2>
      <ul class="sp-why">{why}</ul>
      <p class="sp-related reveal">{esc(d["related_label"])}: <a href="{rel_href}">{esc(rel_t)} {ARROW}</a></p>
    </div>
    <div>
      <h2 class="sp-faq-h reveal">{esc(d["faq_h2"])}</h2>
      <div class="sp-faq">{faq}</div>
    </div>
  </div>
</section>''')
    m.append(f'''<section class="cta-band">
  <div class="container">
    <h2 class="reveal">{esc(d["cta"])}</h2>
    <div class="cta-btns reveal"><a class="btn btn-light" href="{'./' if tr else '../en/'}#iletisim">{esc(d["cta_btn"])} {ARROW}</a><a class="btn btn-ghost" href="tel:+902165193424">+90 216 519 34 24</a></div>
  </div>
</section>''')
    main = "\n\n".join(m)
    rest = re.sub(r"<main id=\"main\">.*?</main>", lambda _: f'<main id="main">\n\n{main}\n\n</main>', rest, flags=re.S)
    return head + rest


def main():
    for p in PAGES:
        tr, en = p["tr"], p["en"]
        for lang, d, other in (("tr", tr, en["file"]), ("en", en, tr["file"])):
            out = build(p["key"], lang, d, other)
            (SITE / d["file"]).write_text(out, encoding="utf-8")
            print("yazıldı:", d["file"], len(out))


if __name__ == "__main__":
    main()
