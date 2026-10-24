import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = "/home/user/Claude/water-tank-upstand"

# ---- geometry (mm) ----
L, W = 8000, 3600          # overall plan
RIB = 200                  # rib width (perimeter + internal)
RIB_H = 200                # AAC / rib height
SLAB_T = 150               # RC topping slab
ROOF_T = 200               # existing roof slab shown for reference only
BAY = (L - 4 * RIB) / 3    # 2400 clear
rib_x = [0, RIB + BAY, 2 * (RIB + BAY), L - RIB]   # left edge of each rib along L
aac_x = [RIB, 2 * RIB + BAY, 3 * RIB + 2 * BAY]    # left edge of each AAC panel

NOTES = [
    "1. All dimensions are in mm unless noted otherwise.",
    "2. Overall upstand size 8000 x 3600 mm, total height 350 mm above existing roof slab.",
    "3. Concrete ribs 200 mm wide x 200 mm high along the full perimeter and at two",
    "   intermediate positions (3 equal bays of 2400 mm clear), cast on the roof slab.",
    "4. AAC block infill, 200 mm thick, laid in the three bays between the ribs.",
    "5. RC topping slab 150 mm thick over the full area, reinforced with one layer of",
    "   6 mm BRC mesh placed at mid-depth, continuous over the ribs.",
    "6. Mesh spacing and concrete grade: TO BE CONFIRMED by the engineer.",
    "7. Existing roof slab shown for reference only; verify its capacity for the tank load.",
]

# ======================================================================
#  MATPLOTLIB  (PDF + PNG, A3 landscape)
# ======================================================================
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.set_aspect("equal"); ax.axis("off")

CONC = dict(facecolor="#d9d9d9", edgecolor="black", lw=0.9, hatch="////")
AAC = dict(facecolor="#f3efe4", edgecolor="black", lw=0.6, hatch="....")
ROOF = dict(facecolor="none", edgecolor="black", lw=0.6, hatch="xx")
WB = dict(boxstyle="square,pad=0.15", fc="white", ec="none")

def rect(x, y, w, h, **kw):
    ax.add_patch(Rectangle((x, y), w, h, **kw))

def dim_h(x1, x2, y, text, fs=6):
    ax.plot([x1, x2], [y, y], color="black", lw=0.5)
    for x in (x1, x2):
        ax.plot([x, x], [y - 1.2, y + 1.2], color="black", lw=0.5)
        ax.plot([x - 0.8, x + 0.8], [y - 0.8, y + 0.8], color="black", lw=0.7)
    ax.text((x1 + x2) / 2, y + 1, text, ha="center", va="bottom", fontsize=fs)

def dim_v(y1, y2, x, text, fs=6):
    ax.plot([x, x], [y1, y2], color="black", lw=0.5)
    for y in (y1, y2):
        ax.plot([x - 1.2, x + 1.2], [y, y], color="black", lw=0.5)
        ax.plot([x - 0.8, x + 0.8], [y - 0.8, y + 0.8], color="black", lw=0.7)
    ax.text(x + 1.2, (y1 + y2) / 2, text, ha="left", va="center", fontsize=fs, rotation=90)

def ext_v(xs, y0, y1):
    for x in xs:
        ax.plot([x, x], [y0, y1], color="black", lw=0.35)

def ext_h(ys, x0, x1):
    for y in ys:
        ax.plot([x0, x1], [y, y], color="black", lw=0.35)

def title(x, y, s):
    ax.text(x, y, s, ha="center", va="bottom", fontsize=9, fontweight="bold")

XS7 = [0, RIB, RIB + BAY, 2 * RIB + BAY, 2 * RIB + 2 * BAY, 3 * RIB + 2 * BAY, 3 * RIB + 3 * BAY, L]
LAB7 = ["200", "2400", "200", "2400", "200", "2400", "200"]

