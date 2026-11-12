import os
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("provider.image.pillow")


class PillowPosterRenderer:
    SIZES = {
        "square": (1080, 1080),
        "feed": (1080, 1350),
        "story": (1080, 1920),
    }

    # BrandMonk Academy Brand Kit colors
    NAVY = (19, 38, 34)      # #132622 Deep BrandMonk Slate
    TEAL = (10, 124, 110)    # #0A7C6E BrandMonk Primary Teal
    BLUE = (10, 124, 110)    # #0A7C6E Accent
    SUN = (242, 184, 75)     # #F2B84B Warm Gold Accent
    WHITE = (255, 255, 255)
    MUTED = (197, 209, 205)  # #C5D1CD Crisp Muted Text

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or os.path.join(settings.media_storage_dir, "posters")
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        candidates = (
            [
                "/usr/share/fonts/noto/NotoSans-Bold.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "DejaVuSans-Bold.ttf",
            ]
            if bold
            else [
                "/usr/share/fonts/noto/NotoSans-Regular.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "DejaVuSans.ttf",
            ]
        )
        for path in candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    def render(
        self,
        *,
        poster_id: int,
        headline: str,
        subline: str,
        cta_text: str = "Book a free demo",
        size_format: str = "feed",
    ) -> str:
        width, height = self.SIZES.get(size_format, self.SIZES["feed"])
        img = Image.new("RGB", (width, height), color=self.NAVY)
        draw = ImageDraw.Draw(img)

        # Decorative geometric brand accent top-right
        orb_radius = int(width * 0.36)
        orb_center = (int(width * 1.02), int(height * -0.02))
        draw.ellipse(
            [
                orb_center[0] - orb_radius,
                orb_center[1] - orb_radius,
                orb_center[0] + orb_radius,
                orb_center[1] + orb_radius,
            ],
            fill=self.TEAL,
        )

        # Warm gold accent circle
        small_orb = int(width * 0.11)
        draw.ellipse(
            [
                int(width * 0.86) - small_orb,
                int(height * 0.14) - small_orb,
                int(width * 0.86) + small_orb,
                int(height * 0.14) + small_orb,
            ],
            fill=self.SUN,
        )

        margin_x = int(width * 0.08)
        padding_top = int(height * 0.07)

        font_badge = self._load_font(int(width * 0.028), bold=True)
        font_head = self._load_font(int(width * 0.068), bold=True)
        font_sub = self._load_font(int(width * 0.036), bold=False)
        font_pill = self._load_font(int(width * 0.026), bold=True)
        font_cta = self._load_font(int(width * 0.034), bold=True)

        # 1. Brand Tag
        badge_text = "BRANDMONK ACADEMY"
        badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
        badge_w = (badge_bbox[2] - badge_bbox[0]) + 44
        badge_h = (badge_bbox[3] - badge_bbox[1]) + 26
        draw.rounded_rectangle(
            [margin_x, padding_top, margin_x + badge_w, padding_top + badge_h],
            radius=8,
            fill=self.WHITE,
        )
        draw.text(
            (margin_x + 22, padding_top + 10),
            badge_text,
            fill=self.NAVY,
            font=font_badge,
        )

        # 2. Main Headline (placed prominently in upper-middle focal area)
        content_y = int(height * 0.27)
        after_head_y = self._draw_multiline_text(
            draw=draw,
            text=headline,
            xy=(margin_x, content_y),
            font=font_head,
            fill=self.WHITE,
            max_width=int(width * 0.84),
            line_spacing=18,
        )

        # Accent divider bar
        divider_y = after_head_y + int(height * 0.03)
        draw.rounded_rectangle(
            [margin_x, divider_y, margin_x + int(width * 0.12), divider_y + 8],
            radius=4,
            fill=self.SUN,
        )

        # 3. Subline
        sub_y = divider_y + int(height * 0.04)
        after_sub_y = self._draw_multiline_text(
            draw=draw,
            text=subline,
            xy=(margin_x, sub_y),
            font=font_sub,
            fill=self.MUTED,
            max_width=int(width * 0.84),
            line_spacing=14,
        )

        # 4. Trust strip above CTA
        trust_y = max(after_sub_y + int(height * 0.05), int(height * 0.72))
        draw.text(
            (margin_x, trust_y),
            "Transparent Fees   ·   Live Agency Mentors   ·   Small Batches",
            fill=self.SUN,
            font=font_pill,
        )

        # 5. CTA Button
        cta_y = int(height * 0.82)
        cta_bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
        btn_w = max(int(width * 0.44), (cta_bbox[2] - cta_bbox[0]) + 84)
        btn_h = int(height * 0.072)
        draw.rounded_rectangle(
            [margin_x, cta_y, margin_x + btn_w, cta_y + btn_h],
            radius=12,
            fill=self.TEAL,
        )
        text_w = cta_bbox[2] - cta_bbox[0]
        text_h = cta_bbox[3] - cta_bbox[1]
        draw.text(
            (margin_x + (btn_w - text_w) // 2, cta_y + (btn_h - text_h) // 2 - 4),
            cta_text,
            fill=self.WHITE,
            font=font_cta,
        )

        filename = f"poster_{poster_id}_{size_format}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, format="PNG", quality=95)
        return filepath

    def _draw_multiline_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        xy: tuple[int, int],
        font: ImageFont.ImageFont,
        fill: tuple,
        max_width: int,
        line_spacing: int = 10,
    ):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width > max_width and len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        x, y = xy
        for line in lines:
            draw.text((x, y), line, font=font, fill=fill)
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            y += line_height + line_spacing
        return y

