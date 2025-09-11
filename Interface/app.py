import io
import os
import numpy as np
from PIL import Image
from flask import Flask, jsonify, request, send_from_directory

# ---------------- CONFIG ----------------
MODEL_PATH = r"E:\JEC Internship\Character_Recognition_Notebooks\handwritten_cnn_model3.h5"
TARGET_SIZE = (64, 64)   # H, W
INDEX_FILE = "1.html"

# Class labels: 0–9 + A–Z + a–z (62 total)
CLASS_LABELS = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

# ---------------- UTILITIES ----------------
def smart_autocrop(img: Image.Image, bg_is_white=True, margin_ratio=0.12) -> Image.Image:
    """Crop whitespace around drawn character."""
    gray = img.convert("L")
    arr = np.array(gray)
    mask = arr < 250 if bg_is_white else arr > 5
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img.crop((x0, y0, x1, y1))
    w, h = cropped.size
    m = int(round(max(w, h) * margin_ratio))
    new_w, new_h = w + 2*m, h + 2*m
    bg_color = 255 if bg_is_white else 0
    canvas = Image.new("L", (new_w, new_h), bg_color)
    canvas.paste(cropped, (m, m))
    return canvas

def make_square_and_resize(img: Image.Image, target_hw=(64,64), bg_is_white=True) -> Image.Image:
    """Pad to square, then resize."""
    img = smart_autocrop(img, bg_is_white)
    w, h = img.size
    side = max(w, h)
    bg_color = 255 if bg_is_white else 0
    square = Image.new("L", (side, side), bg_color)
    square.paste(img, ((side-w)//2, (side-h)//2))
    return square.resize(target_hw, Image.LANCZOS)

def preprocess_for_model(pil: Image.Image, target_hw=(64,64), invert=True) -> np.ndarray:
    """Prepare image for CNN model (expects RGB 3-channel)."""
    # 1. Convert to grayscale for cleaning
    gray = pil.convert("L")
    gray = make_square_and_resize(gray, target_hw, bg_is_white=True)

    # 2. Convert to numpy
    arr = np.array(gray, dtype="float32")

    # 3. Invert if training dataset had white digits on black background
    if invert:
        arr = 255.0 - arr

    # 4. Normalize
    arr = arr / 255.0

    # 5. Convert grayscale to 3 channels
    arr = np.stack([arr, arr, arr], axis=-1)  # shape (64, 64, 3)

    return arr

# ---------------- LOAD MODEL ----------------
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import tensorflow as tf
from tensorflow.keras.models import load_model

try:
    model = load_model(MODEL_PATH, compile=False)
    MODEL_BACKEND = "keras"
except Exception as e:
    model = None
    MODEL_BACKEND = None
    print("Error loading model:", e)

def predict_array(x: np.ndarray):
    """Run model prediction and return probs + best index."""
    x_b = np.expand_dims(x, 0)  # batch
    y = model.predict(x_b, verbose=0)
    y = np.array(y)
    if y.ndim > 2:
        y = np.squeeze(y, axis=0)
    logits = y if y.ndim == 1 else y[0]
    exps = np.exp(logits - np.max(logits))
    probs = exps / np.clip(np.sum(exps), 1e-9, None)
    best_idx = int(np.argmax(probs))
    best_prob = float(probs[best_idx])
    return probs, best_idx, best_prob

# ---------------- FLASK APP ----------------
app = Flask(__name__, static_folder=".", static_url_path="")

@app.get("/")
def index():
    if os.path.exists(INDEX_FILE):
        return app.send_static_file(INDEX_FILE)
    return "<h2>Handwritten Character Recognition API</h2>", 200

@app.post("/predict")
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        pil = Image.open(io.BytesIO(file.read()))
        x = preprocess_for_model(pil, TARGET_SIZE, invert=True)

        probs, best_idx, best_conf = predict_array(x)
        label = CLASS_LABELS[best_idx] if best_idx < len(CLASS_LABELS) else str(best_idx)

        top_k = min(3, len(probs))
        top_indices = np.argsort(probs)[::-1][:top_k].tolist()
        top3 = [
            {"label": CLASS_LABELS[i], "confidence": float(probs[i])}
            for i in top_indices
        ]

        return jsonify({
            "prediction": label,
            "confidence": round(best_conf, 6),
            "top3": top3
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/<path:filename>")
def serve_static(filename):
    if os.path.exists(filename):
        return send_from_directory(".", filename)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
