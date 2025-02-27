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

## OSC Data Structure and Transmission

The program transmits data via OSC (Open Sound Control) protocol on port 8000. Here's a detailed map of the data structure:

### 1. Static Analysis Mode (Press 'a')

```
/image/object_count [int]
└── Total number of detected objects/keypoints in the image
    Range: 0 to n (depends on image complexity)
    Update rate: On analysis completion
    Example: /image/object_count 42
```

### 2. Dynamic Scanning Mode (Press 'b')

```
/image/scan_object_count [int]
├── Number of objects in current scan window
│   Range: 0 to n
│   Update rate: Per scan step
│   Example: /image/scan_object_count 5
│
/image/scan_min_size [float]
├── Minimum size of detected features
│   Range: 0.0 to n.n
│   Update rate: Per scan step
│   Example: /image/scan_min_size 1.2
│
/image/scan_avg_size [float]
├── Average size of detected features
│   Range: 0.0 to n.n
│   Update rate: Per scan step
│   Example: /image/scan_avg_size 3.7
│
/image/scan_max_size [float]
└── Maximum size of detected features
    Range: 0.0 to n.n
    Update rate: Per scan step
    Example: /image/scan_max_size 8.4
```

### Data Characteristics

1. **Transmission Rate**
   - Static Analysis: Once per analysis
   - Dynamic Scanning: Continuous updates based on scan speed
   - Scan speed = score duration / image width

2. **Value Ranges**
   - Object Count: Integer values (0 to ∞)
   - Size Metrics: Float values (typically 0.0 to 20.0)
   - All values are normalized to image dimensions

3. **Timing and Synchronization**
   - Base Port: 8000
   - Protocol: UDP
   - Host: localhost (127.0.0.1)
   - No handshake required

### Example OSC Applications

1. **Sound Synthesis**
   ```
   /image/scan_object_count → Amplitude/Density
   /image/scan_avg_size    → Frequency/Pitch
   /image/scan_max_size    → Filter Cutoff
   /image/scan_min_size    → Modulation Depth
   ```

2. **Spatial Audio**
   ```
   Scan Position → Stereo/Multichannel Panning
   Object Count  → Reverb Amount
   Feature Sizes → Sound Source Width
   ```

3. **Rhythmic Generation**
   ```
   Object Count     → Rhythm Density
   Feature Sizes    → Note Velocity
   Scan Position    → Time Position
   ```

### Integration Examples

```python
# Pure Data / Max/MSP
# OSC receive objects:
[netreceive 8000]
[route /image/scan_object_count /image/scan_avg_size]

# SuperCollider
OSCdef(\imageAnalysis, {|msg, time, addr, recvPort|
    msg[1].postln; // First value of message
}, '/image/scan_object_count');
```

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