from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os, random, sys

# ---------------- CONFIG ----------------
FONTS = {
    "Style 1": "assets/fonts/handwriting_1.ttf",
    "Style 2": "assets/fonts/handwriting_2.ttf",
    "Style 3": "assets/fonts/handwriting_3.ttf",
    "Style 4": "assets/fonts/handwriting_4.ttf",
    "Style 5": "assets/fonts/handwriting_5.ttf",
    "Style 6": "assets/fonts/handwriting_6.ttf",
    "Style 7": "assets/fonts/handwriting_7.ttf"
}

OUTPUT_DIR = "output"
MARGIN_X = 120
MARGIN_Y = 180
PAGE_WIDTH_PX = 2000
PAGE_HEIGHT_PX = 2800  # approx A4 at 300 DPI
ANSWER_BLUE = (20, 50, 150)
QUESTION_BLACK = (0, 0, 0)

os.makedirs(OUTPUT_DIR, exist_ok=True)

valid_fonts = {name: path for name, path in FONTS.items() if os.path.isfile(path)}
if not valid_fonts:
    sys.exit("❌ No valid fonts found. Check assets/fonts folder.")

# ---------------- HELPERS ----------------
def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def draw_wrapped_text(draw, text, font, x_start, y_start, max_width, text_align, color):
    """Draw wrapped text with alignment. Returns new y position."""
    wrapped_lines = wrap_text(draw, text, font, max_width)
    y = y_start
    for wl in wrapped_lines:
        bbox = draw.textbbox((0, 0), wl, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if text_align == "center":
            x = (PAGE_WIDTH_PX - w) // 2
        elif text_align == "right":
            x = PAGE_WIDTH_PX - w - MARGIN_X
        else:
            x = x_start

        # Draw each character with slight random offsets for realism
        x_cursor = x
        line_img = Image.new("RGBA", (PAGE_WIDTH_PX, h + 20), (255, 255, 255, 0))
        line_draw = ImageDraw.Draw(line_img)

        for char in wl:
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            line_draw.text((x_cursor + offset_x, offset_y), char, font=font, fill=color)
            x_cursor += draw.textlength(char, font=font)

        angle = random.uniform(-2, 2)
        line_img = line_img.rotate(angle, expand=True)
        draw.bitmap((0, y), line_img, fill=None)
        y += h + 25
    return y

# ---------------- PDF & Preview ----------------
def generate_pdf(text, output_path, font_name=None, font_size=12, text_align="left"):
    font_path = valid_fonts.get(font_name, random.choice(list(valid_fonts.values())))
    base_size = int(font_size) * 3

    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = []
    for line_text in raw_lines:
        color = QUESTION_BLACK if line_text.endswith("?") or line_text.lower().startswith("q") else ANSWER_BLUE
        lines.append((line_text, color))

    pages = []
    current_line = 0
    total_lines = len(lines)

    while current_line < total_lines:
        bg = Image.new("RGB", (PAGE_WIDTH_PX, PAGE_HEIGHT_PX), color=(255, 255, 255))
        draw = ImageDraw.Draw(bg)
        y = MARGIN_Y

        while current_line < total_lines:
            line_text, color = lines[current_line]
            font_size_variation = random.randint(-2, 2)
            font = ImageFont.truetype(font_path, base_size + font_size_variation)

            y = draw_wrapped_text(draw, line_text, font, MARGIN_X, y, PAGE_WIDTH_PX - MARGIN_X*2, text_align, color)

            if y > PAGE_HEIGHT_PX - 200:
                break
            current_line += 1

        page_path = os.path.join(OUTPUT_DIR, f"page_{len(pages)+1}.png")
        bg.save(page_path)
        pages.append(page_path)

    pdf = FPDF(unit="mm", format="A4")
    for img in pages:
        pdf.add_page()
        pdf.image(img, x=0, y=0, w=210, h=297)
    pdf.output(output_path)
    print(f"✅ PDF generated with {len(pages)} pages using {font_name} at size {font_size}")

def generate_preview(text, preview_path, font_name=None, font_size=12, text_align="left"):
    font_path = valid_fonts.get(font_name, random.choice(list(valid_fonts.values())))
    base_size = int(font_size) * 3

    bg = Image.new("RGB", (2000, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(bg)

    lines = text.split("\n")[:5]  # only first few lines for speed
    y = 150

    for line_text in lines:
        color = QUESTION_BLACK if line_text.endswith("?") or line_text.lower().startswith("q") else ANSWER_BLUE
        font = ImageFont.truetype(font_path, base_size)

        # wrap text to fit width
        wrapped_lines = wrap_text(draw, line_text, font, 1800)
        for wl in wrapped_lines:
            bbox = draw.textbbox((0,0), wl, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            if text_align == "center":
                x = (bg.width - w) // 2
            elif text_align == "right":
                x = bg.width - w - 120
            else:
                x = 120

            draw.text((x, y), wl, font=font, fill=color)
            y += h + 10

    bg.save(preview_path)

