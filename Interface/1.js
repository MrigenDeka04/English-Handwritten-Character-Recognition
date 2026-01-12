// 1.js - improved canvas drawing + upload/download + predict posting
const canvas = document.getElementById('draw-canvas');
const ctx = canvas.getContext('2d');
const loader = document.getElementById('loader');
const output = document.getElementById('prediction-output');

let drawing = false;
let lastX = 0;
let lastY = 0;

// defaults
let brushSize = document.getElementById('brush-size').valueAsNumber || 20;
let brushColor = document.getElementById('brush-color').value || '#222';

// HiDPI scaling
function configureCanvasForDPR() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const cssW = rect.width || canvas.width;
  const cssH = rect.height || canvas.height;

  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);

  canvas.style.width = cssW + 'px';
  canvas.style.height = cssH + 'px';

  ctx.scale(dpr, dpr);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.fillStyle = '#fff';
  // Fill white background so exported PNG has white background
  ctx.fillRect(0, 0, cssW, cssH);

  ctx.lineWidth = brushSize;
  ctx.strokeStyle = brushColor;
}
configureCanvasForDPR();
window.addEventListener('resize', () => {
  // Save current image, reconfigure, then draw saved image back scaled to new canvas size
  const img = new Image();
  img.src = canvas.toDataURL('image/png');
  img.onload = () => {
    configureCanvasForDPR();
    // draw image centered/fit
    const rect = canvas.getBoundingClientRect();
    ctx.drawImage(img, 0, 0, rect.width, rect.height);
  };
});

// helpers
function setBrushSize(v) {
  brushSize = Number(v);
  ctx.lineWidth = brushSize;
}
function setBrushColor(v) {
  brushColor = v;
  ctx.strokeStyle = brushColor;
}

function getPointerPos(e) {
  const rect = canvas.getBoundingClientRect();
  // Use clientX/Y for pointer events
  return [e.clientX - rect.left, e.clientY - rect.top];
}

// Pointer event handlers
canvas.addEventListener('pointerdown', (e) => {
  canvas.setPointerCapture(e.pointerId);
  drawing = true;
  const [x, y] = getPointerPos(e);
  lastX = x; lastY = y;
  // in case user tapped, create a little dot
  ctx.beginPath();
  ctx.moveTo(lastX, lastY);
  ctx.lineTo(lastX + 0.1, lastY + 0.1);
  ctx.stroke();
});

canvas.addEventListener('pointermove', (e) => {
  if (!drawing) return;
  const [x, y] = getPointerPos(e);
  ctx.beginPath();
  ctx.moveTo(lastX, lastY);
  ctx.lineTo(x, y);
  ctx.stroke();
  lastX = x; lastY = y;
});

function stopDrawing(e) {
  drawing = false;
  try { canvas.releasePointerCapture(e && e.pointerId); } catch (err) {}
  ctx.beginPath();
}
canvas.addEventListener('pointerup', stopDrawing);
canvas.addEventListener('pointercancel', stopDrawing);
canvas.addEventListener('pointerleave', stopDrawing);

// Controls
document.getElementById('brush-size').addEventListener('input', (e) => {
  setBrushSize(e.target.value);
});
document.getElementById('brush-color').addEventListener('input', (e) => {
  setBrushColor(e.target.value);
});

// Clear
document.getElementById('clear-canvas').onclick = () => {
  const rect = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, rect.width, rect.height);
  // fill white background
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, rect.width, rect.height);
  output.textContent = "Draw a character and click Recognize.";
  output.className = "prediction-text";
  loader.style.display = 'none';
};

// Download
document.getElementById('download-image').onclick = () => {
  // ensure white background
  const rect = canvas.getBoundingClientRect();
  const tmp = document.createElement('canvas');
  tmp.width = rect.width;
  tmp.height = rect.height;
  const tctx = tmp.getContext('2d');
  tctx.fillStyle = '#fff';
  tctx.fillRect(0, 0, tmp.width, tmp.height);
  const img = new Image();
  img.src = canvas.toDataURL('image/png');
  img.onload = () => {
    tctx.drawImage(img, 0, 0, tmp.width, tmp.height);
    const a = document.createElement('a');
    a.href = tmp.toDataURL('image/png');
    a.download = 'drawn_character.png';
    a.click();
  };
};

// Upload image to canvas
document.getElementById('upload-image').addEventListener('change', (ev) => {
  const file = ev.target.files && ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      const rect = canvas.getBoundingClientRect();
      // clear and paint white bg
      ctx.clearRect(0, 0, rect.width, rect.height);
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, rect.width, rect.height);

      // draw the uploaded image centered and fit
      const scale = Math.min(rect.width / img.width, rect.height / img.height);
      const w = img.width * scale;
      const h = img.height * scale;
      const x = (rect.width - w) / 2;
      const y = (rect.height - h) / 2;
      ctx.drawImage(img, x, y, w, h);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
});

// POST image (keep your original server API contract)
async function postImage(blob) {
  loader.style.display = 'inline-block';
  output.textContent = 'Recognizing...';
  output.className = "prediction-text";

  const formData = new FormData();
  formData.append('file', blob, 'drawn.png');

  try {
    const res = await fetch('/predict', { method: 'POST', body: formData });
    const data = await res.json();

    loader.style.display = 'none';

    if (data.prediction) {
      // show prediction + confidence (if provided)
      const conf = typeof data.confidence === 'number' ? `${(data.confidence * 100).toFixed(1)}%` : 'N/A';
      output.innerHTML = `<strong>Prediction:</strong> ${escapeHtml(data.prediction)}<br><small>Confidence: ${conf}</small>`;
    } else {
      output.textContent = "⚠️ Prediction failed: " + (data.error || "Unknown error");
      output.className = "prediction-text error";
    }
  } catch (e) {
    loader.style.display = 'none';
    output.textContent = "Server error. Please try again.";
    output.className = "prediction-text error";
  }
}

// helper to escape html in server data
function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"'`=\/]/g, function (c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','/':'&#x2F;','`':'&#x60;','=':'&#x3D;'}[c];
  });
}

// When clicking Recognize: convert canvas to blob with white background
document.getElementById('recognize-draw').onclick = () => {
  // Ensure exported image has white background: draw onto a temp canvas
  const rect = canvas.getBoundingClientRect();
  const tmp = document.createElement('canvas');
  tmp.width = rect.width;
  tmp.height = rect.height;
  const tctx = tmp.getContext('2d');

  tctx.fillStyle = '#fff';
  tctx.fillRect(0, 0, tmp.width, tmp.height);

  const img = new Image();
  img.src = canvas.toDataURL('image/png');
  img.onload = () => {
    tctx.drawImage(img, 0, 0, tmp.width, tmp.height);
    tmp.toBlob((blob) => {
      if (blob) postImage(blob);
    }, 'image/png');
  };
};
