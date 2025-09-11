# ============================================================
# Notebook 3: Character Recognition GUI with Tkinter
# ============================================================

# Install required libraries if not already installed
# !pip install tensorflow pillow matplotlib

import tkinter as tk
from tkinter import Button, Label, messagebox, filedialog
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageTk
import tensorflow as tf
from tensorflow.keras.models import load_model

# --- CORRECTED Configuration ---
# NOTE: Replace this path with a relative path if the model is in the same folder.
# Example: MODEL_PATH = "handwritten_cnn_model3.h5"
MODEL_PATH = r"E:\JEC Internship\Character_Recognition_Notebooks\handwritten_cnn_model3.h5"
IMG_SIZE = (64, 64)

# Class names for 62 classes
CLASS_NAMES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + \
              [chr(c) for c in range(ord('A'), ord('Z')+1)] + \
              [chr(c) for c in range(ord('a'), ord('z')+1)]

# Load model
try:
    model = load_model(MODEL_PATH, compile=False) # compile=False to suppress warning
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
    print(f"Model input shape: {model.input_shape}")
except Exception as e:
    raise SystemExit(f"❌ Failed to load model: {e}")

# GUI Configuration
CANVAS_SIZE = 420
BG_COLOR = "white"
INK_COLOR = "black"
INK_WIDTH = 18

root = tk.Tk()
root.title("Handwritten Character Recognition")
root.resizable(False, False)

# Canvas for drawing
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg=BG_COLOR, cursor="cross")
canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Backing image for clean pixel capture
image1 = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG_COLOR)
draw = ImageDraw.Draw(image1)

last_x, last_y = None, None

def clear_canvas():
    """Clears the canvas and backing image."""
    global image1, draw
    canvas.delete("all")
    image1 = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(image1)

def on_button_press(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def on_move(event):
    global last_x, last_y
    if last_x is not None and last_y is not None:
        canvas.create_line(last_x, last_y, event.x, event.y, 
                          fill=INK_COLOR, width=INK_WIDTH, capstyle=tk.ROUND, smooth=True)
        draw.line((last_x, last_y, event.x, event.y), fill=INK_COLOR, width=INK_WIDTH)
        last_x, last_y = event.x, event.y

def on_button_release(event):
    global last_x, last_y
    last_x, last_y = None, None

def crop_to_content(pil_img: Image.Image, threshold=250):
    """Crops the image to the bounding box of the non-white pixels."""
    gray = pil_img.convert("L")
    arr = np.array(gray)
    ys, xs = np.where(arr < threshold)
    if not ys.size:
        return pil_img # Return original if empty
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    return pil_img.crop((x0, y0, x1 + 1, y1 + 1))

def preprocess_for_model(pil_img: Image.Image):
    """Preprocesses the image to match the model's input requirements."""
    img = pil_img.convert("RGB")
    img = crop_to_content(img)
    
    # Pad to square (white background)
    w, h = img.size
    side = max(w, h)
    bg = Image.new("RGB", (side, side), "white")
    bg.paste(img, ((side - w)//2, (side - h)//2))
    
    img = bg.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img).astype("float32") # Keep 0-255, model has Rescaling layer
    arr = np.expand_dims(arr, axis=0)
    
    return arr, img

def predict_canvas():
    """Predicts the drawn character on the canvas."""
    try:
        arr, preview = preprocess_for_model(image1)
        if np.mean(arr) > 250:
            messagebox.showerror("Error", "Please draw a character before recognizing.")
            return

        probs = model.predict(arr, verbose=0)[0]
        idx = int(np.argmax(probs))
        top1 = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else str(idx)
        conf = float(probs[idx])
        
        # Show results
        msg_lines = [f"Prediction: {top1} (confidence: {conf:.2%})"]
        messagebox.showinfo("Prediction", "\n".join(msg_lines))
        
    except Exception as e:
        messagebox.showerror("Error", f"Prediction failed: {e}")

# Bind drawing events
canvas.bind("<Button-1>", on_button_press)
canvas.bind("<B1-Motion>", on_move)  
canvas.bind("<ButtonRelease-1>", on_button_release)

# Create buttons
btn_predict = tk.Button(root, text="Recognize", command=predict_canvas, width=16)
btn_clear = tk.Button(root, text="Clear", command=clear_canvas, width=16) 

btn_predict.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
btn_clear.grid(row=1, column=1, padx=10, pady=(0,10), sticky="ew")

print("✅ GUI ready - drawing canvas uses 64x64 preprocessing")
root.mainloop()