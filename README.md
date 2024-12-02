# iOS Video Codec Converter

A Python GUI application that helps convert video files to make them compatible with iOS devices. This tool automatically scans directories for MP4 files and converts them to use H.264 video codec and AAC audio codec, ensuring compatibility with iOS devices.

## Features

- User-friendly graphical interface
- Recursive directory scanning
- Automatic codec compatibility checking
- Real-time conversion progress display
- Batch processing capability
- Compatible with Windows, macOS, and Linux

## Prerequisites

Before running the application, make sure you have the following installed:

- Python 3.6 or higher
- FFmpeg (must be accessible from command line)
- Required Python packages:
  ```bash
  pip install tkinter
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ios-video-codec-converter.git
   cd ios-video-codec-converter
   ```

2. Install FFmpeg:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

## Usage

1. Run the application:
   ```bash
   python repair_mp4_codec.py
   ```

2. Click "Browse" to select the root directory containing your video files
3. Click "Start Conversion" to begin the process
4. Monitor progress in the text area

## How It Works

- The application scans the selected directory and all subdirectories for MP4 files
- Each file is checked for codec compatibility:
  - Video codec must be H.264
  - Audio codec must be AAC or MP3
- Incompatible files are automatically converted using FFmpeg
- Original files are preserved, and converted files are saved with "_converted" suffix

## Technical Details

- Built with Python's tkinter library for GUI
- Uses FFmpeg for video conversion
- Uses FFprobe for codec detection
- Runs conversions in separate threads to maintain GUI responsiveness
- Includes real-time console output redirection to GUI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FFmpeg team for their excellent video processing tools
- Python tkinter library for GUI capabilities

## Support

If you encounter any problems or have any suggestions, please open an issue on GitHub. 