# ---------------- PLAN  1:50 ----------------
S = 50.0; m = lambda v: v / S
px, py = 25, 190
PL, PW = m(L), m(W)
rect(px, py, PL, PW, **CONC)
for x0 in aac_x:
    rect(px + m(x0), py + m(RIB), m(BAY), m(W - 2 * RIB), **AAC)
    ax.text(px + m(x0 + BAY / 2), py + m(W / 2), "AAC BLOCK\n200 THK", ha="center", va="center", fontsize=7, bbox=WB)
ax.text(px + m(RIB / 2), py + PW + 2, "CONC. RIB\n200 WIDE", ha="center", va="bottom", fontsize=5.5)
ax.text(px + m(rib_x[1] + RIB / 2), py + PW + 2, "CONC. RIB\n200 WIDE", ha="center", va="bottom", fontsize=5.5)
xs = [px + m(v) for v in XS7]
ext_v(xs, py - 1, py - 14)
for i, t in enumerate(LAB7):
    dim_h(xs[i], xs[i + 1], py - 6, t, fs=5.5)
dim_h(px, px + PL, py - 13, "8000", fs=6.5)
xv = px + PL + 7
ext_h([py + m(v) for v in (0, RIB, W - RIB, W)], px + PL + 1, xv + 8)
dim_v(py, py + m(RIB), xv, "200", fs=5.5)
dim_v(py + m(RIB), py + m(W - RIB), xv, "3200", fs=5.5)
dim_v(py + m(W - RIB), py + PW, xv, "200", fs=5.5)
dim_v(py, py + PW, xv + 7, "3600", fs=6.5)
def sec_marker(x, y, dx, dy, name):
    ax.plot([x, x + dx], [y, y + dy], color="black", lw=1.2, ls=(0, (6, 2)))
    for (mx, my) in [(x, y), (x + dx, y + dy)]:
        ax.text(mx, my, name, ha="center", va="center", fontsize=7, fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec="black", lw=0.6))
sec_marker(px - 10, py + PW / 2 + 14, PL + 20, 0, "A")
sec_marker(px + m(rib_x[1] + RIB + BAY / 2), py - 22, 0, PW + 36, "B")
title(px + PL / 2, py + PW + 20, "PLAN  (scale 1:50)")

# ---------------- SECTION A-A  1:50 ----------------
sx, sy = 25, 118
rect(sx, sy - m(ROOF_T), PL, m(ROOF_T), **ROOF)
for x0 in rib_x:
    rect(sx + m(x0), sy, m(RIB), m(RIB_H), **CONC)
for x0 in aac_x:
    rect(sx + m(x0), sy, m(BAY), m(RIB_H), **AAC)
rect(sx, sy + m(RIB_H), PL, m(SLAB_T), **CONC)
ym = sy + m(RIB_H + SLAB_T / 2)
ax.plot([sx + m(50), sx + PL - m(50)], [ym, ym], color="red", lw=1.0)
ax.text(sx + PL / 2, sy + m(RIB_H + SLAB_T) + 1.5, "RC SLAB 150 THK c/w 6 mm BRC MESH (1 layer, mid-depth), continuous over ribs",
        ha="center", va="bottom", fontsize=6, color="darkred")
ax.text(sx + m(aac_x[1] + BAY / 2), sy + m(RIB_H / 2), "AAC BLOCK", ha="center", va="center", fontsize=5.5, bbox=WB)
ax.text(sx + m(rib_x[1] + RIB / 2), sy - m(ROOF_T) - 2, "CONC. RIB\n200x200", ha="center", va="top", fontsize=5.5)
ax.text(sx + PL + 2, sy - m(ROOF_T) / 2, "EXISTING ROOF SLAB\n(reference only)", fontsize=5.5, va="center")
ysd = sy - m(ROOF_T) - 14
xs2 = [sx + m(v) for v in XS7]
ext_v(xs2, sy - m(ROOF_T) - 1, ysd - 8)
for i, t in enumerate(LAB7):
    dim_h(xs2[i], xs2[i + 1], ysd, t, fs=5.5)
