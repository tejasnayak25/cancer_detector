# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import api.models as models_module
import torch

app = FastAPI(title="Cancer Detection API (PyTorch)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# models placeholder
MODELS = {"brain": None, "retina": None}

@app.on_event("startup")
def load_models():
    MODELS["brain"] = models_module.load_model("models/brain_model.pt", num_classes=4, device=DEVICE)
    MODELS["retina"] = models_module.load_model("models/retina_model.pt", num_classes=3, device=DEVICE)

@app.post("/predict/brain")
async def predict_brain(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        model = MODELS["brain"]
        if model is None:
            raise HTTPException(status_code=503, detail="Brain model not loaded")
        x = models_module.preprocess_image_bytes(contents, device=DEVICE)
        with torch.no_grad():
            logits = model(x)
        label, confidence = models_module.decode_brain_pred(logits)
        return JSONResponse({"label": label, "confidence": confidence})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/retina")
async def predict_retina(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        model = MODELS["retina"]
        if model is None:
            raise HTTPException(status_code=503, detail="Retina model not loaded")
        x = models_module.preprocess_image_bytes(contents, device=DEVICE)
        with torch.no_grad():
            logits = model(x)
        label, confidence = models_module.decode_retina_pred(logits)
        return JSONResponse({"label": label, "confidence": confidence})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
