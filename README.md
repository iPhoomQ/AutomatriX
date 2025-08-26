# AutomatriX

**Professional automation tools for business activities**

AutomatriX is a comprehensive Python toolkit designed to streamline various business automation tasks including video processing, YouTube content management, and image collection. Built with professional-grade architecture, it offers both command-line interface and programmatic API access.

## 🚀 Features

### Video Processing
- **Professional Watermarking**: Add customizable text watermarks to videos
- **Batch Processing**: Process multiple videos simultaneously
- **Audio Control**: Adjust volume levels during processing
- **Configurable Output**: Control codecs, quality, and positioning

### YouTube Content Management
- **Smart Downloads**: Download videos with quality selection and filtering
- **Search Integration**: Search and download videos based on queries
- **Duration Filtering**: Filter content by maximum duration
- **Audio Extraction**: Extract audio-only content
- **Batch Operations**: Handle multiple downloads efficiently

### Image Collection
- **Multi-Engine Search**: Search across multiple image search engines
- **Quality Filtering**: Filter by minimum file size and image quality
- **Concurrent Downloads**: Download multiple images simultaneously
- **Intelligent Validation**: Verify image integrity and format

### Professional Features
- **Centralized Configuration**: INI-based configuration management
- **Advanced Logging**: Comprehensive logging with file and console output
- **Error Handling**: Robust error handling with meaningful messages
- **Type Safety**: Full type hints for better code reliability
- **Modular Architecture**: Clean, extensible codebase structure

## 📦 Installation

### From Source
```bash
git clone https://github.com/iPhoomQ/AutomatriX.git
cd AutomatriX
pip install -e .
```

### Dependencies
```bash
pip install -r requirements.txt
```

## 🛠️ Quick Start

### Command Line Interface

#### Video Watermarking
```bash
# Single video
automatrix video-watermark input.mp4 output.mp4 --text "My Company"

# Batch processing
automatrix video-watermark input_folder output_folder --text "Watermark" --batch
```

#### YouTube Downloads
```bash
# Single video
automatrix youtube-download --url "https://youtube.com/watch?v=..."

# Search and download
automatrix youtube-download --search "tutorial python" --count 5 --max-duration 10m
```

#### Image Downloads
```bash
# Download images
automatrix image-download "nature photography" --count 20 --min-size 1.0
```

### Python API

```python
from automatrix import config
from automatrix.video.processor import VideoProcessor
from automatrix.youtube.downloader import YouTubeDownloader
from automatrix.image.downloader import ImageDownloader

# Video processing
processor = VideoProcessor(config)
result = processor.add_text_watermark(
    input_path="input.mp4",
    output_path="output.mp4",
    text="Professional Watermark"
)

# YouTube downloading
downloader = YouTubeDownloader(config)
result = downloader.search_and_download(
    query="business automation",
    num_videos=5,
    max_duration="10m"
)

# Image downloading
image_downloader = ImageDownloader(config)
result = image_downloader.download_images(
    query="business graphics",
    max_images=10,
    min_size_mb=1.0
)
```

## ⚙️ Configuration

AutomatriX uses a centralized configuration system. Create a `config.ini` file:

```ini
[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
file_enabled = true
console_enabled = true

[video_processing]
default_font = Arial-Bold
default_fontsize = 50
default_text_color = white
default_stroke_color = black
default_stroke_width = 2

[youtube_download]
default_quality = best
max_videos_per_search = 100
default_output_directory = ./downloads

[image_download]
default_min_size_mb = 0.5
max_concurrent_downloads = 4
default_output_directory = ./downloaded_images
```

## 📁 Project Structure

```
AutomatriX/
├── automatrix/              # Main package
│   ├── core/                # Core utilities
│   │   ├── config.py        # Configuration management
│   │   ├── logger.py        # Logging system
│   │   └── utils.py         # Utility functions
│   ├── video/               # Video processing
│   │   └── processor.py     # Video processor class
│   ├── youtube/             # YouTube functionality
│   │   └── downloader.py    # YouTube downloader
│   ├── image/               # Image downloading
│   │   └── downloader.py    # Image downloader
│   └── cli.py               # Command-line interface
├── config.ini               # Configuration file
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## 🔧 Advanced Usage

### Custom Configuration
```python
from automatrix.core.config import Config

# Load custom config
config = Config('my_config.ini')

# Modify settings programmatically
config.set('video_processing', 'default_fontsize', '60')
config.save()
```

### Progress Callbacks
```python
def progress_callback(info):
    print(f"Status: {info['status']}")
    if info['status'] == 'downloading':
        print(f"Progress: {info['percent']}")

downloader = YouTubeDownloader(config, progress_callback)
```

### Error Handling
```python
from automatrix.core.utils import ValidationError, DownloadError

try:
    result = downloader.download_single_video(url)
except ValidationError as e:
    print(f"Invalid input: {e}")
except DownloadError as e:
    print(f"Download failed: {e}")
```

## 📋 Requirements

- Python 3.8+
- moviepy >= 1.0.3
- yt-dlp >= 2023.1.6
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- Pillow >= 9.0.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/iPhoomQ/AutomatriX/wiki)
- **Issues**: [GitHub Issues](https://github.com/iPhoomQ/AutomatriX/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iPhoomQ/AutomatriX/discussions)

## 🎯 Roadmap

- [ ] GUI Interface with tkinter
- [ ] Web API with FastAPI
- [ ] Docker containerization
- [ ] Cloud storage integration
- [ ] Batch job scheduling
- [ ] Plugin system
- [ ] Machine learning features

## 📊 Performance

AutomatriX is designed for performance:
- **Concurrent Processing**: Multi-threaded downloads and processing
- **Memory Efficient**: Streaming downloads and processing
- **Configurable**: Adjust performance parameters via configuration
- **Progress Tracking**: Real-time progress reporting

---

**Made with ❤️ by the AutomatriX Team**