dim_h(sx, sx + PL, ysd - 7, "8000", fs=6.5)
xv2 = sx + PL + 30
ext_h([sy, sy + m(RIB_H), sy + m(RIB_H + SLAB_T)], sx + PL + 1, xv2 + 8)
dim_v(sy, sy + m(RIB_H), xv2, "200", fs=5.5)
dim_v(sy + m(RIB_H), sy + m(RIB_H + SLAB_T), xv2, "150", fs=5.5)
dim_v(sy, sy + m(RIB_H + SLAB_T), xv2 + 7, "350", fs=6.5)
title(sx + PL / 2, sy + m(RIB_H + SLAB_T) + 8, "SECTION A-A  (scale 1:50)")

# ---------------- SECTION B-B  1:25 ----------------
S = 25.0; m = lambda v: v / S
bx, by = 25, 45
BW = m(W)
rect(bx, by - m(ROOF_T), BW, m(ROOF_T), **ROOF)
rect(bx, by, m(RIB), m(RIB_H), **CONC)
rect(bx + BW - m(RIB), by, m(RIB), m(RIB_H), **CONC)
rect(bx + m(RIB), by, m(W - 2 * RIB), m(RIB_H), **AAC)
rect(bx, by + m(RIB_H), BW, m(SLAB_T), **CONC)
ymb = by + m(RIB_H + SLAB_T / 2)
ax.plot([bx + m(50), bx + BW - m(50)], [ymb, ymb], color="red", lw=1.2)
ax.text(bx + BW / 2, by + m(RIB_H / 2), "AAC BLOCK 200 THK", ha="center", va="center", fontsize=6, bbox=WB)
ax.text(bx + BW / 2, by + m(RIB_H + SLAB_T) + 1.5, "RC SLAB 150 THK c/w 6 mm BRC MESH (1 layer, mid-depth)",
        ha="center", va="bottom", fontsize=6, color="darkred")
ax.text(bx + m(RIB / 2), by + m(RIB_H) + m(SLAB_T) + 8, "CONC. RIB\n200x200", ha="center", va="bottom", fontsize=5.5)
ax.plot([bx + m(RIB / 2), bx + m(RIB / 2)], [by + m(RIB_H / 2), by + m(RIB_H + SLAB_T) + 8], color="black", lw=0.4)
ax.text(bx + BW / 2, by - m(ROOF_T) / 2, "EXISTING ROOF SLAB (reference only)", ha="center", va="center", fontsize=5.5, bbox=WB)
ysb = by - m(ROOF_T) - 8
xs3 = [bx + m(v) for v in (0, RIB, W - RIB, W)]
ext_v(xs3, by - m(ROOF_T) - 1, ysb - 8)
for i, t in enumerate(["200", "3200", "200"]):
    dim_h(xs3[i], xs3[i + 1], ysb, t, fs=5.5)
dim_h(bx, bx + BW, ysb - 7, "3600", fs=6.5)
xv3 = bx + BW + 7
ext_h([by, by + m(RIB_H), by + m(RIB_H + SLAB_T)], bx + BW + 1, xv3 + 8)
dim_v(by, by + m(RIB_H), xv3, "200", fs=5.5)
dim_v(by + m(RIB_H), by + m(RIB_H + SLAB_T), xv3, "150", fs=5.5)
dim_v(by, by + m(RIB_H + SLAB_T), xv3 + 7, "350", fs=6.5)
title(bx + BW / 2, by + m(RIB_H + SLAB_T) + 16, "SECTION B-B  (scale 1:25)")

