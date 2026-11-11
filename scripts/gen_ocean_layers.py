"""Ocean-layer schematic adapted from gtc2026/scripts/ocean_layers.py."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-o", "--output", type=Path, default=Path("img/ocean_layers.svg"))
parser.add_argument("--static", action="store_true", help="export the original still image")
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
INK, TEAL, AMBER = "#12364A", "#087E8B", "#B26020"
fig, ax = plt.subplots(figsize=(5.5, 3.3))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set(xlim=(0, 11), ylim=(0, 4))
ax.axis("off")
x = np.linspace(.9, 10.45, 400)
phase = (x - .9) / 9.55
interfaces = []
for k in range(6):
    amplitude = .18 if k == 0 else .21
    interfaces.append(3.1 - k*.43 + amplitude*np.sin(phase*2.5*np.pi + k*.45)
                      + (.06 if k else 0)*np.cos(phase*4*np.pi))

# Hatched ground follows the lowest interface.
ax.fill_between(x, np.min(interfaces[-1]) - .28, interfaces[-1],
                 facecolor="#F3EFE7", edgecolor="#9C9385", hatch="///",
                 linewidth=0, gid="ocean-seabed")

# Wavy, non-crossing interfaces; five layers, one selected layer.
for k in range(5):
    ax.fill_between(x, interfaces[k+1], interfaces[k],
                    color="#81C9CE" if k == 2 else ["#EAF5F8", "#DFEEF3"][k % 2],
                    gid=f"ocean-layer-{k}")
for k, y in enumerate(interfaces):
    ax.plot(x, y, color=TEAL if k in (2, 3) else "#8BAEBB",
            lw=1.5 if k in (2, 3) else 1, gid=f"ocean-interface-{k}")

# A vertical column samples every layer; its cells retain the local interfaces.
left, right = 7.15, 7.68
mask = (x >= left) & (x <= right)
for k in range(5):
    ax.fill_between(x[mask], interfaces[k+1][mask], interfaces[k][mask],
                    color="#F0C477", alpha=.85, zorder=4, gid=f"column-cell-{k}")
    ax.plot(x[mask], interfaces[k][mask], color=AMBER, lw=1.2, zorder=5,
            gid=f"column-interface-{k}")
for edge in (left, right):
    ax.plot([edge, edge], [np.interp(edge, x, interfaces[-1]),
                          np.interp(edge, x, interfaces[0])],
             color=AMBER, lw=1.5, zorder=5, gid=f"column-edge-{edge}")
ax.plot(x[mask], interfaces[-1][mask], color=AMBER, lw=1.2, zorder=5,
        gid="column-bottom")

ax.annotate("Layer", (3.2, np.interp(3.2, x, interfaces[2])-.2),
            (1.8, 3.62), fontsize=20, color=TEAL,
            arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.5), va="center")
ax.annotate("Column", (7.42, np.interp(7.42, x, interfaces[0])), (6.3, 3.62),
            fontsize=20, color=AMBER, va="center", zorder=10,
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.5))
# Crop unused canvas while retaining the labels, arrows, and hatched seabed.
crop = Bbox.from_extents(.75, np.min(interfaces[-1]) - .34, 10.6, 3.85)
crop_inches = ax.transData.transform_bbox(crop).transformed(fig.dpi_scale_trans.inverted())
fig.savefig(args.output, transparent=True, bbox_inches=crop_inches)

if not args.static:
    # Native SVG path animation: no video, canvas, or external JS dependency.
    # Keep the seabed and column x coordinates fixed. Interfaces move through
    # the column, and its side walls extend up to the moving ocean surface.
    wave_x = np.unique(np.concatenate((np.linspace(x[0], x[-1], 120), [left, right])))
    wave_phase = (wave_x - .9) / 9.55
    base = np.array([np.interp(wave_x, x, interface) for interface in interfaces])

    def wave_interfaces(angle):
        traveling = np.sin(2*np.pi*wave_phase - angle) - np.sin(2*np.pi*wave_phase)
        depth_weight = np.linspace(1, 0, 6)[:, None]
        #return base + .065 * depth_weight * traveling
        return base + .1 * depth_weight * traveling

    # Validate a denser sampling than the exported keyframes, including crop
    # bounds and fixed seabed. Linear SVG interpolation preserves order.
    for angle in np.linspace(0, 2*np.pi, 257):
        wave = wave_interfaces(angle)
        assert np.all(wave[:-1] > wave[1:]), "Ocean interfaces crossed"
        np.testing.assert_allclose(wave[-1], base[-1])
        assert wave.min() > crop.y0 and wave.max() < crop.y1

    svg_ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", svg_ns)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    tree = ET.parse(args.output)
    root = tree.getroot()
    root.set("role", "img")
    root.set("tabindex", "0")
    root.set("aria-label", "Moving ocean layers through a column with fixed horizontal bounds. Click or press Enter to pause.")
    title = ET.Element(f"{{{svg_ns}}}title")
    title.text = "Moving ocean layers; column walls fixed horizontally"
    root.insert(0, title)

    def svg_points(xx, yy):
        pixels = ax.transData.transform(np.column_stack((xx, yy)))
        return np.column_stack((
            (pixels[:, 0] / fig.dpi - crop_inches.x0) * 72,
            (crop_inches.y1 - pixels[:, 1] / fig.dpi) * 72,
        ))

    def outline(points, closed=False):
        return "M" + " L".join(f"{px:.3f},{py:.3f}" for px, py in points) + (" Z" if closed else "")

    frames = [wave_interfaces(angle) for angle in np.linspace(0, 2*np.pi, 33)]

    def animate(group_id, paths, style):
        group = root.find(f".//*[@id='{group_id}']")
        group.clear()
        group.set("id", group_id)
        path = ET.SubElement(group, f"{{{svg_ns}}}path", {"d": paths[0], "style": style})
        ET.SubElement(path, f"{{{svg_ns}}}animate", {
            "attributeName": "d", "values": ";".join(paths),
            #"dur": "10s", "repeatCount": "indefinite", "calcMode": "linear",
            "dur": "6s", "repeatCount": "indefinite", "calcMode": "linear",
        })

    for k in range(5):
        paths = [outline(np.concatenate((svg_points(wave_x, wave[k]),
                                         svg_points(wave_x[::-1], wave[k+1][::-1]))), True)
                 for wave in frames]
        color = "#81C9CE" if k == 2 else ["#EAF5F8", "#DFEEF3"][k % 2]
        animate(f"ocean-layer-{k}", paths, f"fill:{color};stroke:{color}")
    for k in range(5):
        paths = [outline(svg_points(wave_x, wave[k])) for wave in frames]
        color, width = (TEAL, 1.5) if k in (2, 3) else ("#8BAEBB", 1)
        animate(f"ocean-interface-{k}", paths, f"fill:none;stroke:{color};stroke-width:{width}")

    # Use the same samples and keyframes on both sides of each column wall,
    # so the highlighted cells stay aligned with the moving ocean interfaces.
    column_mask = (wave_x >= left) & (wave_x <= right)
    column_x = wave_x[column_mask]
    for k in range(5):
        paths = [outline(np.concatenate((svg_points(column_x, wave[k, column_mask]),
                                         svg_points(column_x[::-1], wave[k+1, column_mask][::-1]))), True)
                 for wave in frames]
        animate(f"column-cell-{k}", paths,
                "fill:#F0C477;fill-opacity:.85;stroke:#F0C477;stroke-opacity:.85")
        paths = [outline(svg_points(column_x, wave[k, column_mask])) for wave in frames]
        animate(f"column-interface-{k}", paths, f"fill:none;stroke:{AMBER};stroke-width:1.2")
    for edge in (left, right):
        edge_index = np.flatnonzero(wave_x == edge)[0]
        paths = [outline(svg_points([edge, edge], [wave[-1, edge_index], wave[0, edge_index]]))
                 for wave in frames]
        animate(f"column-edge-{edge}", paths, f"fill:none;stroke:{AMBER};stroke-width:1.5")

    # An object embedding allows these small accessibility/playback controls.
    # Without script or SMIL support, the SVG still contains its original frame.
    script = ET.SubElement(root, f"{{{svg_ns}}}script")
    script.text = """
    (() => {
      const svg = document.documentElement;
      const reduced = matchMedia('(prefers-reduced-motion: reduce)');
      let paused = reduced.matches;
      function apply() { paused ? svg.pauseAnimations() : svg.unpauseAnimations(); }
      function toggle() { paused = !paused; apply(); }
      svg.addEventListener('click', toggle);
      svg.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(); }
      });
      reduced.addEventListener('change', event => { paused = event.matches; apply(); });
      addEventListener('beforeprint', () => { svg.pauseAnimations(); svg.setCurrentTime(0); });
      addEventListener('afterprint', apply);
      apply();
    })();
    """
    tree.write(args.output, encoding="utf-8", xml_declaration=True)
plt.close(fig)
