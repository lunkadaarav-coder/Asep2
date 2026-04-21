"""HealthMitra Scan – Food Detector Service (Real YOLOv8 with fallback)"""
import os
import random
import logging

logger = logging.getLogger(__name__)

# ── Try to import YOLOv8 ────────────────────────────────────────────
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics not installed. Using simulated food detection.")


# ── Indian food nutrition database ──────────────────────────────────
INDIAN_FOODS = {
    "dal_rice": {
        "name": "Dal Rice (दाल चावल)",
        "category": "Main Course",
        "calories": 350, "protein": 12, "carbs": 55, "fat": 8, "fiber": 6,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Good source of protein", "Rich in fiber", "Complete amino acids"]
    },
    "butter_chicken": {
        "name": "Butter Chicken (बटर चिकन)",
        "category": "Main Course",
        "calories": 490, "protein": 28, "carbs": 15, "fat": 35, "fiber": 2,
        "is_safe": True,
        "warnings": ["High in fat", "High calorie – limit portion if diabetic"],
        "benefits": ["High protein", "Good source of iron"]
    },
    "roti": {
        "name": "Roti / Chapati (रोटी)",
        "category": "Bread",
        "calories": 120, "protein": 3.5, "carbs": 25, "fat": 1.5, "fiber": 3,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Whole grain", "Low fat", "Good source of fiber"]
    },
    "samosa": {
        "name": "Samosa (समोसा)",
        "category": "Snack",
        "calories": 310, "protein": 5, "carbs": 32, "fat": 18, "fiber": 2,
        "is_safe": False,
        "warnings": ["Deep fried – avoid if heart patient", "High in trans fats", "Spike blood sugar"],
        "benefits": ["Contains potatoes (potassium)"]
    },
    "biryani": {
        "name": "Chicken Biryani (बिरयानी)",
        "category": "Main Course",
        "calories": 450, "protein": 18, "carbs": 52, "fat": 18, "fiber": 3,
        "is_safe": True,
        "warnings": ["High calorie – watch portion size", "High glycemic index"],
        "benefits": ["Protein from chicken", "Spices have anti-inflammatory properties"]
    },
    "paneer_tikka": {
        "name": "Paneer Tikka (पनीर टिक्का)",
        "category": "Appetizer",
        "calories": 280, "protein": 18, "carbs": 8, "fat": 20, "fiber": 2,
        "is_safe": True,
        "warnings": ["High fat from cheese"],
        "benefits": ["High protein", "Good calcium source", "Low carb"]
    },
    "gulab_jamun": {
        "name": "Gulab Jamun (गुलाब जामुन)",
        "category": "Dessert",
        "calories": 380, "protein": 4, "carbs": 55, "fat": 16, "fiber": 0.5,
        "is_safe": False,
        "warnings": ["Very high sugar – AVOID if diabetic", "High calorie", "Deep fried"],
        "benefits": []
    },
    "idli": {
        "name": "Idli (इडली)",
        "category": "Breakfast",
        "calories": 80, "protein": 2, "carbs": 16, "fat": 0.5, "fiber": 1,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Low fat", "Easy to digest", "Fermented – good for gut"]
    },
    "chole_bhature": {
        "name": "Chole Bhature (छोले भटूरे)",
        "category": "Main Course",
        "calories": 520, "protein": 14, "carbs": 58, "fat": 26, "fiber": 8,
        "is_safe": False,
        "warnings": ["Deep fried bhature", "Very high calorie", "Avoid if heart patient"],
        "benefits": ["Chickpeas are protein-rich", "Good fiber from chole"]
    },
    "palak_paneer": {
        "name": "Palak Paneer (पालक पनीर)",
        "category": "Main Course",
        "calories": 260, "protein": 14, "carbs": 10, "fat": 18, "fiber": 4,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Iron-rich spinach", "High protein", "Good calcium"]
    },
    "jalebi": {
        "name": "Jalebi (जलेबी)",
        "category": "Dessert",
        "calories": 420, "protein": 2, "carbs": 68, "fat": 15, "fiber": 0,
        "is_safe": False,
        "warnings": ["Extremely high sugar – DANGEROUS for diabetics", "Deep fried", "No nutritional value"],
        "benefits": []
    },
    "dosa": {
        "name": "Masala Dosa (मसाला डोसा)",
        "category": "Breakfast",
        "calories": 210, "protein": 5, "carbs": 30, "fat": 8, "fiber": 2,
        "is_safe": True,
        "warnings": ["Moderate oil in preparation"],
        "benefits": ["Fermented batter – good probiotics", "Rice + lentil = complete protein"]
    }
}

