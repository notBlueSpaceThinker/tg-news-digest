from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import ASSETS_PATH


def render_text(
        text: str,
        output_path: str | Path,
        background_path: str | Path = ASSETS_PATH / "background.png",
        font_path: str | Path = ASSETS_PATH / "font.ttf",
        text_rgb_color: tuple = (255, 255, 255),
        text_size: int = 200
    ) -> None:
    img = Image.open(background_path)
    font = ImageFont.truetype(font_path, size=text_size) 
    imgDrawer = ImageDraw.Draw(img)

    (left, top, right, bottom) = imgDrawer.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    image_width, image_height = img.size
    imgDrawer.text(
        (
            (image_width - text_width) / 2,
            (image_height - text_height) / 2
        ),
        text,
        fill=text_rgb_color,
        font=font,
        align="center"
    )
    img.save(output_path)
    