#!/usr/bin/env python3
"""
RECI — Entrenamiento local MobileNetV2 (plástico / vidrio).

Reemplaza RECI_entrenar_automatico.ipynb en Colab. Mismo pipeline en 6 pasos,
con reanudación si se interrumpe (Ctrl+C, cierre de sesión, etc.).

Uso típico (dataset en ~/RECI_dataset_propio, copiado desde Google Drive):

  python3 scripts/entrenar_modelo.py

Continuar solo Fase 2 si Fase 1 ya terminó en Colab/Drive:

  python3 scripts/entrenar_modelo.py \\
    --solo-fase 2 \\
    --checkpoint ~/RECI_dataset_propio/runs/run_20260715_1437/mejor_modelo.keras

Ver todas las opciones:

  python3 scripts/entrenar_modelo.py --help
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# TensorFlow se importa después de parsear args (--help sin cargar TF)


EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp")


def _banner(paso: str, titulo: str) -> None:
    print("\n" + "=" * 70)
    print(f" {paso} — {titulo}")
    print("=" * 70)


def contar_imagenes(ruta: Path) -> int:
    if not ruta.is_dir():
        return 0
    return sum(
        1 for f in ruta.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONES
    )


def organizar_dataset(
    rutas_origen: dict[str, Path],
    dataset_dir: Path,
    split_train: float,
    seed: int,
) -> tuple[dict, int]:
    """Copia fotos nuevas del origen → train/val (85/15)."""
    for split in ("train", "val"):
        for clase in rutas_origen:
            (dataset_dir / split / clase).mkdir(parents=True, exist_ok=True)

    total_nuevas = 0
    stats: dict[str, dict[str, int]] = {"train": {}, "val": {}}

    for clase, ruta_origen in rutas_origen.items():
        if not ruta_origen.is_dir():
            raise FileNotFoundError(
                f"No existe {ruta_origen}\n"
                "Copia RECI_dataset_propio desde Drive (plastico/ y vidrio/) "
                "o usa --dataset-base apuntando a la carpeta correcta."
            )

        train_dir = dataset_dir / "train" / clase
        val_dir = dataset_dir / "val" / clase
        ya = {
            f.name for f in train_dir.iterdir()
            if f.suffix.lower() in EXTENSIONES
        } | {
            f.name for f in val_dir.iterdir()
            if f.suffix.lower() in EXTENSIONES
        }

        todas = sorted(
            f.name for f in ruta_origen.iterdir()
            if f.is_file() and f.suffix.lower() in EXTENSIONES
        )
        nuevas = [f for f in todas if f not in ya]

        if nuevas:
            rng = random.Random(seed)
            rng.shuffle(nuevas)
            corte = int(len(nuevas) * split_train)
            for img in nuevas[:corte]:
                shutil.copy(ruta_origen / img, train_dir / img)
            for img in nuevas[corte:]:
                shutil.copy(ruta_origen / img, val_dir / img)
            total_nuevas += len(nuevas)
            print(f"  {clase}: +{len(nuevas)} fotos nuevas copiadas")
        else:
            print(f"  {clase}: sin fotos nuevas ({len(todas)} en origen)")

    print(f"\nFotos nuevas agregadas al split: {total_nuevas}")
    print("\nResumen dataset organizado:")
    total = 0
    for split in ("train", "val"):
        stats[split] = {}
        for clase in rutas_origen:
            n = contar_imagenes(dataset_dir / split / clase)
            stats[split][clase] = n
            total += n
            print(f"  {split}/{clase}: {n}")
    print(f"  TOTAL: {total} fotos")

    if total == 0:
        raise ValueError("Dataset vacío — revisa plastico/ y vidrio/ en --dataset-base.")

    return stats, total_nuevas


def sync_fotos_repo(repo_root: Path, rutas_origen: dict[str, Path]) -> int:
    """Copia fotos_dataset/{clase}/ del repo al origen del dataset."""
    fotos = repo_root / "fotos_dataset"
    copiadas = 0
    for clase, destino in rutas_origen.items():
        origen = fotos / clase
        if not origen.is_dir():
            continue
        destino.mkdir(parents=True, exist_ok=True)
        ya = {f.name for f in destino.iterdir() if f.is_file()}
        for f in origen.iterdir():
            if f.suffix.lower() in EXTENSIONES and f.name not in ya:
                shutil.copy(f, destino / f.name)
                copiadas += 1
    if copiadas:
        print(f"  fotos_dataset → origen: +{copiadas} fotos")
    return copiadas


def cargar_estado(output_dir: Path) -> dict:
    path = output_dir / "training_state.json"
    if path.is_file():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_estado(output_dir: Path, estado: dict) -> None:
    path = output_dir / "training_state.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


def construir_modelo_fase1(tf, clases: int, img_size: int, lr: float):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False
    inputs = tf.keras.Input(shape=(img_size, img_size, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(clases, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def encontrar_mobilenet(model):
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            return layer
    return None


def parse_args() -> argparse.Namespace:
    repo = Path(__file__).resolve().parents[1]
    default_base = Path(
        os.environ.get("RECI_DATASET_BASE", Path.home() / "RECI_dataset_propio")
    )

    p = argparse.ArgumentParser(
        description="Entrenar MobileNetV2 RECI en local (sin Colab)."
    )
    p.add_argument(
        "--dataset-base",
        type=Path,
        default=default_base,
        help=f"Carpeta RECI_dataset_propio (default: {default_base})",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Carpeta del run (default: dataset-base/runs/run_YYYYMMDD_HHMM)",
    )
    p.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Nombre del run (default: run_YYYYMMDD_HHMM)",
    )
    p.add_argument(
        "--sync-fotos-repo",
        action="store_true",
        help="Copiar fotos_dataset/ del repo a plastico/ y vidrio/ antes de organizar",
    )
    p.add_argument(
        "--solo-fase",
        type=int,
        choices=(1, 2, 6),
        default=None,
        help="1=solo Fase 1, 2=solo Fase 2, 6=solo exportar TFLite",
    )
    p.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Keras .keras para reanudar Fase 2 o exportar (mejor_modelo.keras)",
    )
    p.add_argument("--resume", action="store_true", help="Reanudar fase en curso si hay checkpoint")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split-train", type=float, default=0.85)
    p.add_argument("--img-size", type=int, default=224)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--epochs-fase1", type=int, default=15)
    p.add_argument("--epochs-fase2", type=int, default=10)
    p.add_argument("--lr-fase1", type=float, default=0.001)
    p.add_argument("--lr-fase2", type=float, default=5e-5)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument(
        "--instalar-modelo",
        action="store_true",
        help="Copiar model.tflite y labels.txt a model/ si accuracy >= umbral",
    )
    p.add_argument("--umbral-accuracy", type=float, default=0.90)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    import tensorflow as tf

    tf.keras.utils.set_random_seed(args.seed)

    run_id = args.run_id or datetime.now().strftime("run_%Y%m%d_%H%M")
    base = args.dataset_base.expanduser().resolve()
    dataset_dir = base / "dataset_organizado"
    rutas = {
        "plastico": base / "plastico",
        "vidrio": base / "vidrio",
    }
    output_dir = (args.output_dir or (base / "runs" / run_id)).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[1]

    ckpt1 = output_dir / "mejor_modelo.keras"
    ckpt2 = output_dir / "mejor_modelo_ft.keras"

    if args.checkpoint:
        ckpt_src = args.checkpoint.expanduser().resolve()
        if not ckpt_src.is_file():
            print(f"ERROR: checkpoint no encontrado: {ckpt_src}", file=sys.stderr)
            return 1
        if args.solo_fase == 2:
            ckpt1 = ckpt_src
            if args.output_dir is None:
                output_dir = ckpt1.parent
                ckpt2 = output_dir / "mejor_modelo_ft.keras"
        elif args.solo_fase == 6:
            ckpt2 = ckpt_src
            if args.output_dir is None:
                output_dir = ckpt2.parent
        else:
            shutil.copy(ckpt_src, ckpt1)
            print(f"Checkpoint copiado → {ckpt1}")

    _banner("INICIO", f"Entrenamiento local RECI · run {run_id}")
    print(f"Dataset base : {base}")
    print(f"Salida       : {output_dir}")
    gpus = tf.config.list_physical_devices("GPU")
    print(f"TensorFlow   : {tf.__version__}")
    print(f"GPU          : {gpus if gpus else 'ninguna (CPU — más lento; en Mac instala tensorflow-metal)'}")
    if not gpus:
        print(
            "  Tip Mac Apple Silicon: pip install tensorflow-metal\n"
            "  Tip PC con NVIDIA: instala CUDA/cuDNN compatible con TF 2.x"
        )

    estado = cargar_estado(output_dir)
    stats: dict = estado.get("stats_dataset", {})
    best1 = estado.get("best_val_fase1", 0.0)
    best2 = estado.get("best_val_fase2", 0.0)

    skip_organize = args.solo_fase in (2, 6) and args.checkpoint
    if not skip_organize:
        _banner("PASO 2/6", "Organizar dataset (copiar fotos nuevas → train/val 85/15)")
        if args.sync_fotos_repo:
            sync_fotos_repo(repo_root, rutas)
        stats, _ = organizar_dataset(
            rutas, dataset_dir, args.split_train, args.seed
        )
        estado["stats_dataset"] = stats

    if args.solo_fase == 6 and not ckpt2.is_file() and ckpt1.is_file():
        ckpt2 = ckpt1

    need_data = args.solo_fase not in (6,) or not ckpt2.is_file()

    train_ds = val_ds = None
    class_weight = None
    clases_nombres: list[str] = []

    if need_data and args.solo_fase != 6:
        _banner("PASO 3/6", "Preparar datos (augmentation + class weights)")
        aug = tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal", seed=args.seed),
            tf.keras.layers.RandomRotation(0.1, seed=args.seed),
            tf.keras.layers.RandomZoom(0.1, seed=args.seed),
            tf.keras.layers.RandomBrightness(0.1, seed=args.seed),
        ])
        train_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir / "train",
            image_size=(args.img_size, args.img_size),
            batch_size=args.batch_size,
            label_mode="categorical",
            seed=args.seed,
            shuffle=True,
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            dataset_dir / "val",
            image_size=(args.img_size, args.img_size),
            batch_size=args.batch_size,
            label_mode="categorical",
            seed=args.seed,
            shuffle=False,
        )
        clases_nombres = train_ds.class_names
        print("Clases:", clases_nombres)

        conteos = {
            c: contar_imagenes(dataset_dir / "train" / c) for c in clases_nombres
        }
        total_train = sum(conteos.values())
        class_weight = {
            i: total_train / (len(clases_nombres) * conteos[c])
            for i, c in enumerate(clases_nombres)
        }
        print("Conteos train:", conteos)
        print("Class weights:", class_weight)

        autotune = tf.data.AUTOTUNE
        train_ds = train_ds.map(lambda x, y: (aug(x, training=True), y))
        train_ds = train_ds.prefetch(autotune)
        val_ds = val_ds.prefetch(autotune)

    hist1 = hist2 = None

    if args.solo_fase is None:
        run_fase1, run_fase2, run_export = True, True, True
    elif args.solo_fase == 1:
        run_fase1, run_fase2, run_export = True, False, False
    elif args.solo_fase == 2:
        run_fase1, run_fase2, run_export = False, True, True
    else:  # 6
        run_fase1, run_fase2, run_export = False, False, True

    if run_fase1:
        _banner("PASO 4/6", "Fase 1: entrenar capas nuevas (base MobileNetV2 congelada)")
        initial_epoch = 0
        if args.resume and ckpt1.is_file():
            print(f"Reanudando desde {ckpt1}")
            model = tf.keras.models.load_model(ckpt1)
            initial_epoch = estado.get("fase1_epoch", 0)
        else:
            model = construir_modelo_fase1(
                tf, len(clases_nombres), args.img_size, args.lr_fase1
            )

        cb1 = [
            tf.keras.callbacks.ModelCheckpoint(
                str(ckpt1), save_best_only=True, monitor="val_accuracy", verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy",
                patience=args.patience,
                restore_best_weights=True,
                verbose=1,
            ),
            tf.keras.callbacks.CSVLogger(str(output_dir / "fase1_history.csv")),
        ]

        hist1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.epochs_fase1,
            initial_epoch=initial_epoch,
            callbacks=cb1,
            class_weight=class_weight,
        )
        best1 = float(max(hist1.history["val_accuracy"]))
        estado["fase1_epoch"] = len(hist1.history["val_accuracy"])
        estado["best_val_fase1"] = best1
        guardar_estado(output_dir, estado)
        print(f"\n✓ Fase 1 terminada — mejor val_accuracy: {best1:.1%}")

    if run_fase2:
        _banner("PASO 5/6", "Fase 2: fine-tuning (últimas 30 capas MobileNetV2)")
        if not ckpt1.is_file():
            print(f"ERROR: falta {ckpt1} para Fase 2", file=sys.stderr)
            return 1

        model = tf.keras.models.load_model(ckpt1)
        base = encontrar_mobilenet(model)
        if base is None:
            print("ERROR: no se encontró MobileNetV2 en el modelo", file=sys.stderr)
            return 1

        base.trainable = True
        for layer in base.layers[:-30]:
            layer.trainable = False
        model.compile(
            optimizer=tf.keras.optimizers.Adam(args.lr_fase2),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        initial_epoch = 0
        if args.resume and ckpt2.is_file():
            print(f"Reanudando Fase 2 desde {ckpt2}")
            model = tf.keras.models.load_model(ckpt2)
            base = encontrar_mobilenet(model)
            if base:
                base.trainable = True
                for layer in base.layers[:-30]:
                    layer.trainable = False
                model.compile(
                    optimizer=tf.keras.optimizers.Adam(args.lr_fase2),
                    loss="categorical_crossentropy",
                    metrics=["accuracy"],
                )
            initial_epoch = estado.get("fase2_epoch", 0)

        cb2 = [
            tf.keras.callbacks.ModelCheckpoint(
                str(ckpt2), save_best_only=True, monitor="val_accuracy", verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor="val_accuracy",
                patience=args.patience,
                restore_best_weights=True,
                verbose=1,
            ),
            tf.keras.callbacks.CSVLogger(str(output_dir / "fase2_history.csv")),
        ]

        hist2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.epochs_fase2,
            initial_epoch=initial_epoch,
            callbacks=cb2,
            class_weight=class_weight,
        )
        best2 = float(max(hist2.history["val_accuracy"]))
        estado["fase2_epoch"] = len(hist2.history["val_accuracy"])
        estado["best_val_fase2"] = best2
        guardar_estado(output_dir, estado)
        print(f"\n✓ Fase 2 terminada — mejor val_accuracy: {best2:.1%}")

    if run_export:
        _banner("PASO 6/6", "Evaluar + exportar TFLite")
        export_ckpt = ckpt2 if ckpt2.is_file() else ckpt1
        if not export_ckpt.is_file():
            print(f"ERROR: no hay checkpoint para exportar en {output_dir}", file=sys.stderr)
            return 1

        if val_ds is None:
            val_ds = tf.keras.utils.image_dataset_from_directory(
                dataset_dir / "val",
                image_size=(args.img_size, args.img_size),
                batch_size=args.batch_size,
                label_mode="categorical",
                seed=args.seed,
                shuffle=False,
            )
            clases_nombres = val_ds.class_names

        model = tf.keras.models.load_model(export_ckpt)
        loss, accuracy = model.evaluate(val_ds)
        print(f"\nPrecisión final: {accuracy:.1%}")
        print(f"Loss final:      {loss:.4f}")

        y_true, y_pred = [], []
        for batch_x, batch_y in val_ds:
            probs = model.predict(batch_x, verbose=0)
            y_true.extend(np.argmax(batch_y.numpy(), axis=1))
            y_pred.extend(np.argmax(probs, axis=1))

        cm = tf.math.confusion_matrix(
            np.array(y_true), np.array(y_pred), num_classes=len(clases_nombres)
        ).numpy()
        print("\nMatriz de confusión (filas=real, cols=pred):")
        print(cm)

        metricas_clase = {}
        print("\nMétricas por clase:")
        for idx, clase in enumerate(clases_nombres):
            tp = cm[idx, idx]
            fp = cm[:, idx].sum() - tp
            fn = cm[idx, :].sum() - tp
            prec = tp / (tp + fp) if tp + fp else 0.0
            rec = tp / (tp + fn) if tp + fn else 0.0
            f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
            print(f"  {clase:10s} precision={prec:.3f} recall={rec:.3f} f1={f1:.3f}")
            metricas_clase[clase] = {
                "precision": float(prec),
                "recall": float(rec),
                "f1": float(f1),
            }

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_bytes = converter.convert()
        tflite_path = output_dir / "model.tflite"
        labels_path = output_dir / "labels.txt"
        tflite_path.write_bytes(tflite_bytes)
        with open(labels_path, "w", encoding="utf-8") as f:
            for i, c in enumerate(clases_nombres):
                f.write(f"{i} {c}\n")

        manifest = {
            "run_id": run_id,
            "accuracy": float(accuracy),
            "loss": float(loss),
            "best_val_fase1": float(best1),
            "best_val_fase2": float(best2),
            "stats_dataset": stats,
            "class_weight": {str(k): v for k, v in (class_weight or {}).items()},
            "confusion_matrix": cm.tolist(),
            "metricas_por_clase": metricas_clase,
            "clases": clases_nombres,
            "entorno": "local",
        }
        manifest_path = output_dir / "entrenamiento_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        mb = tflite_path.stat().st_size / 1024 / 1024
        print(f"\n✓ model.tflite  ({mb:.1f} MB) → {tflite_path}")
        print(f"✓ labels.txt    → {labels_path}")
        print(f"✓ manifest JSON → {manifest_path}")

        if accuracy >= args.umbral_accuracy:
            print(f"\n🏆 Modelo ≥ {args.umbral_accuracy:.0%} — listo para verificar en RECI")
        else:
            print(f"\n⚠️  Precisión < {args.umbral_accuracy:.0%} — revisa fotos antes de producción")

        if args.instalar_modelo and accuracy >= args.umbral_accuracy:
            dest_model = repo_root / "model"
            dest_model.mkdir(parents=True, exist_ok=True)
            shutil.copy(tflite_path, dest_model / "model.tflite")
            shutil.copy(labels_path, dest_model / "labels.txt")
            print(f"✓ Copiado a {dest_model}/")

        print("\nVerificar:")
        print(f"  cp {tflite_path} model/model.tflite")
        print("  python3 tests/test_imagenes_completo.py")

    print("\nEntrenamiento local finalizado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