# ── COCO class → Indian food / generic food mapping ─────────────────
# YOLOv8 COCO classes that are food-related (class IDs 46-58 approx)
COCO_FOOD_MAP = {
    "banana": {
        "name": "Banana (केला)",
        "category": "Fruit",
        "calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4, "fiber": 3.1,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Rich in potassium", "Good energy source", "Helps digestion"]
    },
    "apple": {
        "name": "Apple (सेब)",
        "category": "Fruit",
        "calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3, "fiber": 4.4,
        "is_safe": True,
        "warnings": [],
        "benefits": ["High in fiber", "Rich in antioxidants", "Heart-healthy"]
    },
    "orange": {
        "name": "Orange (संतरा)",
        "category": "Fruit",
        "calories": 62, "protein": 1.2, "carbs": 15, "fat": 0.2, "fiber": 3.1,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Rich in Vitamin C", "Boosts immunity", "Good hydration"]
    },
    "sandwich": {
        "name": "Burger / Sandwich (बर्गर / सैंडविच)",
        "category": "Fast Food",
        "calories": 350, "protein": 15, "carbs": 35, "fat": 18, "fiber": 2,
        "is_safe": True,
        "warnings": ["May be high in fat", "Processed ingredients – limit intake", "High sodium content"],
        "benefits": ["Good protein source", "Quick meal option"]
    },
    "pizza": {
        "name": "Pizza (पिज़्ज़ा)",
        "category": "Fast Food",
        "calories": 285, "protein": 12, "carbs": 36, "fat": 10, "fiber": 2,
        "is_safe": True,
        "warnings": ["High in sodium", "Processed cheese – limit intake"],
        "benefits": ["Contains vegetables (if veggie pizza)", "Calcium from cheese"]
    },
    "cake": {
        "name": "Cake (केक)",
        "category": "Dessert",
        "calories": 350, "protein": 4, "carbs": 50, "fat": 16, "fiber": 1,
        "is_safe": False,
        "warnings": ["Very high sugar", "High calorie", "Avoid if diabetic"],
        "benefits": []
    },
    "donut": {
        "name": "Donut (डोनट)",
        "category": "Dessert",
        "calories": 290, "protein": 3, "carbs": 33, "fat": 16, "fiber": 1,
        "is_safe": False,
        "warnings": ["Deep fried", "High sugar", "Avoid if heart patient"],
        "benefits": []
    },
    "hot dog": {
        "name": "Hot Dog",
        "category": "Fast Food",
        "calories": 290, "protein": 11, "carbs": 24, "fat": 17, "fiber": 1,
        "is_safe": True,
        "warnings": ["Processed meat – limit intake", "High sodium"],
        "benefits": ["Protein source"]
    },
    "carrot": {
        "name": "Carrot (गाजर)",
        "category": "Vegetable",
        "calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "fiber": 2.8,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Rich in Vitamin A", "Good for eyes", "Antioxidant-rich"]
    },
    "broccoli": {
        "name": "Broccoli (ब्रोकोली)",
        "category": "Vegetable",
        "calories": 55, "protein": 3.7, "carbs": 11, "fat": 0.6, "fiber": 5.1,
        "is_safe": True,
        "warnings": [],
        "benefits": ["High in fiber", "Rich in Vitamin C & K", "Anti-cancer properties"]
    },
    "bowl": {
        "name": "Food Bowl (कटोरा)",
        "category": "Main Course",
        "calories": 300, "protein": 12, "carbs": 40, "fat": 10, "fiber": 4,
        "is_safe": True,
        "warnings": [],
        "benefits": ["Balanced meal option"]
    },
    "cup": {
        "name": "Chai / Beverage (चाय)",
        "category": "Beverage",
        "calories": 50, "protein": 1, "carbs": 8, "fat": 1.5, "fiber": 0,
        "is_safe": True,
        "warnings": ["Limit sugar in tea"],
        "benefits": ["Contains antioxidants", "Mild energy boost"]
    },
    "dining table": None,  # Not food — skip
    "bottle": None,  # Not food — skip
    "wine glass": None,
    "fork": None,
    "knife": None,
    "spoon": None,
}

# All COCO food class names
COCO_FOOD_CLASSES = {
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
    "hot dog", "pizza", "donut", "cake", "bowl", "cup",
}

# ── Cached YOLO model ──────────────────────────────────────────────
_yolo_model = None


