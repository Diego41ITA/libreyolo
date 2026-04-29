from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_files(folder: Path, extensions: set[str]) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Cartella non trovata: {folder}")

    return sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in extensions
        ),
        key=lambda path: path.name.lower(),
    )


def stems(paths: list[Path]) -> set[str]:
    return {path.stem for path in paths}


def print_list(title: str, paths: list[Path], limit: int) -> None:
    print(f"{title}: {len(paths)}")
    for path in paths[:limit]:
        print(f"  - {path}")
    if len(paths) > limit:
        print(f"  ... altri {len(paths) - limit} file")


def delete_files(paths: list[Path]) -> int:
    deleted = 0
    for path in paths:
        path.unlink()
        deleted += 1
    return deleted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Pulisce FrameEtichettati mantenendo frames come riferimento. "
            "Ogni immagine in frames deve avere un .txt in frames_labels e "
            "un'immagine con lo stesso nome in frames_original."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("FrameEtichettati"),
        help="Cartella principale con frames, frames_labels e frames_original.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Cancella davvero i file. Senza questa opzione mostra solo l'anteprima.",
    )
    parser.add_argument(
        "--prune-frames",
        action="store_true",
        help=(
            "Cancella anche da frames le immagini senza .txt o senza originale "
            "corrispondente."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Numero massimo di file mostrati per ogni lista.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root
    frames_dir = root / "frames"
    labels_dir = root / "frames_labels"
    originals_dir = root / "frames_original"

    frame_files = collect_files(frames_dir, IMAGE_EXTENSIONS)
    label_files = collect_files(labels_dir, {".txt"})
    original_files = collect_files(originals_dir, IMAGE_EXTENSIONS)

    frame_stems = stems(frame_files)
    label_stems = stems(label_files)
    original_stems = stems(original_files)

    labels_to_delete = [
        path for path in label_files if path.stem not in frame_stems
    ]
    originals_to_delete = [
        path for path in original_files if path.stem not in frame_stems
    ]

    missing_labels = sorted(frame_stems - label_stems)
    missing_originals = sorted(frame_stems - original_stems)
    incomplete_frame_stems = (frame_stems - label_stems) | (
        frame_stems - original_stems
    )
    frames_to_delete = [
        path for path in frame_files if path.stem in incomplete_frame_stems
    ]

    print(f"Root: {root}")
    print(f"Modalita: {'cancellazione' if args.delete else 'anteprima'}")
    print(f"Immagini in frames: {len(frame_files)}")
    print(f"Label .txt in frames_labels: {len(label_files)}")
    print(f"Originali in frames_original: {len(original_files)}")
    print()

    print_list("Label senza immagine corrispondente in frames", labels_to_delete, args.limit)
    print_list(
        "Originali senza immagine corrispondente in frames",
        originals_to_delete,
        args.limit,
    )
    print(f"Immagini in frames senza label .txt: {len(missing_labels)}")
    print(f"Immagini in frames senza originale: {len(missing_originals)}")

    if args.prune_frames:
        print_list(
            "Immagini in frames senza coppia completa",
            frames_to_delete,
            args.limit,
        )

    if not args.delete:
        print()
        print("Anteprima completata. Aggiungi --delete per cancellare davvero.")
        return

    deleted_labels = delete_files(labels_to_delete)
    deleted_originals = delete_files(originals_to_delete)
    deleted_frames = delete_files(frames_to_delete) if args.prune_frames else 0

    print()
    print(f"File .txt cancellati da frames_labels: {deleted_labels}")
    print(f"Originali cancellati da frames_original: {deleted_originals}")
    if args.prune_frames:
        print(f"Immagini cancellate da frames: {deleted_frames}")
    print("Pulizia completata.")


if __name__ == "__main__":
    main()
