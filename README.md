# nnU-Net v2 pipeline for liver CT segmentation (3D-IRCADb-01)

This repository shows how to prepare a CT dataset for nnU-Net v2, train a 3D model on Google Colab, and make predictions. It comes from my internship work on automatic segmentation of liver structures in CT images.

> **No patient data in this repository.** You must download the dataset yourself. See [Data](#data).

## Contents

| Path | Purpose |
|---|---|
| `scripts/convert_ircadb_to_nnunet.py` | Converts 3D-IRCADb-01 (DICOM) to the nnU-Net v2 format |
| `notebooks/nnunet_colab.ipynb` | Colab notebook: install, plan, train, resume, predict |
| `requirements.txt` | Python packages |

## Data

Download 3D-IRCADb-01 from the official IRCAD website and read its licence terms. The database has 20 patient folders. Each folder has `PATIENT_DICOM`, `LABELLED_DICOM`, `MASKS_DICOM` and `MESHES_VTK`.

Check which mask folders exist before conversion. The names change between patients, and not every patient has every structure.

## Setup

1. Convert the data on your computer (no GPU needed):
   ```bash
   pip install -r requirements.txt
   python scripts/convert_ircadb_to_nnunet.py \
       --src 3D-IRCADb-01 --out Dataset001_IRCADb \
       --labels liver=1,livertumors=2
   ```
   Put the small structures last in `--labels`. Later labels overwrite earlier labels.
2. Copy `Dataset001_IRCADb` to `MyDrive/nnunet/raw/` in Google Drive.
3. Open `notebooks/nnunet_colab.ipynb` in Colab. Select a **T4 GPU**. Run the cells in order.

## Important notes

- **Out of RAM during preprocessing:** use `-np 1`, or use a High-RAM runtime. Free Colab has about 12 GB.
- **Disconnects:** all paths are on Google Drive. After a disconnect, run the environment cell again and then train with `--c`. Without `--c`, training starts at epoch 0.
- **Checkpoints:** nnU-Net saves `checkpoint_latest.pth` every 50 epochs by default. The notebook changes this to 10. Do this before training starts.
- **Trainer name:** use the same `-tr` value (here `nnUNetTrainer_100epochs`) for training and prediction. The results folder name contains it.
- **Warnings from `torch.compile`:** you can ignore them. Set `nnUNet_compile=false` to hide them.
- **Mac:** nnU-Net needs CUDA for practical training. Use Mac only for data preparation and viewing.

## Results

Fill this table after training.

| Configuration | Fold | Epochs | Dice (liver) | Dice (tumor) | HD95 |
|---|---|---|---|---|---|
| 3d_fullres | 0 | 100 | _TBD_ | _TBD_ | _TBD_ |

Hardware: Colab T4 GPU. nnU-Net version: _TBD_.

## View the results in 3D Slicer

1. Load the CT and the prediction (**File > Add Data**). Tick **LabelMap** for the prediction.
2. Right-click the label map in **Data** and choose **Convert labelmap to segmentation node**.
3. In **Segmentations**, create the closed surface and enable **Show 3D**.

## References

- Isensee, F., et al. *nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation.* Nature Methods 18, 203–211 (2021).
- 3D-IRCADb-01 dataset: IRCAD, Strasbourg.

## Licence

MIT. See `LICENSE`. The dataset has its own licence.
