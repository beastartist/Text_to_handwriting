from flask import Flask, render_template, request, send_file, jsonify
from handwriting_generator import generate_pdf, generate_preview, valid_fonts
import os

app = Flask(__name__)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text")
        font_name = request.form.get("font_name")
        font_size = request.form.get("font_size")
        text_align = request.form.get("text_align", "left")
        output_path = os.path.join(OUTPUT_DIR, "handwritten.pdf")
        generate_pdf(text, output_path, font_name, font_size, text_align)
        return send_file(output_path, as_attachment=True)
    return render_template("index.html", fonts=list(valid_fonts.keys()))

@app.route("/preview", methods=["POST"])
def preview():
    text = request.form.get("text")
    font_name = request.form.get("font_name")
    font_size = request.form.get("font_size")
    text_align = request.form.get("text_align", "left")
    preview_path = os.path.join(OUTPUT_DIR, "preview.png")

    generate_preview(text, preview_path, font_name, font_size, text_align)
    return jsonify({"preview_url": f"/{preview_path}"})

@app.route("/output/<path:filename>")
def output_file(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename))

if __name__ == "__main__":
    app.run(debug=True)