# ---------------- EDGE DETAIL  1:10 ----------------
S = 10.0; m = lambda v: v / S
dx_, dy_ = 240, 75
DW = 700  # 200 rib + 500 of AAC shown
rect(dx_, dy_ - m(ROOF_T), m(DW), m(ROOF_T), **ROOF)
rect(dx_, dy_, m(RIB), m(RIB_H), **CONC)
rect(dx_ + m(RIB), dy_, m(DW - RIB), m(RIB_H), **AAC)
rect(dx_, dy_ + m(RIB_H), m(DW), m(SLAB_T), **CONC)
# break lines on the cut edge
for yy0, yy1 in [(dy_ - m(ROOF_T), dy_ + m(RIB_H + SLAB_T))]:
    xx = dx_ + m(DW)
    ax.add_patch(Polygon([[xx - 1.5, yy0], [xx + 1.5, yy0 + 8], [xx - 1.5, yy0 + 16], [xx + 1.5, yy0 + 24], [xx - 1.5, yy0 + 32],
                          [xx + 1.5, yy0 + 40], [xx - 1.5, yy0 + 48], [xx + 1.5, yy1 + 1], [xx + 4, yy1 + 1], [xx + 4, yy0 - 1], [xx + 1.5, yy0 - 1]],
                         closed=True, fc="white", ec="none", zorder=5))
    ax.plot([xx - 1.5, xx + 1.5, xx - 1.5, xx + 1.5, xx - 1.5, xx + 1.5, xx - 1.5, xx + 1.5],
            [yy0, yy0 + 8, yy0 + 16, yy0 + 24, yy0 + 32, yy0 + 40, yy0 + 48, yy1 + 1], color="black", lw=0.6, zorder=6)
ymd = dy_ + m(RIB_H + SLAB_T / 2)
ax.plot([dx_ + m(25), dx_ + m(DW)], [ymd, ymd], color="red", lw=1.6)
for xx in [dx_ + m(25) + i * m(150) for i in range(5)]:
    ax.plot(xx, ymd, "o", color="red", ms=2.5)
ax.text(dx_ + m(RIB / 2), dy_ + m(RIB_H / 2), "CONC.\nRIB", ha="center", va="center", fontsize=6, bbox=WB)
ax.text(dx_ + m(RIB + (DW - RIB) / 2), dy_ + m(RIB_H / 2), "AAC BLOCK", ha="center", va="center", fontsize=6.5, bbox=WB)
ax.text(dx_ + m(DW / 2), dy_ - m(ROOF_T) / 2, "EXISTING ROOF SLAB", ha="center", va="center", fontsize=6, bbox=WB)
ax.annotate("6 mm BRC MESH, 1 LAYER\nAT MID-DEPTH OF SLAB\n(25 mm END COVER)", xy=(dx_ + m(350), ymd), xytext=(dx_ + m(DW) + 10, dy_ + m(RIB_H + SLAB_T) + 14),
            fontsize=6, color="darkred", va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color="darkred"))
ax.annotate("RC TOPPING SLAB 150 THK", xy=(dx_ + m(120), dy_ + m(RIB_H + SLAB_T) - 2), xytext=(dx_ - 2, dy_ + m(RIB_H + SLAB_T) + 10),
            fontsize=6, va="center", arrowprops=dict(arrowstyle="-", lw=0.5))
# dims
ydd = dy_ - m(ROOF_T) - 8
ext_v([dx_, dx_ + m(RIB)], dy_ - m(ROOF_T) - 1, ydd - 1.5)
dim_h(dx_, dx_ + m(RIB), ydd, "200", fs=6)
xvd = dx_ - 8
ext_h([dy_, dy_ + m(RIB_H), dy_ + m(RIB_H + SLAB_T)], dx_ - 1, xvd - 8)
dim_v(dy_, dy_ + m(RIB_H), xvd, "200", fs=6)
dim_v(dy_ + m(RIB_H), dy_ + m(RIB_H + SLAB_T), xvd, "150", fs=6)
dim_v(dy_, dy_ + m(RIB_H + SLAB_T), xvd - 7, "350", fs=6.5)
title(dx_ + m(DW / 2), dy_ + m(RIB_H + SLAB_T) + 24, "TYPICAL EDGE DETAIL  (scale 1:10)")

