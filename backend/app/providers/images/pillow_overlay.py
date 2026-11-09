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
    NAVY = (22, 32, 46)      # #16202E
    BLUE = (31, 79, 216)     # #1F4FD8
    SUN = (242, 184, 75)     # #F2B84B
    WHITE = (255, 255, 255)
    MUTED = (180, 190, 205)

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or os.path.join(settings.media_storage_dir, "posters")
        os.makedirs(self.output_dir, exist_ok=True)

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

        # Draw decorative geometric brand accent (sun orb top-right per reference design)
        orb_radius = int(width * 0.35)
        orb_center = (int(width * 1.05), int(height * -0.05))
        draw.ellipse(
            [
                orb_center[0] - orb_radius,
                orb_center[1] - orb_radius,
                orb_center[0] + orb_radius,
                orb_center[1] + orb_radius,
            ],
            fill=self.BLUE,
        )

        # Accent circle
        small_orb = int(width * 0.12)
        draw.ellipse(
            [
                int(width * 0.85) - small_orb,
                int(height * 0.15) - small_orb,
                int(width * 0.85) + small_orb,
                int(height * 0.15) + small_orb,
            ],
            fill=self.SUN,
        )

        margin_x = int(width * 0.08)
        padding_top = int(height * 0.08)

        # Use default font or truetype if available
        try:
            font_badge = ImageFont.truetype("DejaVuSans-Bold.ttf", int(width * 0.035))
            font_head = ImageFont.truetype("DejaVuSans-Bold.ttf", int(width * 0.062))
            font_sub = ImageFont.truetype("DejaVuSans.ttf", int(width * 0.038))
            font_cta = ImageFont.truetype("DejaVuSans-Bold.ttf", int(width * 0.036))
        except Exception:
            font_badge = ImageFont.load_default()
            font_head = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # 1. Brand Tag
        badge_text = "BrandMonk Academy"
        badge_w = int(width * 0.42)
        badge_h = int(height * 0.04)
        draw.rounded_rectangle(
            [margin_x, padding_top, margin_x + badge_w, padding_top + badge_h],
            radius=8,
            fill=self.WHITE,
        )
        draw.text(
            (margin_x + 18, padding_top + 8),
            badge_text,
            fill=self.NAVY,
            font=font_badge,
        )

        # 2. Main Headline
        content_y = int(height * 0.58)
        self._draw_multiline_text(
            draw=draw,
            text=headline,
            xy=(margin_x, content_y),
            font=font_head,
            fill=self.WHITE,
            max_width=int(width * 0.84),
            line_spacing=18,
        )

        # 3. Subline
        sub_y = int(height * 0.76)
        self._draw_multiline_text(
            draw=draw,
            text=subline,
            xy=(margin_x, sub_y),
            font=font_sub,
            fill=self.MUTED,
            max_width=int(width * 0.84),
            line_spacing=12,
        )

        # 4. CTA Button
        cta_y = int(height * 0.86)
        btn_w = int(width * 0.45)
        btn_h = int(height * 0.065)
        draw.rounded_rectangle(
            [margin_x, cta_y, margin_x + btn_w, cta_y + btn_h],
            radius=12,
            fill=self.BLUE,
        )
        draw.text(
            (margin_x + 36, cta_y + int(btn_h * 0.28)),
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

