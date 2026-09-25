"""Natural Earth verisinden (kamu malı) 3B maket için kara ve derinlik katmanlarını üretir.

Kullanım: python3 tools/harita3d.py <natural-earth-geojson-klasörü>
Çıktı: assets/data/maket.json
Koordinatlar: x = doğu (boylam farkı × cos(39°)), y = kuzey (enlem farkı); 1 birim ≈ 1 enlem derecesi.
"""
import json, math, sys
from pathlib import Path
from shapely.geometry import shape, box, Polygon
from shapely.ops import unary_union

GEO = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets/data/maket.json"
LON0, LON1, LAT0, LAT1 = 23.0, 44.5, 33.6, 44.8
LONC, LATC = 33.5, 39.0
K = math.cos(math.radians(LATC))
BB = box(LON0, LAT0, LON1, LAT1)
TOL = 0.014

def load(name):
    return [shape(f["geometry"]) for f in json.loads((GEO / f"{name}.geojson").read_text())["features"]]

def polys(g, tol=TOL, min_area=4e-4):
    g = g.intersection(BB).simplify(tol, preserve_topology=True)
    ps = [g] if isinstance(g, Polygon) else [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]
    out = []
    for p in ps:
        if p.area < min_area:
            continue
        ring = lambda cs: [[round((x - LONC) * K, 3), round(y - LATC, 3)] for x, y in list(cs)[:-1]]
        out.append([ring(p.exterior.coords)] + [ring(i.coords) for i in p.interiors if Polygon(i).area > min_area])
    return out

land = unary_union([g for g in load("ne_10m_land") if g.intersects(BB)])
tur = [shape(f["geometry"]) for f in json.loads((GEO / "ne_10m_admin_0_countries.geojson").read_text())["features"] if f["properties"]["ADM0_A3"] == "TUR"][0]
tur = tur.intersection(land)
d = {k: unary_union([g for g in load(f"ne_10m_bathymetry_{k}") if g.intersects(BB)]).intersection(BB) for k in ("K_200", "J_1000", "I_2000")}
sea = BB.difference(land)
out = {
    "bbox": [round((LON0 - LONC) * K, 3), round(LAT0 - LATC, 3), round((LON1 - LONC) * K, 3), round(LAT1 - LATC, 3)],
    "proj": {"lonc": LONC, "latc": LATC, "k": K},
    "turkiye": polys(tur),
    "komsu": polys(land.difference(tur)),
    "derinlik": [
        polys(sea.difference(d["K_200"])),            # 0–200 m
        polys(d["K_200"].difference(d["J_1000"])),    # 200–1000 m
        polys(d["J_1000"].difference(d["I_2000"])),   # 1000–2000 m
        polys(d["I_2000"]),                           # 2000 m+
    ],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, separators=(",", ":")))
n = lambda ps: sum(len(r) for p in ps for r in p)
print(OUT, f"{OUT.stat().st_size/1024:.0f} KB", "noktalar:", n(out["turkiye"]), n(out["komsu"]), [n(x) for x in out["derinlik"]])