# ---------------- LEGEND ----------------
lx, ly = 225, 240
ax.text(lx, ly + 36, "LEGEND", fontsize=8, fontweight="bold")
rect(lx, ly + 26, 10, 6, **CONC); ax.text(lx + 13, ly + 29, "Reinforced concrete (ribs / topping slab)", va="center", fontsize=6.5)
rect(lx, ly + 16, 10, 6, **AAC);  ax.text(lx + 13, ly + 19, "AAC block infill, 200 mm thick", va="center", fontsize=6.5)
rect(lx, ly + 6, 10, 6, **ROOF);  ax.text(lx + 13, ly + 9, "Existing roof slab (reference)", va="center", fontsize=6.5)
ax.plot([lx, lx + 10], [ly + 1, ly + 1], color="red", lw=1.0); ax.text(lx + 13, ly + 1, "6 mm BRC mesh", va="center", fontsize=6.5)

# ---------------- BORDER + TITLE BLOCK ----------------
rect(8, 8, 404, 281, facecolor="none", edgecolor="black", lw=1.2)
tb_x, tb_y, tb_w, tb_h = 262, 8, 150, 36
rect(tb_x, tb_y, tb_w, tb_h, facecolor="white", edgecolor="black", lw=1.0)
ax.plot([tb_x, tb_x + tb_w], [tb_y + 24, tb_y + 24], color="black", lw=0.6)
ax.plot([tb_x, tb_x + tb_w], [tb_y + 12, tb_y + 12], color="black", lw=0.6)
ax.plot([tb_x + 75, tb_x + 75], [tb_y, tb_y + 24], color="black", lw=0.6)
ax.text(tb_x + tb_w / 2, tb_y + 30, "WATER TANK UPSTAND ON ROOF - PLAN, SECTIONS & DETAIL", ha="center", va="center", fontsize=8, fontweight="bold")
ax.text(tb_x + 2, tb_y + 18, "SCALES: AS NOTED @ A3", fontsize=6.5, va="center")
ax.text(tb_x + 77, tb_y + 18, "UNITS: mm", fontsize=6.5, va="center")
ax.text(tb_x + 2, tb_y + 6, "DATE: 2026-10-24", fontsize=6.5, va="center")
ax.text(tb_x + 77, tb_y + 6, "DWG No: WT-UPS-01   REV: 0", fontsize=6.5, va="center")

fig.savefig(f"{OUT}/water-tank-upstand.pdf")
fig.savefig(f"{OUT}/water-tank-upstand.png", dpi=200)
print("pdf/png ok")

# ======================================================================
#  DXF  (model space, 1 unit = 1 mm)
# ======================================================================
doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
for name, color in [("CONC", 8), ("AAC", 30), ("ROOF", 9), ("MESH", 1), ("DIM", 4), ("TEXT", 7), ("HATCH", 253), ("TITLE", 7), ("SECTION", 6)]:
    doc.layers.add(name, color=color)
ds = doc.dimstyles.get("EZDXF")
ds.dxf.dimtxt = 60; ds.dxf.dimasz = 50; ds.dxf.dimexe = 30; ds.dxf.dimexo = 30; ds.dxf.dimtad = 1; ds.dxf.dimgap = 20; ds.dxf.dimdec = 0; ds.dxf.dimzin = 8; ds.dxf.dimlfac = 1.0

def drect(x, y, w, h, layer, hatch=None, hscale=1.0, hcolor=253):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    if hatch:
        h_ = msp.add_hatch(color=hcolor, dxfattribs={"layer": "HATCH"})
        h_.set_pattern_fill(hatch, scale=hscale)
        h_.paths.add_polyline_path(pts, is_closed=True)

def dtext(x, y, s, h=70, align=TextEntityAlignment.MIDDLE_CENTER, layer="TEXT", rot=0):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "rotation": rot}).set_placement((x, y), align=align)

def dh(x1, x2, y, layer="DIM"):
    msp.add_linear_dim(base=(x1, y), p1=(x1, y), p2=(x2, y), dimstyle="EZDXF", dxfattribs={"layer": layer}).render()

