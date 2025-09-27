# training/train_dummy_models.py
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from api.models import SmallCNN

os.makedirs("models", exist_ok=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_dummy(num_classes, save_path, epochs=3):
    # create random dataset: 100 samples of 3x224x224
    X = torch.randn(100, 3, 224, 224)
    y = torch.randint(0, num_classes, (100,))
    ds = TensorDataset(X, y)
    loader = DataLoader(ds, batch_size=8, shuffle=True)

    model = SmallCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    opt = optim.Adam(model.parameters(), lr=1e-3)

    model.train()
    for ep in range(epochs):
        running = 0.0
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            opt.step()
            running += loss.item()
        print(f"[{save_path}] Epoch {ep+1}/{epochs} loss: {running/len(loader):.4f}")

    # save state_dict
    torch.save(model.state_dict(), save_path)
    print(f"Saved dummy model to {save_path}")

if __name__ == "__main__":
    train_dummy(num_classes=4, save_path="models/brain_model.pt", epochs=2)
    train_dummy(num_classes=3, save_path="models/retina_model.pt", epochs=2)
