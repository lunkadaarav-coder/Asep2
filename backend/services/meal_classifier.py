"""Meal classifier service using EfficientNet-B4 for offline inference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError
import torch
import torch.nn.functional as F
from torchvision import models, transforms

BASE_DIR = Path(__file__).resolve().parents[1]

CANDIDATE_MODEL_DIRS = [
    BASE_DIR / "models",
    BASE_DIR / "model_assets",
    BASE_DIR.parent / "models",
]

WEIGHTS_CANDIDATES = [
    "best_classifier_model.pth",
    "best_classifier_model.pt",
    "meal_classifier_model.pth",
    "model.pth",
]
CLASS_NAMES_CANDIDATES = [
    "class_names.json",
    "classes.json",
    "labels.json",
]

HIGH_CARB_FOODS = {
    "biryani", "fried_rice", "pizza", "burger", "chapati", "chole_bhature"
}
HIGH_SUGAR_FOODS = {
    "jalebi", "gulab_jamun", "rasgulla", "ras_malai", "mysore_pak", "modak"
}
FRIED_FOODS = {
    "samosa", "pakode", "butter_naan", "chole_bhature"
}

_TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_model: torch.nn.Module | None = None
_class_names: list[str] | None = None
_model_error: str | None = None


def _resolve_artifact(filenames: list[str], artifact_type: str) -> Path:
    for model_dir in CANDIDATE_MODEL_DIRS:
        for filename in filenames:
            candidate = model_dir / filename
            if candidate.exists():
                return candidate

        for filename in filenames:
            matches = list(model_dir.glob(f"**/{filename}"))
            if matches:
                return matches[0]

    primary_dir = CANDIDATE_MODEL_DIRS[0]
    expected = ", ".join(str(primary_dir / name) for name in filenames)
    raise FileNotFoundError(
        f"{artifact_type} not found. Place files in '{primary_dir}' (e.g. {expected})."
    )


def _parse_class_names_payload(payload: Any) -> list[str]:
    if isinstance(payload, list):
        labels = [str(item) for item in payload]
    elif isinstance(payload, dict):
        if all(str(k).isdigit() for k in payload.keys()):
            labels = [str(label) for _, label in sorted(payload.items(), key=lambda kv: int(kv[0]))]
        elif all(isinstance(v, int) for v in payload.values()):
            by_index = sorted(payload.items(), key=lambda kv: kv[1])
            labels = [str(name) for name, _ in by_index]
        else:
            raise ValueError("Unsupported class_names.json dict format")
    else:
        raise ValueError("class_names.json must be a list or a dict")

    if not labels:
        raise ValueError("class_names.json is empty")

    return labels


def _load_class_names() -> list[str]:
    class_names_path = _resolve_artifact(CLASS_NAMES_CANDIDATES, "Class names file")
    with class_names_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return _parse_class_names_payload(payload)


def _extract_state_dict(checkpoint: Any) -> dict[str, torch.Tensor]:
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    elif isinstance(checkpoint, dict):
        state_dict = checkpoint
    else:
        raise ValueError("Unsupported checkpoint format")

    cleaned: dict[str, torch.Tensor] = {}
    for key, value in state_dict.items():
        key = key.replace("module.", "")
        key = key.replace("model.", "")
        cleaned[key] = value
    return cleaned


def _checkpoint_num_classes(state_dict: dict[str, torch.Tensor]) -> int | None:
    for key in ("classifier.1.weight", "classifier.weight", "fc.weight"):
        if key in state_dict and hasattr(state_dict[key], "shape"):
            return int(state_dict[key].shape[0])
    return None


def _labels_from_checkpoint_meta(checkpoint: Any) -> list[str] | None:
    if not isinstance(checkpoint, dict):
        return None

    class_to_idx = checkpoint.get("class_to_idx")
    if isinstance(class_to_idx, dict) and class_to_idx:
        by_index = sorted(class_to_idx.items(), key=lambda kv: int(kv[1]))
        return [str(name) for name, _ in by_index]

    return None


def _build_model_and_labels() -> tuple[torch.nn.Module, list[str]]:
    weights_path = _resolve_artifact(WEIGHTS_CANDIDATES, "Model weights")
    checkpoint = torch.load(weights_path, map_location=torch.device("cpu"))
    state_dict = _extract_state_dict(checkpoint)

    labels = _labels_from_checkpoint_meta(checkpoint) or _load_class_names()

    inferred_classes = _checkpoint_num_classes(state_dict)
    if inferred_classes is not None and inferred_classes != len(labels):
        raise ValueError(
            f"Class mismatch: checkpoint expects {inferred_classes} classes but labels provide {len(labels)}"
        )

    model = models.efficientnet_b4(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, len(labels))
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model, labels


def load_meal_model() -> None:
    """Load classifier + labels once and cache for all requests."""
    global _model, _class_names, _model_error

    if _model is not None and _class_names is not None:
        return

    try:
        model, labels = _build_model_and_labels()
        _model = model
        _class_names = labels
        _model_error = None
    except Exception as exc:  # noqa: BLE001
        _model = None
        _class_names = None
        _model_error = str(exc)
        raise


def ensure_model_ready() -> None:
    if _model is None or _class_names is None:
        if _model_error:
            raise RuntimeError(_model_error)
        load_meal_model()


def _compute_health_flags(predicted_food: str, patient_profile: dict[str, float] | None) -> list[str]:
    if not patient_profile:
        return []

    flags: list[str] = []
    predicted_food = predicted_food.lower()

    hba1c = patient_profile.get("hba1c")
    ldl = patient_profile.get("ldl")
    triglycerides = patient_profile.get("triglycerides")

    if predicted_food in HIGH_CARB_FOODS and (hba1c is not None and hba1c >= 5.7):
        flags.append("High carbohydrate food")

    if predicted_food in HIGH_SUGAR_FOODS and (hba1c is not None and hba1c >= 5.7):
        flags.append("High sugar food")

    lipid_risk = (ldl is not None and ldl >= 130) or (triglycerides is not None and triglycerides >= 150)
    if predicted_food in FRIED_FOODS and lipid_risk:
        flags.append("Fried food risk")

    return flags


def classify_meal_image(image_path: str, patient_profile: dict[str, float] | None = None) -> dict[str, Any]:
    ensure_model_ready()

    if _model is None or _class_names is None:
        raise RuntimeError("Meal classifier is not available")

    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            tensor = _TRANSFORM(image).unsqueeze(0)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Invalid image file. Please upload a valid image.") from exc

    with torch.no_grad():
        logits = _model(tensor)
        probabilities = F.softmax(logits, dim=1)[0]

    top_k = min(3, len(_class_names))
    top_probs, top_indices = torch.topk(probabilities, k=top_k)

    top_3 = [
        {"label": _class_names[idx], "confidence": round(prob * 100, 2)}
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist())
    ]

    predicted_food = top_3[0]["label"]
    top_confidence = top_3[0]["confidence"]

    result: dict[str, Any] = {
        "predicted_food": predicted_food,
        "confidence": top_confidence,
        "top_3": top_3,
        "status": "Confident" if top_confidence >= 60 else "Uncertain",
    }

    health_flags = _compute_health_flags(predicted_food, patient_profile)
    if health_flags:
        result["health_flags"] = health_flags

    return result