def dv(y1, y2, x, layer="DIM"):
    msp.add_linear_dim(base=(x, y1), p1=(x, y1), p2=(x, y2), angle=90, dimstyle="EZDXF", dxfattribs={"layer": layer}).render()

# PLAN at origin
PX, PY = 0, 0
drect(PX, PY, L, W, "CONC", "ANSI31", 40)
for x0 in aac_x:
    # AAC panel: punch out of concrete hatch by drawing AAC hatch over it (separate panel)
    pts = [(PX + x0, PY + RIB), (PX + x0 + BAY, PY + RIB), (PX + x0 + BAY, PY + W - RIB), (PX + x0, PY + W - RIB)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "AAC"})
    dtext(PX + x0 + BAY / 2, PY + W / 2, "AAC BLOCK 200 THK", 80)
# rebuild concrete hatch properly as ring with islands
msp.delete_entity([e for e in msp if e.dxftype() == "HATCH"][0])
h_ = msp.add_hatch(color=253, dxfattribs={"layer": "HATCH"})
h_.set_pattern_fill("ANSI31", scale=40)
h_.paths.add_polyline_path([(PX, PY), (PX + L, PY), (PX + L, PY + W), (PX, PY + W)], is_closed=True, flags=1)
for x0 in aac_x:
    h_.paths.add_polyline_path([(PX + x0, PY + RIB), (PX + x0 + BAY, PY + RIB), (PX + x0 + BAY, PY + W - RIB), (PX + x0, PY + W - RIB)], is_closed=True, flags=0)
    a = msp.add_hatch(color=30, dxfattribs={"layer": "HATCH"})
    a.set_pattern_fill("DOTS", scale=30)
    a.paths.add_polyline_path([(PX + x0, PY + RIB), (PX + x0 + BAY, PY + RIB), (PX + x0 + BAY, PY + W - RIB), (PX + x0, PY + W - RIB)], is_closed=True)
dtext(PX + RIB / 2, PY + W + 120, "CONC. RIB 200 WIDE", 55)
dtext(PX + rib_x[1] + RIB / 2, PY + W + 120, "CONC. RIB 200 WIDE", 55)
xs_plan = [0, RIB, RIB + BAY, 2 * RIB + BAY, 2 * RIB + 2 * BAY, 3 * RIB + 2 * BAY, 3 * RIB + 3 * BAY, L]
for i in range(7):
    dh(PX + xs_plan[i], PX + xs_plan[i + 1], PY - 300)
dh(PX, PX + L, PY - 600)
for a_, b_ in [(0, RIB), (RIB, W - RIB), (W - RIB, W)]:
    dv(PY + a_, PY + b_, PX + L + 300)
dv(PY, PY + W, PX + L + 600)
# section lines
msp.add_line((PX - 400, PY + W / 2 + 600), (PX + L + 400, PY + W / 2 + 600), dxfattribs={"layer": "SECTION", "linetype": "DASHED"})
for x in (PX - 400, PX + L + 400):
    msp.add_circle((x, PY + W / 2 + 600), 120, dxfattribs={"layer": "SECTION"})
    dtext(x, PY + W / 2 + 600, "A", 120, layer="SECTION")
bxx = PX + rib_x[1] + RIB + BAY / 2
msp.add_line((bxx, PY - 900), (bxx, PY + W + 500), dxfattribs={"layer": "SECTION", "linetype": "DASHED"})
for y in (PY - 900, PY + W + 500):
    msp.add_circle((bxx, y), 120, dxfattribs={"layer": "SECTION"})
    dtext(bxx, y, "B", 120, layer="SECTION")
dtext(PX + L / 2, PY + W + 700, "PLAN", 150, layer="TITLE")

# SECTION A-A below plan
SX, SY = 0, -3500
drect(SX, SY - ROOF_T, L, ROOF_T, "ROOF", "ANSI37", 20)
for x0 in rib_x:
    drect(SX + x0, SY, RIB, RIB_H, "CONC", "ANSI31", 10)
