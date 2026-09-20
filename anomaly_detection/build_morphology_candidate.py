from __future__ import annotations

"""Create frozen-model morphology references from normal cell crops only."""

import json
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.nn import functional as functional

from anomaly_detection.scoring import cosine_distance, fit_calibration
from feature_extraction.extract_latent import load_autoencoder
from training.dataset_loader import CellCropDataset
from utils.config import PROJECT_ROOT, load_yaml
from utils.morphology import standardize_cell_crop


def _features(model: torch.nn.Module, dataset: CellCropDataset, device: torch.device) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    latents, errors, labels = [], [], []
    with torch.inference_mode():
        for start in range(0, len(dataset), 128):
            batch, batch_labels = [], []
            for index in range(start, min(start + 128, len(dataset))):
                image, class_id, _ = dataset[index]
                bgr = cv2.cvtColor(image.permute(1, 2, 0).numpy(), cv2.COLOR_RGB2BGR)
                normalized = standardize_cell_crop(bgr)
                rgb = cv2.cvtColor(normalized, cv2.COLOR_BGR2RGB)
                batch.append(torch.from_numpy(rgb).permute(2, 0, 1).float().div(255))
                batch_labels.append(class_id)
            tensor = torch.stack(batch).to(device)
            reconstruction, latent = model(tensor)
            errors.extend(functional.mse_loss(reconstruction, tensor, reduction="none").mean(dim=(1, 2, 3)).cpu().numpy())
            latents.extend(latent.cpu().numpy())
            labels.extend(batch_labels)
    return np.asarray(latents), np.asarray(errors), np.asarray(labels)


def build() -> None:
    config = load_yaml(PROJECT_ROOT / "configs" / "anomaly_morphology_candidate.yaml")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_autoencoder(PROJECT_ROOT / "outputs" / "weights" / "autoencoder_best.pt", device)
    train_latent, _train_mse, train_labels = _features(model, CellCropDataset(PROJECT_ROOT / "dataset" / "crops", "train"), device)
    val_latent, val_mse, val_labels = _features(model, CellCropDataset(PROJECT_ROOT / "dataset" / "crops", "val"), device)
    centroids = {class_id: train_latent[train_labels == class_id].mean(axis=0) for class_id in (0, 1, 2)}
    calibration_by_class = {}
    for class_id in (0, 1, 2):
        selected = val_labels == class_id
        cosine = np.asarray([cosine_distance(vector, centroids[class_id]) for vector in val_latent[selected]])
        calibration_by_class[str(class_id)] = fit_calibration(val_mse[selected], cosine, np.ones(selected.sum()), config).to_dict()
    weights = PROJECT_ROOT / "outputs" / "weights"
    torch.save({"centroids": {key: torch.from_numpy(value).float() for key, value in centroids.items()}, "source": "normal transformed crops"}, weights / "centroids_morphology_candidate.pt")
    (weights / "anomaly_calibration_morphology_candidate.json").write_text(
        json.dumps({"calibration": calibration_by_class["1"], "calibration_by_class": calibration_by_class, "normal_validation_cells": int(len(val_labels))}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
