#!/usr/bin/env python3
"""Draw the GitHub-profile banner: Hermite functions psi_n(phi(x)) on a grid warped by a
smooth monotone map phi, i.e. a (toy) flow-induced basis. Writes a light and a dark SVG.

    python bin/banner.py OUT_DIR        # -> OUT_DIR/banner-light.svg, OUT_DIR/banner-dark.svg
"""
import math
import sys
from pathlib import Path

import yaml

W, H = 1200, 300
ROOT = Path(__file__).resolve().parent.parent


def hermite_functions(n_max, x):
    """Orthonormal Hermite functions psi_0..psi_n at x (stable three-term recurrence)."""
    p0 = math.pi ** -0.25 * math.exp(-x * x / 2)
    out = [p0]
    if n_max >= 1:
        out.append(math.sqrt(2) * x * p0)
    for n in range(2, n_max + 1):
        out.append(math.sqrt(2 / n) * x * out[-1] - math.sqrt((n - 1) / n) * out[-2])
    return out


def phi(x):
    """Monotone 'flow' map: identity plus a smooth bump (derivative stays > 0)."""
    return x + 0.55 * math.tanh(0.9 * (x - 0.8)) - 0.35 * math.tanh(1.3 * (x + 1.6))


def path(points):
    return "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in points)


def svg(theme):
    bg, fg, sub, grid, curves = {
        "light": ("#ffffff", "#14326e", "#555b66", "#dfe4ee", ["#14326e", "#2f6fbd", "#5aa0d8", "#9cc3e6"]),
        "dark": ("#0d1117", "#e6edf3", "#9aa4b2", "#1f2a3a", ["#79c0ff", "#58a6ff", "#3b82c4", "#2a5d8f"]),
    }[theme]
    prof = yaml.safe_load((ROOT / "_data" / "cv.yml").read_text(encoding="utf-8"))["profile"]

    x0, x1 = 480, W - 30  # plot area (right part)
    y_mid, amp = H / 2, 95
    xs = [-4.5 + 9 * i / 400 for i in range(401)]
    to_px = lambda x: x0 + (x + 4.5) / 9 * (x1 - x0)

    parts = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    # warped grid: vertical lines at phi^{-1}(uniform) positions -> look where phi squeezes/stretches
    for k in range(-9, 10):
        u = k * 0.5
        # invert phi by bisection
        lo, hi = -10.0, 10.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if phi(mid) < u else (lo, mid)
        x = (lo + hi) / 2
        if -4.5 <= x <= 4.5:
            px = to_px(x)
            parts.append(f'<line x1="{px:.1f}" y1="30" x2="{px:.1f}" y2="{H-30}" stroke="{grid}" stroke-width="1"/>')
    for yy in range(30, H - 29, 40):
        parts.append(f'<line x1="{x0}" y1="{yy}" x2="{x1}" y2="{yy}" stroke="{grid}" stroke-width="1"/>')

    # warped Hermite functions psi_n(phi(x)) * sqrt(phi'(x))  (unitary composition operator)
    for idx, n in enumerate([6, 4, 2, 0][::-1]):
        pts = []
        for x in xs:
            h = 1e-4
            dphi = (phi(x + h) - phi(x - h)) / (2 * h)
            val = hermite_functions(n, phi(x))[n] * math.sqrt(dphi)
            pts.append((to_px(x), y_mid - amp * val * (1.0 if n else 0.9)))
        op = [1.0, 0.85, 0.7, 0.55][idx]
        parts.append(
            f'<path d="{path(pts)}" fill="none" stroke="{curves[idx]}" stroke-width="{2.4 - 0.3*idx:.1f}" '
            f'stroke-opacity="{op}" stroke-linecap="round"/>'
        )

    font = "Palatino, 'Palatino Linotype', 'Book Antiqua', Georgia, serif"
    parts.append(
        f'<text x="40" y="128" font-family="{font}" font-size="46" fill="{fg}">{prof["name"]}</text>'
        f'<text x="42" y="168" font-family="{font}" font-size="19" font-style="italic" fill="{sub}">'
        "Approximation theory · scientific machine learning</text>"
        f'<text x="42" y="196" font-family="{font}" font-size="19" font-style="italic" fill="{sub}">'
        "normalizing flows · quantum molecular physics</text>"
        f'<text x="42" y="{H-34}" font-family="{font}" font-size="13" fill="{sub}" opacity="0.8">'
        "ψ<tspan baseline-shift=\"sub\" font-size=\"10\">n</tspan>(φ(x)) √φ′(x) — Hermite functions under a learned coordinate map</text>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{prof["name"]}">' + "".join(parts) + "</svg>\n"
    )


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for t in ("light", "dark"):
        (out / f"banner-{t}.svg").write_text(svg(t), encoding="utf-8")
        print(out / f"banner-{t}.svg")