for x0 in aac_x:
    drect(SX + x0, SY, BAY, RIB_H, "AAC", "DOTS", 20, 30)
drect(SX, SY + RIB_H, L, SLAB_T, "CONC", "ANSI31", 10)
msp.add_line((SX + 50, SY + RIB_H + SLAB_T / 2), (SX + L - 50, SY + RIB_H + SLAB_T / 2), dxfattribs={"layer": "MESH", "lineweight": 50})
dtext(SX + L / 2, SY + RIB_H + SLAB_T + 120, "RC SLAB 150 THK c/w 6 mm BRC MESH (1 LAYER, MID-DEPTH)", 70)
dtext(SX + aac_x[1] + BAY / 2, SY + RIB_H / 2, "AAC BLOCK", 60)
dtext(SX + L + 100, SY - ROOF_T / 2, "EXISTING ROOF SLAB (REF.)", 55, TextEntityAlignment.MIDDLE_LEFT)
dtext(SX + rib_x[1] + RIB / 2, SY - ROOF_T - 100, "CONC. RIB 200x200", 55)
for i in range(7):
    dh(SX + xs_plan[i], SX + xs_plan[i + 1], SY - ROOF_T - 400)
dh(SX, SX + L, SY - ROOF_T - 700)
dv(SY, SY + RIB_H, SX + L + 300); dv(SY + RIB_H, SY + RIB_H + SLAB_T, SX + L + 300); dv(SY, SY + RIB_H + SLAB_T, SX + L + 600)
dtext(SX + L / 2, SY + RIB_H + SLAB_T + 450, "SECTION A-A", 150, layer="TITLE")

# SECTION B-B to the right of plan
BX, BY = L + 2500, 0
drect(BX, BY - ROOF_T, W, ROOF_T, "ROOF", "ANSI37", 20)
drect(BX, BY, RIB, RIB_H, "CONC", "ANSI31", 10)
drect(BX + W - RIB, BY, RIB, RIB_H, "CONC", "ANSI31", 10)
drect(BX + RIB, BY, W - 2 * RIB, RIB_H, "AAC", "DOTS", 20, 30)
drect(BX, BY + RIB_H, W, SLAB_T, "CONC", "ANSI31", 10)
msp.add_line((BX + 50, BY + RIB_H + SLAB_T / 2), (BX + W - 50, BY + RIB_H + SLAB_T / 2), dxfattribs={"layer": "MESH", "lineweight": 50})
dtext(BX + W / 2, BY + RIB_H + SLAB_T + 120, "RC SLAB 150 THK c/w 6 mm BRC MESH", 70)
dtext(BX + W / 2, BY + RIB_H / 2, "AAC BLOCK", 60)
dtext(BX + W / 2, BY - ROOF_T / 2, "EXISTING ROOF SLAB (REF.)", 55)
dtext(BX + RIB / 2, BY - ROOF_T - 100, "CONC. RIB 200x200", 55)
for a_, b_ in [(0, RIB), (RIB, W - RIB), (W - RIB, W)]:
    dh(BX + a_, BX + b_, BY - ROOF_T - 400)
dh(BX, BX + W, BY - ROOF_T - 700)
dv(BY, BY + RIB_H, BX + W + 300); dv(BY + RIB_H, BY + RIB_H + SLAB_T, BX + W + 300); dv(BY, BY + RIB_H + SLAB_T, BX + W + 600)
dtext(BX + W / 2, BY + RIB_H + SLAB_T + 450, "SECTION B-B", 150, layer="TITLE")

dtext(L + 2500, 3800, "WATER TANK UPSTAND ON ROOF - PLAN & SECTIONS   |   UNITS: mm   |   DWG WT-UPS-01 REV 0   |   2026-10-24", 100, TextEntityAlignment.MIDDLE_LEFT, "TITLE")

doc.saveas(f"{OUT}/water-tank-upstand.dxf")
print("dxf ok")
