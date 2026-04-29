import os
import cv2

# -------------------------------
# CONFIGURAZIONE
# -------------------------------
dataset_path = "./datasets/USOD10k"      # cartella principale con TR, VAL, TE
output_path = "./datasets/YOLO_USOD10k"  # dove salvare YOLO dataset
class_id = 0                     # tutte le maschere diventano classe 0

splits = {
    "TR": "train",
    "VAL": "val",
    "TE": "test"
}

# Crea le cartelle YOLO
for split in splits.values():
    os.makedirs(os.path.join(output_path, "images", split), exist_ok=True)
    os.makedirs(os.path.join(output_path, "labels", split), exist_ok=True)

# -------------------------------
# FUNZIONE PER CONVERTIRE MASCHERA IN YOLO
# -------------------------------
def mask_to_yolo(mask_path, img_shape):
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    yolo_boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 10:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        x_center = (x + w/2) / img_shape[1]
        y_center = (y + h/2) / img_shape[0]
        w_norm = w / img_shape[1]
        h_norm = h / img_shape[0]
        yolo_boxes.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")
    return yolo_boxes

# -------------------------------
# PROCESSA OGNI SPLIT
# -------------------------------
for split_folder, split_name in splits.items():
    img_folder = os.path.join(dataset_path, split_folder, "RGB")
    mask_folder = os.path.join(dataset_path, split_folder, "GT")

    out_img_folder = os.path.join(output_path, "images", split_name)
    out_label_folder = os.path.join(output_path, "labels", split_name)

    for img_name in os.listdir(img_folder):
        if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        img_path = os.path.join(img_folder, img_name)
        mask_path = os.path.join(mask_folder, img_name)

        # Salta immagini senza maschera
        if not os.path.exists(mask_path):
            print(f"Maschera mancante per {img_name}, salto...")
            continue

        # Copia immagine nella cartella YOLO
        img = cv2.imread(img_path)
        out_img_path = os.path.join(out_img_folder, img_name)
        cv2.imwrite(out_img_path, img)

        # Genera bounding box dalla maschera
        boxes = mask_to_yolo(mask_path, img.shape)

        # Salva file .txt
        label_file = os.path.join(out_label_folder, os.path.splitext(img_name)[0] + ".txt")
        with open(label_file, "w") as f:
            f.write("\n".join(boxes))

print("✅ Conversione completata! Dataset pronto per YOLO.")
