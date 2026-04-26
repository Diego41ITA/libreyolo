from libreyolo import LibreYOLO9
import os
import sys
from multiprocessing import freeze_support

import torch

def main():
    os.chdir(sys.path[0])

    model = LibreYOLO9("LibreYOLO9m.pt", size="m")

    results = model.train(
        data="usod10k.yaml",
        epochs=1,              # default: 300
        batch=16,
        imgsz=640,
        lr0=0.01,
        optimizer="SGD",
        device="cuda",
        workers=2,
        seed=0,
        project="runs/train",
        name="yolo9_exp",        # default: "yolo9_exp"
        exist_ok=False,
        resume=False,
        amp=True,
        patience=50,
    )

    print(f"Best mAP50-95: {results['best_mAP50_95']:.3f}")
    print(f"Best checkpoint: {results['best_checkpoint']}")

    # TorchScript
    model.export(format="torchscript")


if __name__ == "__main__":
    freeze_support()
    main()
