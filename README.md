# Image Collection and Labeling App for Analog Dials

Image collection and labeling application for analog dial images collected from 
[AI-on-the-Edge Devices](https://github.com/jomjol/AI-on-the-edge-device). Improve analog dial predictions 
by collecting and labeling image data from your own meter device!


## Device Preparation

### 1. Configure ROIs (Regions of Interest)

Proper ROI configuration is essential for accurate training. Ensure the center of the analog dial is 
centered within the ROI.

Refer to the [ROI Configuration Documentation](https://github.com/jomjol/AI-on-the-edge-device/wiki/ROI-Configuration).

### 2. Enable Image Logging

1. Open the device configuration menu.
   ![Config Menu](images/Menu-Config.png)
2. Set up `LogfileRetentionsInDays` and enable logging. Do not change `LogImageLocation` (keep as `/log/analog`).
   ![Logging Config](images/Config-LogImages.png)
3. Wait a few days to accumulate enough images before reading them out.


## Image Collection

### Installation

#### Option 1: Precompiled Executables

Download from [Releases](https://github.com/haverland/collectmeteranalog/releases) for Windows, macOS, or Linux.

```bash
# Windows
collectmeteranalog.exe --collect=<METER IP or NAME>

# Linux/macOS
./collectmeteranalog --collect=<METER IP or NAME>
```

The app downloads the last three days (default: --days=3) of images into `data/` (This step takes quite a while, 
depending on the amount of images to download), hashes the filenames for privacy, removes duplicates, and stores 
labeled images in `data/labeled`.

#### Option 2: Python Package

1. Install [Python](https://www.python.org/downloads/).
2. Install the app:
   ```bash
   pip install git+https://github.com/haverland/collectmeteranalog
   ```
3. Collect images:
   ```bash
   python -m collectmeteranalog --collect=<METER IP or NAME>
   ```

The app downloads the last three days (default: --days=3) of images into `data/` (This step takes quite a while, 
depending on the amount of images to download), hashes the filenames for privacy, removes duplicates, and stores 
labeled images in `data/labeled`.

#### Optional: Enable Prediction for Labeling

Windows and macOS excecutables do not have any prediction functionality pre-installed, because the tflite-runtime 
is only available for linux and the complete tensorflow library is to large (600MB) for a single file application. 
This functionality is only used while labeling the images, but the labeling process will also work without prediction.

To enable image prediction assistance for labeling process for Windows and macOS:

```bash
# Windows
pip install tensorflow

# macOS
pip install tensorflow-macos
```

Collect images + label them with image prediction assistance:
```bash
python -m collectmeteranalog --collect=<METER IP or NAME> --model=<MODEL FILE>
```


## Image Labeling

This application can also be used to properly label the images or adjust existing labels. The labeling process starts 
automatically after image collection is completed or can be manually triggered:

```bash
# Label all images in a folder
python -m collectmeteranalog --labeling="<IMAGE FOLDER>"

# Label specific images listed in a CSV file
python -m collectmeteranalog --labeling="<IMAGE FOLDER>" --labelfile="<LABEL FILE>"
```

With prediction model (Optional | Supported model types: `ana-cont` and `ana-class100`):
```bash
python -m collectmeteranalog --labeling="<IMAGE FOLDER>" --model="<MODEL FILE>"
python -m collectmeteranalog --labeling="<IMAGE FOLDER>" --labelfile="<LABEL FILE>" --model="<MODEL FILE>"
```

### Label File Syntax

The label file is primarily used to refine and optimize existing labels. It is typically generated as an output 
from a model training process. This file usually lists images where model's prediction deviation is high.

**Modern Format:**
```csv
Index,File,Predicted,Expected,Deviation
0,1.3_abc.jpg,2.2,1.3,0.9
1,1.4_def.jpg,2.1,1.4,0.6
```

**Legacy Format:**
```csv
,0
0,/data_raw_images/1.3_abc.jpg
1,/data_raw_images/1.4_def.jpg
```

### Labeling Window

#### Labeling Procedure and Buttons
- Use `+1.0`, `+0.1`, `-1.0` and `-0.1` buttons
- Use the `pageup` (+1.0), `up` (+0.1), `pagedown` (-1.0) and `down` (+1.0) keys.
- Click on the dial in the image plot (ensure tick alignment is correct, because it's saved after click)
- `Update` or `right` key to save labeled image and continue with next image
- `Previous` or `left` key to go back to previous image
- `Delete` to delete actual image (e.g. subpar image quality, misaligned, etc.)
- `Grid` to enable / disable image tick overlay

#### Prediction Visualization (If Activated)
The prediction on the left hand side can help you to identify the number.
But be ware the model can only be a help for you.

**Note:** Always verify model predictions manually.

![Labeling Window](images/Labeling3.png)

### Labeling Example With Missaligned Overlay
Evaluate always like a human would read the dail. This dial is pointing to 1.7. Due to a small 
missalignment of the image the ticks overlay is not placed properly, e.g. the real 1.7 is overlaying 
with tick 1.8. If you would label it like displayed, the image will be labeled with 1.8, which is not 
accurate. Adjust the pointer to tick 1.7, even it's not perfect matches the overlay and "update" label.

![Example](images/ClickonTick.png)


## Options

List all available options:
```bash
python -m collectmeteranalog
```

```bash
Available options:
  -h, --help                    Show this help message and exit
  --collect COLLECT             Collect images from AI-on-the-Edge-Device. Define IP address or name of meter.
  --collectpath COLLECTPATH     Root path for collected images. (default: application root)
  --days DAYS                   Defines in days how many images shall be collected. (default: 3)
  --keepdownloads               Normally all collected images will be deleted. If defined the images are kept.
  --nodownload                  Do not collect any images. Only remove duplicates and start labeling process.
  --startlabel STARTLABEL       Process only images >= startlabel. (default: 0.0)
  --saveduplicates              Save the duplicates in an intermediate subdirectory in raw_images.
  --ticksteps TICKSTEPS         How many label ticks are shown (default: 1, max. 5 | 1=0.1 .. 5=0.5 steps)
  --similiarbits SIMILIARBITS   How many pixels must be different if an image is not similiar to others. (default = 2)
  --labeling LABELING           Path to image folder containing images which shall be labeled.
  --labelfile LABELFILE         Path to a CSV file containing an indexed list of images which shall be labeled.
  --model MODEL                 Path to model file to use prediction functionality (default: off)
  --version                     Print application version
```


## Share Your Data

After labeling, zip the `data/labeled` folder. If it's under 2MB, email it to: **iotson(at)t-online.de**. 
For larger datasets, please contact us for alternatives.