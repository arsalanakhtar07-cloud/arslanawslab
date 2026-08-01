#!/usr/bin/env python3
"""Generate the architecture diagram, social preview, and favicon."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "site" / "assets"

NAVY = "#04111d"
NAVY_2 = "#071a2b"
CARD = "#0b263d"
CYAN = "#42d3ff"
CYAN_SOFT = "#8ae7ff"
BLUE = "#649dff"
GREEN = "#5ee6a8"
ORANGE = "#ffad42"
WHITE = "#f5f8fb"
MUTED = "#a9b7c5"
LINE = "#24445c"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def rounded_gradient(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, NAVY)
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            cyan_glow = max(0.0, 1.0 - math.hypot(x - width * 0.82, y - height * 0.15) / (width * 0.72))
            blue_glow = max(0.0, 1.0 - math.hypot(x - width * 0.16, y - height * 0.85) / (width * 0.65))
            base = (4, 17, 29)
            pixels[x, y] = (
                int(base[0] + 7 * cyan_glow + 8 * blue_glow),
                int(base[1] + 34 * cyan_glow + 15 * blue_glow),
                int(base[2] + 45 * cyan_glow + 35 * blue_glow),
            )
    return image


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = CYAN) -> None:
    draw.line([start, end], fill=color, width=8)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head = 18
    left = (end[0] - head * math.cos(angle - 0.65), end[1] - head * math.sin(angle - 0.65))
    right = (end[0] - head * math.cos(angle + 0.65), end[1] - head * math.sin(angle + 0.65))
    draw.polygon([end, left, right], fill=color)


def node(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    number: str,
    title: str,
    subtitle: str,
    accent: str,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=26, fill=CARD, outline=LINE, width=3)
    draw.rounded_rectangle((x1 + 20, y1 + 20, x1 + 74, y1 + 74), radius=16, fill=accent)
    draw.text((x1 + 47, y1 + 47), number, font=font(23, True), fill=NAVY, anchor="mm")
    draw.text((x1 + 94, y1 + 21), title, font=font(29, True), fill=WHITE)
    draw.multiline_text((x1 + 94, y1 + 62), subtitle, font=font(20), fill=MUTED, spacing=5)


def generate_architecture() -> None:
    image = rounded_gradient((1600, 900))
    draw = ImageDraw.Draw(image)
    draw.text((90, 72), "How Arslan's AWS website deploys", font=font(54, True), fill=WHITE)
    draw.text((90, 142), "A beginner-friendly map from one code change to a live HTTPS page", font=font(27), fill=MUTED)

    nodes = [
        ((90, 270, 385, 450), "1", "Arslan", "Edits the site\nand pushes code", CYAN),
        ((455, 270, 750, 450), "2", "GitHub", "Stores the code\non the main branch", BLUE),
        ((820, 270, 1115, 450), "3", "Actions", "Builds and deploys\nwith temporary access", GREEN),
        ((1185, 270, 1510, 450), "4", "Private S3", "Stores HTML, CSS,\nJavaScript, and images", ORANGE),
    ]
    for values in nodes:
        node(draw, *values)

    for index in range(len(nodes) - 1):
        current = nodes[index][0]
        following = nodes[index + 1][0]
        arrow(draw, (current[2] + 12, 360), (following[0] - 12, 360))

    cloud_box = (680, 585, 1085, 760)
    node(draw, cloud_box, "5", "CloudFront", "Reads S3 privately and serves\nthe public HTTPS website", CYAN)
    arrow(draw, (1347, 466), (1065, 575), ORANGE)

    visitor_box = (90, 585, 520, 760)
    node(draw, visitor_box, "6", "Visitor", "Opens the CloudFront URL\nfrom a phone or computer", BLUE)
    arrow(draw, (665, 675), (535, 675), CYAN)

    draw.rounded_rectangle((1150, 585, 1510, 760), radius=26, fill="#082e35", outline="#287766", width=3)
    draw.text((1180, 613), "Security path", font=font(27, True), fill=GREEN)
    draw.text((1180, 658), "GitHub OIDC", font=font(22), fill=WHITE)
    draw.text((1180, 696), "Short-lived credentials", font=font(22), fill=WHITE)
    draw.text((1180, 724), "No public S3 access", font=font(22), fill=WHITE)

    draw.text((90, 830), "Git push  →  GitHub Actions  →  private S3  →  CloudFront  →  visitor", font=font(24, True), fill=CYAN_SOFT)
    image.save(ASSETS / "aws-deployment-architecture.png", optimize=True)


def generate_og_card() -> None:
    image = rounded_gradient((1200, 630))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((56, 54, 1144, 576), radius=34, fill="#071d30", outline=LINE, width=3)
    draw.rounded_rectangle((92, 91, 154, 153), radius=18, fill=CYAN)
    draw.text((123, 122), "A", font=font(31, True), fill=NAVY, anchor="mm")
    draw.text((174, 102), "ARSLAN AWS LAB", font=font(25, True), fill=CYAN_SOFT)
    draw.text((92, 195), "From one Git push", font=font(64, True), fill=WHITE)
    draw.text((92, 274), "to a live AWS website.", font=font(64, True), fill=WHITE)
    draw.text((94, 382), "GitHub Actions  •  Private S3  •  CloudFront", font=font(28), fill=MUTED)

    positions = [(138, 495), (356, 495), (574, 495), (792, 495), (1010, 495)]
    labels = ["Git", "Actions", "S3", "CDN", "Live"]
    colors = [BLUE, GREEN, ORANGE, CYAN, GREEN]
    for index, ((x, y), label, color) in enumerate(zip(positions, labels, colors)):
        draw.rounded_rectangle((x - 68, y - 30, x + 68, y + 30), radius=15, fill=CARD, outline=LINE, width=2)
        draw.ellipse((x - 51, y - 7, x - 37, y + 7), fill=color)
        draw.text((x - 25, y), label, font=font(20, True), fill=WHITE, anchor="lm")
        if index < len(positions) - 1:
            arrow(draw, (x + 78, y), (positions[index + 1][0] - 78, y), CYAN)
    image.save(ASSETS / "og-card.png", optimize=True)


def generate_favicon() -> None:
    image = Image.new("RGBA", (192, 192), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((16, 16, 176, 176), radius=48, fill=CYAN)
    draw.text((96, 92), "A", font=font(112, True), fill=NAVY, anchor="mm")
    image.save(ASSETS / "favicon.png", optimize=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    generate_architecture()
    generate_og_card()
    generate_favicon()
    print(f"Generated website graphics in {ASSETS}")


if __name__ == "__main__":
    main()
