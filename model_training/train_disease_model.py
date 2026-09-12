"""
train_disease_model.py
-----------------------
Trains a tomato leaf disease classifier on the PlantVillage dataset
using transfer learning (MobileNetV2). MobileNetV2 is chosen because:
  - It is small (~14MB) -> loads fast on modest hackathon-demo hardware
  - It trains quickly even on CPU-only Colab/laptop within a few epochs
  - It is accurate enough for leaf-texture/colour based classification

HOW TO USE
----------
1. Download the PlantVillage dataset (Kaggle: "PlantVillage Dataset").
2. Keep only the Tomato___* folders, arranged like:

   dataset/
     Tomato___Bacterial_spot/
     Tomato___Early_blight/
     Tomato___Late_blight/
     Tomato___Leaf_Mold/
     Tomato___Septoria_leaf_spot/
     Tomato___Spider_mites Two-spotted_spider_mite/
     Tomato___Target_Spot/
     Tomato___Tomato_Yellow_Leaf_Curl_Virus/
     Tomato___Tomato_mosaic_virus/
     Tomato___healthy/

3. Set DATASET_DIR below to that folder's path.
4. Run:  python train_disease_model.py
5. Output: disease_model.h5 + class_indices.json saved into model_training/
   Copy both into the modules/ folder (or update the path in
   modules/disease_predictor.py) before running the Flask app.
"""

import json
import os

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ----------------------------- CONFIG -----------------------------
# Resolves to <project_root>/dataset regardless of whether you run this
# script from the project root or from inside model_training/ (VS Code's
# "Run Python File" button runs with cwd = the file's own folder).
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dataset")
IMG_SIZE = (160, 160)            # small & fast; MobileNetV2 default-friendly
BATCH_SIZE = 32
EPOCHS_HEAD = 8                  # train the new classification head
EPOCHS_FINETUNE = 5              # unfreeze top layers of MobileNetV2 and fine-tune
OUTPUT_MODEL_PATH = "disease_model.h5"
OUTPUT_CLASS_MAP = "class_indices.json"
# --------------------------------------------------------------------


def build_data_generators():
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=25,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        validation_split=0.2,
    )

    train_gen = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
    )

    val_gen = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
    )
    return train_gen, val_gen


def build_model(num_classes):
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet"
    )
    base_model.trainable = False  # freeze for the first training phase

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base_model


def main():
    train_gen, val_gen = build_data_generators()
    num_classes = train_gen.num_classes
    print(f"Detected {num_classes} disease classes: {train_gen.class_indices}")

    model, base_model = build_model(num_classes)

    print("\n=== Phase 1: training classification head ===")
    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_HEAD)

    print("\n=== Phase 2: fine-tuning top layers of MobileNetV2 ===")
    base_model.trainable = True
    # only unfreeze the last ~30 layers to avoid overfitting / long training
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_FINETUNE)

    model.save(OUTPUT_MODEL_PATH)
    with open(OUTPUT_CLASS_MAP, "w") as f:
        # invert so index -> class name, which is what predictor.py needs
        json.dump({v: k for k, v in train_gen.class_indices.items()}, f, indent=2)

    print(f"\nSaved model to {OUTPUT_MODEL_PATH}")
    print(f"Saved class index map to {OUTPUT_CLASS_MAP}")


if __name__ == "__main__":
    main()
