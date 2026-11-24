
import os
import csv
import json
import shutil
import tempfile

from pathlib import Path
from datetime import datetime, timezone
import kagglehub


# ==========================================
# KONFIGURASI DATASET
# ==========================================

DATASET_HANDLE = (
    "bwandowando/"
    "tomtom-traffic-data-55-countries-387-cities"
)

DATASET_URL = (
    "https://www.kaggle.com/datasets/"
    + DATASET_HANDLE
)

OUTPUT_DIR = Path("data/hasil_scraping")


# ==========================================
# FUNGSI DOWNLOAD DATASET
# ==========================================

def download_dataset():

    print("=" * 50)
    print("MEMULAI DOWNLOAD DATASET TOMTOM TRAFFIC")
    print("=" * 50)

    # Pastikan output lama dibersihkan
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download dataset ke temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        print("\nMengunduh dataset dari Kaggle...")

        downloaded_path = kagglehub.dataset_download(
            DATASET_HANDLE,
            output_dir=temp_dir,
            force_download=True
        )

        source_dir = Path(downloaded_path)

        if not source_dir.exists():
            raise FileNotFoundError(
                "Folder hasil download Kaggle tidak ditemukan"
            )

        # Salin seluruh file asli dataset
        file_list = []

        for file_path in source_dir.rglob("*"):

            if not file_path.is_file():
                continue

            relative_path = file_path.relative_to(source_dir)

            destination = OUTPUT_DIR / relative_path

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(file_path, destination)

            file_list.append(destination)

    if not file_list:
        raise ValueError(
            "Dataset berhasil diakses tetapi tidak ada file ditemukan"
        )

    print(f"\nJumlah file ditemukan: {len(file_list)}")


    # ======================================
    # MEMBUAT MANIFEST DATASET
    # ======================================

    manifest_path = OUTPUT_DIR / "manifest.csv"

    with open(
        manifest_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "file_name",
                "file_path",
                "file_format",
                "file_size_bytes"
            ]
        )

        writer.writeheader()

        for file_path in file_list:

            writer.writerow({
                "file_name": file_path.name,
                "file_path": str(
                    file_path.relative_to(OUTPUT_DIR)
                ),
                "file_format": file_path.suffix.lower(),
                "file_size_bytes": file_path.stat().st_size
            })


    # ======================================
    # MEMBUAT METADATA
    # ======================================

    total_size = sum(
        file.stat().st_size for file in file_list
    )

    metadata = {
        "dataset_name": "TomTom Traffic Data",
        "dataset_source": "Kaggle",
        "dataset_owner": "bwandowando",
        "dataset_handle": DATASET_HANDLE,
        "dataset_url": DATASET_URL,
        "downloaded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_files": len(file_list),
        "total_size_bytes": total_size,
        "status": "success"
    }

    metadata_path = OUTPUT_DIR / "metadata.json"

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ======================================
    # HASIL AKHIR
    # ======================================

    print("\n" + "=" * 50)
    print("DOWNLOAD DATASET BERHASIL")
    print("=" * 50)

    print(f"Dataset       : {DATASET_HANDLE}")
    print(f"Jumlah file   : {len(file_list)}")
    print(f"Ukuran total  : {total_size:,} bytes")
    print(f"Lokasi output : {OUTPUT_DIR}")

    print("\nFile yang dihasilkan:")

    for file_path in OUTPUT_DIR.rglob("*"):

        if file_path.is_file():
            print(f"- {file_path.relative_to(OUTPUT_DIR)}")

    return OUTPUT_DIR


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    download_dataset()
