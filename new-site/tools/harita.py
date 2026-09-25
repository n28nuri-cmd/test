"""Natural Earth verisinden (kamu malı) Türkiye kıyıları deniz haritası SVG'si üretir.

Kullanım: python3 tools/harita.py <natural-earth-geojson-klasörü>
Çıktı: assets/img/harita.svg (sadece zemin: kara, sığ su, derinlik eğrileri, grid).
Limanlar ve etiketler index.html içinde ayrı katmandır (tıklanabilir olmaları için).
"""
import json, math, sys
from pathlib import Path
from shapely.geometry import shape, box, MultiPolygon, Polygon, LineString, MultiLineString
from shapely.ops import unary_union

GEO = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets/img/harita.svg"
LON0, LON1, LAT0, LAT1 = 25.4, 42.0, 35.55, 42.45
K = math.cos(math.radians(39))
W = 1200
SC = W / ((LON1 - LON0) * K)
H = round((LAT1 - LAT0) * SC)
BB = box(LON0, LAT0, LON1, LAT1)

def xy(lon, lat):
    return (lon - LON0) * K * SC, (LAT1 - lat) * SC

def ring(coords):
    pts = [xy(*c[:2]) for c in coords]
    out, last = [], None
    for x, y in pts:
        p = (round(x, 1), round(y, 1))
        if p != last:
            out.append(p); last = p
    if len(out) < 3:
        return ""
    return "M" + " ".join(f"{x},{y}" for x, y in out) + "Z"

def poly_d(g, tol):
    g = g.intersection(BB).simplify(tol, preserve_topology=True)
    polys = [g] if isinstance(g, Polygon) else [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]
    d = []
    for p in polys:
        if p.area < 1e-4:
            continue
        d.append(ring(p.exterior.coords))
        d += [ring(i.coords) for i in p.interiors if Polygon(i).area > 1e-4]
    return "".join(d)

def load(name):
    return json.loads((GEO / f"{name}.geojson").read_text())["features"]

land = unary_union([shape(f["geometry"]) for f in load("ne_10m_land") if shape(f["geometry"]).intersects(BB)])
tur = [shape(f["geometry"]) for f in load("ne_10m_admin_0_countries") if f["properties"]["ADM0_A3"] == "TUR"][0]
def bathy(name):
    return unary_union([shape(f["geometry"]) for f in load(name) if shape(f["geometry"]).intersects(BB)])
d200, d1000, d2000 = bathy("ne_10m_bathymetry_K_200"), bathy("ne_10m_bathymetry_J_1000"), bathy("ne_10m_bathymetry_I_2000")
sea = BB.difference(land)
shallow = sea.difference(d200)  # 0–200 m

tol = 0.012
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
    '<style>.s{fill:#dcebf3}.l{fill:#eceae4;stroke:#9aa6b0;stroke-width:.6}.t{fill:#e2ded3;stroke:#5d7384;stroke-width:.8}'
    '.c{fill:none;stroke:#8fb6cf;stroke-width:.6}.c2{fill:none;stroke:#a9c8db;stroke-width:.5;stroke-dasharray:3 3}'
    '.g{stroke:#b9c9d4;stroke-width:.5}</style>',
    f'<rect width="{W}" height="{H}" fill="#f4f7f8"/>',
    f'<path class="s" d="{poly_d(shallow, tol)}"/>',
]
for g, cls in ((d1000, "c"), (d2000, "c2")):
    b = g.intersection(BB).boundary.difference(BB.exterior.buffer(0.01)).simplify(tol)
    lines = [b] if isinstance(b, LineString) else [l for l in getattr(b, "geoms", [])]
    dd = "".join("M" + " ".join(f"{round(x,1)},{round(y,1)}" for x, y in (xy(*c) for c in l.coords)) for l in lines if l.length > .15)
    parts.append(f'<path class="{cls}" d="{dd}"/>')
parts.append(f'<path class="l" d="{poly_d(land.difference(tur), tol)}"/>')
parts.append(f'<path class="t" d="{poly_d(tur.intersection(land.buffer(0)), tol)}"/>')
# enlem/boylam çizgileri (haritanın gerçek koordinat ağı)
for lon in range(26, 43, 2):
    x = xy(lon, 0)[0]; parts.append(f'<line class="g" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/>')
for lat in range(36, 44, 1):
    y = xy(0, lat)[1]; parts.append(f'<line class="g" x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
parts.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(parts))
json.dump({"W": W, "H": H, "LON0": LON0, "LAT1": LAT1, "K": K, "SC": SC}, open(OUT.with_suffix(".json"), "w"))
print(OUT, f"{OUT.stat().st_size/1024:.0f} KB", W, H)