def _get_yolo_model():
    """Load YOLOv8 model (cached singleton)."""
    global _yolo_model
    if _yolo_model is None:
        try:
            from config import YOLO_MODEL_NAME
            model_name = YOLO_MODEL_NAME
        except Exception:
            model_name = "yolov8n.pt"
        logger.info(f"Loading YOLOv8 model: {model_name}")
        _yolo_model = YOLO(model_name)
    return _yolo_model


def _detect_with_yolo(image_path: str) -> list:
    """Run YOLOv8 inference on an image and return detected food items."""
    try:
        from config import YOLO_CONFIDENCE_THRESHOLD
        conf_threshold = YOLO_CONFIDENCE_THRESHOLD
    except Exception:
        conf_threshold = 0.25

    model = _get_yolo_model()
    results = model(image_path, conf=conf_threshold, verbose=False)

    detected_items = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])

            # Check if it's a food-related class
            if class_name in COCO_FOOD_CLASSES:
                food_info = COCO_FOOD_MAP.get(class_name)
                if food_info is not None:
                    detected_items.append({
                        "class_name": class_name,
                        "confidence": round(confidence, 2),
                        "food_info": food_info,
                        "bbox": box.xyxy[0].tolist()
                    })

    return detected_items


def detect_food(image_path: str, scan_type: str = "single") -> dict:
    """
    Detect food items in an image using YOLOv8.
    Falls back to simulated detection if ultralytics is not available.

    Returns: dict with detected_foods, nutrition, warnings, scan_type, total_items
    """
    detected_foods = []
    total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
    all_warnings = []
    source = "simulated"

    # ── Try real YOLOv8 detection ───────────────────────────────────
    if YOLO_AVAILABLE:
        try:
            yolo_results = _detect_with_yolo(image_path)

            if yolo_results:
                source = "yolov8"
                for item in yolo_results:
                    food = item["food_info"]
                    detected_foods.append({
                        "name": food["name"],
                        "confidence": item["confidence"],
                        "category": food["category"],
                        "is_safe": food["is_safe"],
                        "calories": food["calories"],
                        "protein": food["protein"],
                        "carbs": food["carbs"],
                        "fat": food["fat"],
                        "fiber": food["fiber"],
                        "warnings": food["warnings"],
                        "benefits": food.get("benefits", [])
                    })

                    total_nutrition["calories"] += food["calories"]
                    total_nutrition["protein"] += food["protein"]
                    total_nutrition["carbs"] += food["carbs"]
                    total_nutrition["fat"] += food["fat"]
                    total_nutrition["fiber"] += food["fiber"]
                    all_warnings.extend(food["warnings"])

                logger.info(f"YOLOv8 detected {len(detected_foods)} food items")

                return {
                    "detected_foods": detected_foods,
                    "nutrition": total_nutrition,
                    "warnings": list(set(all_warnings)),
                    "scan_type": scan_type,
                    "total_items": len(detected_foods),
                    "source": source
                }
            else:
                logger.info("YOLOv8 detected no food items, falling back to simulated")

        except Exception as e:
            logger.error(f"YOLOv8 detection failed: {e}. Falling back to simulated.")

    # ── Fallback: simulated detection ───────────────────────────────
    logger.info("Using simulated food detection")
    food_keys = list(INDIAN_FOODS.keys())

    if scan_type == "meal":
        num_items = random.randint(3, 5)
    else:
        num_items = random.randint(1, 2)

    selected_keys = random.sample(food_keys, min(num_items, len(food_keys)))

    for key in selected_keys:
        food = INDIAN_FOODS[key]
        confidence = round(random.uniform(0.78, 0.99), 2)

        detected_foods.append({
            "name": food["name"],
            "confidence": confidence,
            "category": food["category"],
            "is_safe": food["is_safe"],
            "calories": food["calories"],
            "protein": food["protein"],
            "carbs": food["carbs"],
            "fat": food["fat"],
            "fiber": food["fiber"],
            "warnings": food["warnings"],
            "benefits": food.get("benefits", [])
        })

        total_nutrition["calories"] += food["calories"]
        total_nutrition["protein"] += food["protein"]
        total_nutrition["carbs"] += food["carbs"]
        total_nutrition["fat"] += food["fat"]
        total_nutrition["fiber"] += food["fiber"]
        all_warnings.extend(food["warnings"])

    return {
        "detected_foods": detected_foods,
        "nutrition": total_nutrition,
        "warnings": list(set(all_warnings)),
        "scan_type": scan_type,
        "total_items": len(detected_foods),
        "source": source
    }
