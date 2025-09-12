#  English Handwritten Character Recognition

A deep learning–powered application for recognizing **English handwritten characters (A–Z) and (0-1)**.  
It provides an intuitive **Tkinter-based GUI** where users can either **draw** characters or **upload images** and instantly receive predictions with confidence scores.

---

## ✨ Key Features
-  Recognizes **26 English alphabets (A–Z), (a-z) and Numbers (0-1)**  
-  **Tkinter GUI** with:
-    - Drawing canvas
     - Image upload support (`.png`, `.jpg`, `.jpeg`)  
-  Displays **top-5 prediction probabilities** with confidence scores  
-  Powered by a **Convolutional Neural Network (CNN)** trained on handwritten character data  
-  Lightweight, fast, and user-friendly  

---

## 📂 Project Structure
```

English-Handwritten-Character-Recognition/
├── Interface/
│   ├── Character\_GUI\_Tkinter.ipynb        # Tkinter GUI (Jupyter Notebook)
│   ├── Character\_Recognition\_Notebooks.ipynb  # Model training notebook
│   └── ...
├── Models/                                # Pretrained model(s)
├── Data/                                  # Dataset (if included)
├── screenshots/                           # Project screenshots
└── README.md

````

---

##  Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/MrigenDeka04/English-Handwritten-Character-Recognition.git
cd English-Handwritten-Character-Recognition
````

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

Using **Jupyter Notebook**:

```bash
jupyter notebook Interface/Character_GUI_Tkinter.ipynb
```

Or run as a Python script:

```bash
python Interface/character_gui.py
```

---

## 🖼️ Screenshots

### GUI Prediction Example


<img width="720" height="720" alt="Screenshot 2025-08-29 233515" src="https://github.com/user-attachments/assets/13178923-629b-4240-bd2f-f36f565b8012" />

The system correctly recognizes the handwritten character “A” with 98.84% confidence.

<img width="720" height="720" alt="Screenshot 2025-08-29 233536" src="https://github.com/user-attachments/assets/0745fb1d-e747-479a-8e3f-db7c75737b2b" />

The system correctly recognizes the handwritten character “G” with 90.21% confidence.

<img width="720" height="720" alt="Screenshot 2025-08-29 233849" src="https://github.com/user-attachments/assets/87baa021-5c3a-47dd-b333-efa1d8d37cf2" />

The system correctly recognizes the handwritten character “q” with 98.84% confidence.

<img width="720" height="720" alt="Screenshot 2025-08-29 234634" src="https://github.com/user-attachments/assets/66144d64-e75e-42ca-b734-a81c7df60de7" />

The system correctly recognizes the handwritten character “j” with 99.87% confidence.

---

## 📊 Model Details

* **Input Size:** 64×64 grayscale images
* **Architecture:** Convolutional Neural Network (CNN)
* **Training Accuracy:** \~88%
* **Output:** Softmax probability distribution over 62 classes

---

## 👨‍💻 Author

Developed by **Mrigen Deka**
📧 \[mrigen606@gmail.com]

```

