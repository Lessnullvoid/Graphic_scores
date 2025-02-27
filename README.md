# Graphic Score Analyzer and OSC Transmitter

A Python-based tool for analyzing graphical scores and converting visual information into OSC (Open Sound Control) data for real-time musical/sonic interpretation. This project uses the SIFT (Scale-Invariant Feature Transform) algorithm to detect and analyze visual features, making it particularly useful for experimental music, sound art, and interactive audio installations.

## SIFT Algorithm Overview

SIFT (Scale-Invariant Feature Transform) is a computer vision algorithm that detects and describes local features in images. In the context of this project, SIFT is used to analyze graphical scores with the following key characteristics:

### Key Features of SIFT

1. **Scale Invariance**
   - Detects features regardless of their size in the image
   - Particularly useful for identifying musical elements at different scales
   - Maintains consistency when zooming in/out of the score

2. **Rotation Invariance**
   - Recognizes features regardless of their orientation
   - Enables analysis of rotated or transformed musical notation
   - Maintains feature detection despite page orientation

3. **Keypoint Detection**
   - Identifies distinctive points in the image
   - Focuses on areas with high contrast and unique visual characteristics
   - Creates a robust set of reference points for musical interpretation

4. **Feature Description**
   - Generates unique descriptors for each keypoint
   - Enables consistent feature recognition
   - Facilitates tracking of musical elements across the score

## Application in Sound Technology

This tool bridges the gap between visual scores and sound generation through several key features:

### 1. Static Analysis Mode
- Detects keypoints using SIFT
- Analyzes contrast and object density
- Calculates proximity relationships between elements
- Transmits object count via OSC for sound parameter mapping

### 2. Dynamic Scanning Mode
- Performs real-time left-to-right score scanning
- Analyzes features as the scan progresses
- Provides continuous data streams about:
  - Object count
  - Feature size metrics
  - Spatial relationships
- Enables time-based sound parameter modulation

### 3. OSC Integration
- Transmits data to port 8000
- Sends multiple parameter streams:
  - `/image/object_count`
  - `/image/scan_object_count`
  - `/image/scan_min_size`
  - `/image/scan_avg_size`
  - `/image/scan_max_size`

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python graph_score.py
```

### Controls
- `a` - Static analysis mode
- `b` - Dynamic scanning mode
- `r` - Reverse scanning direction
- `f` - Forward scanning direction
- `n` - Next page
- `p` - Previous page
- `ESC` - Exit

## Musical Applications

The tool can be used in various musical contexts:

1. **Real-time Score Interpretation**
   - Convert visual density to sound intensity
   - Map spatial relationships to sound spatialization
   - Transform feature sizes into frequency ranges

2. **Interactive Performance**
   - Dynamic score scanning for live performance
   - Real-time parameter mapping to synthesizers
   - Automated progression through multi-page scores

3. **Compositional Tool**
   - Analysis of existing graphic scores
   - Generation of parameter data for electronic music
   - Creation of interactive sound installations

## Technical Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- python-osc
- tkinter

## Implementation Details

The program implements SIFT through OpenCV's SIFT detector:

```python
sift = cv2.SIFT_create()
keypoints, descriptors = sift.detectAndCompute(gray, None)
```

Key metrics extracted:
- Keypoint count (object density)
- Feature sizes
- Spatial distribution
- Contrast values
- Proximity relationships

These metrics are then mapped to OSC messages for real-time sound control.

## Future Development

- Additional feature detection algorithms
- Extended parameter mapping options
- Support for real-time video input
- Machine learning integration for pattern recognition
- Enhanced GUI controls for parameter mapping

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Leslie Garcia - 2024

## Acknowledgments

- OpenCV community for SIFT implementation
- OSC protocol developers
- Computer vision researchers and developers 