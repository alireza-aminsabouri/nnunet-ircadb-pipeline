"""Convert 3D-IRCADb-01 (DICOM) to the nnU-Net v2 raw dataset format.

Example:
    python scripts/convert_ircadb_to_nnunet.py \
        --src 3D-IRCADb-01 --out Dataset001_IRCADb \
        --labels liver=1,livertumors=2
"""
import argparse
import glob
import json
import os

import numpy as np
import SimpleITK as sitk


def read_series(folder):
    files = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(folder)
    return sitk.ReadImage(files)


def parse_labels(text):
    labels = {}
    for item in text.split(","):
        name, value = item.split("=")
        labels[name.strip()] = int(value)
    return labels


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="Folder with the patient folders")
    p.add_argument("--out", default="Dataset001_IRCADb", help="Output dataset folder")
    p.add_argument("--labels", default="liver=1,livertumors=2",
                   help="Mask folder name = label ID. Put small structures last.")
    args = p.parse_args()

    labels = parse_labels(args.labels)
    os.makedirs(f"{args.out}/imagesTr", exist_ok=True)
    os.makedirs(f"{args.out}/labelsTr", exist_ok=True)

    n = 0
    for pdir in sorted(glob.glob(f"{args.src}/*/")):
        ct_dir = os.path.join(pdir, "PATIENT_DICOM")
        if not os.path.isdir(ct_dir):
            continue
        ct = read_series(ct_dir)
        seg = np.zeros(sitk.GetArrayFromImage(ct).shape, dtype=np.uint8)

        for name, label_id in labels.items():
            mask_dir = os.path.join(pdir, "MASKS_DICOM", name)
            if not os.path.isdir(mask_dir):
                continue
            mask = sitk.GetArrayFromImage(read_series(mask_dir))
            if mask.shape != seg.shape:
                print(f"Shape mismatch in {pdir} ({name}). Skipped.")
                continue
            seg[mask > 0] = label_id  # later labels overwrite earlier ones

        n += 1
        case_id = f"ircad_{n:03d}"
        seg_img = sitk.GetImageFromArray(seg)
        seg_img.CopyInformation(ct)  # keep spacing, origin and direction
        sitk.WriteImage(ct, f"{args.out}/imagesTr/{case_id}_0000.nii.gz")
        sitk.WriteImage(seg_img, f"{args.out}/labelsTr/{case_id}.nii.gz")

    dataset = {
        "channel_names": {"0": "CT"},
        "labels": {"background": 0, **labels},
        "numTraining": n,
        "file_ending": ".nii.gz",
    }
    with open(f"{args.out}/dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Done. Cases written: {n}")


if __name__ == "__main__":
    main()
