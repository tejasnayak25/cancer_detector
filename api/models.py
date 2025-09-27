# api/models.py
import io
from typing import Tuple
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np

# --- Model architecture (must match training) ---
class SmallCNN(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(16 * 56 * 56, 64),  # input size depends on input image size
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# --- Preprocessing ---
# We'll use 224x224 like the TF demo.
IMG_SIZE = 224
transform = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.ToTensor(),                # scales to [0,1]
    T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])  # imagenet-like
])

def preprocess_image_bytes(image_bytes: bytes, device: torch.device) -> torch.Tensor:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)  # shape: [1,3,H,W]
    return tensor

# --- Loading helpers ---
def load_model(path: str, num_classes: int, device: torch.device):
    """
    Create model instance, load state_dict, put to device and eval mode.
    Returns the model or None on failure.
    """
    try:
        model = SmallCNN(num_classes=num_classes)
        state = torch.load(path, map_location=device)
        # allow either full model or state_dict
        if isinstance(state, dict) and any(k.startswith('features') or k.startswith('classifier') for k in state.keys()):
            model.load_state_dict(state)
        else:
            # if entire model saved, try load directly (rare)
            model = state
        model.to(device)
        model.eval()
        print(f"Loaded PyTorch model from {path}")
        return model
    except Exception as e:
        print(f"Failed to load model {path}: {e}")
        return None

# --- Decode predictions: adjust labels to match training ordering ---
BRAIN_LABELS = ["no_tumor", "glioma", "meningioma", "pituitary"]
RETINA_LABELS = ["normal", "retina_tumor", "other"]

def decode_brain_pred(logits: torch.Tensor) -> Tuple[str, float]:
    if logits is None:
        return "model-not-loaded", 0.0
    probs = torch.softmax(logits, dim=1).cpu().numpy()
    idx = int(np.argmax(probs, axis=1)[0])
    conf = float(np.max(probs))
    return BRAIN_LABELS[idx], conf

def decode_retina_pred(logits: torch.Tensor) -> Tuple[str, float]:
    if logits is None:
        return "model-not-loaded", 0.0
    probs = torch.softmax(logits, dim=1).cpu().numpy()
    idx = int(np.argmax(probs, axis=1)[0])
    conf = float(np.max(probs))
    return RETINA_LABELS[idx], conf
