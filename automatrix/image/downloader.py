"""
Professional image downloader module for AutomatriX
"""

import os
import re
import requests
import logging
import time
import random
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("beautifulsoup4 is required for image downloads. Install with: pip install beautifulsoup4")

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow is required for image processing. Install with: pip install Pillow")

from ..core.config import Config
from ..core.utils import (
    DownloadError,
    ValidationError,
    validate_file_path,
    sanitize_filename,
    format_file_size
)


class ImageDownloader:
    """Professional image downloader with multiple search engines"""
    
    def __init__(self, config: Optional[Config] = None, progress_callback: Optional[Callable] = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        self.progress_callback = progress_callback
        
        # Load configuration
        self.default_min_size_mb = self.config.getfloat('image_download', 'default_min_size_mb', 0.5)
        self.max_concurrent = self.config.getint('image_download', 'max_concurrent_downloads', 4)
        self.default_output_dir = self.config.get('image_download', 'default_output_directory', './downloaded_images')
        self.delay_min = self.config.getfloat('image_download', 'request_delay_min', 1.0)
        self.delay_max = self.config.getfloat('image_download', 'request_delay_max', 3.0)
        
        # Initialize counters
        self.downloaded_count = 0
        self.failed_count = 0
        
        # Setup HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Search engine configurations
        self.search_engines = [
            {
                'name': 'DuckDuckGo',
                'url': 'https://duckduckgo.com/?q={}&iax=images&ia=images',
                'image_selector': 'img[src*="http"]'
            },
            {
                'name': 'Bing',
                'url': 'https://www.bing.com/images/search?q={}&qft=+filterui:imagesize-large',
                'image_selector': 'img[src*="http"]'
            }
        ]
    
    def get_random_delay(self) -> float:
        """Get random delay between requests to avoid being blocked"""
        return random.uniform(self.delay_min, self.delay_max)
    
    def clean_url(self, url: str) -> Optional[str]:
        """Clean and normalize image URLs"""
        if not url:
            return None
        
        # Remove tracking parameters
        url = url.split('?')[0].split('#')[0]
        
        # Fix common URL issues
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            parsed = urlparse(url)
            if parsed.netloc:
                url = 'https://' + parsed.netloc + url
            else:
                return None
        
        return url if url and url.startswith('http') else None
    
    def extract_direct_image_urls(self, html: str, base_url: str = '') -> List[str]:
        """Extract direct image URLs from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = set()
        
        # Find all img tags
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src:
                # Convert relative URLs to absolute
                if base_url and not src.startswith('http'):
                    src = urljoin(base_url, src)
                
                cleaned_url = self.clean_url(src)
                if cleaned_url and self._is_valid_image_url(cleaned_url):
                    urls.add(cleaned_url)
        
        # Find data attributes that might contain image URLs
        for element in soup.find_all(attrs={'data-src': True}):
            data_src = element.get('data-src')
            if data_src:
                if base_url and not data_src.startswith('http'):
                    data_src = urljoin(base_url, data_src)
                
                cleaned_url = self.clean_url(data_src)
                if cleaned_url and self._is_valid_image_url(cleaned_url):
                    urls.add(cleaned_url)
        
        return list(urls)
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL appears to be a valid image URL"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check file extension
        for ext in image_extensions:
            if path.endswith(ext):
                return True
        
        # Check for image-related keywords in URL
        image_keywords = ['image', 'img', 'photo', 'picture', 'pic']
        url_lower = url.lower()
        
        return any(keyword in url_lower for keyword in image_keywords)
    
    def download_single_image(
        self,
        url: str,
        folder_path: str,
        min_size_kb: int = 500,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Download and save a single image with size verification.
        
        Args:
            url: Image URL to download
            folder_path: Directory to save the image
            min_size_kb: Minimum file size in KB
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with download result
        """
        try:
            # Make request with timeout
            response = self.session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                return {
                    'success': False,
                    'url': url,
                    'error': f'Invalid content type: {content_type}'
                }
            
            # Get file extension from content type or URL
            ext_map = {
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/webp': '.webp',
                'image/tiff': '.tiff'
            }
            
            extension = ext_map.get(content_type, '.jpg')
            
            # Generate filename
            filename = f"image_{int(time.time())}_{random.randint(1000, 9999)}{extension}"
            filepath = os.path.join(folder_path, filename)
            
            # Download and save
            total_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            # Check file size
            if total_size < min_size_kb * 1024:
                os.remove(filepath)
                return {
                    'success': False,
                    'url': url,
                    'error': f'File too small: {format_file_size(total_size)} < {min_size_kb}KB'
                }
            
            # Verify image integrity
            try:
                with Image.open(filepath) as img:
                    img.verify()
            except Exception:
                os.remove(filepath)
                return {
                    'success': False,
                    'url': url,
                    'error': 'Invalid or corrupted image'
                }
            
            # Success
            self.downloaded_count += 1
            result = {
                'success': True,
                'url': url,
                'filepath': filepath,
                'filename': filename,
                'file_size': total_size,
                'file_size_formatted': format_file_size(total_size)
            }
            
            self.logger.debug(f"Downloaded image: {filename} ({format_file_size(total_size)})")
            
            if self.progress_callback:
                self.progress_callback({
                    'status': 'downloaded',
                    'filename': filename,
                    'file_size': total_size,
                    'total_downloaded': self.downloaded_count
                })
            
            return result
            
        except Exception as e:
            self.failed_count += 1
            error_msg = f"Failed to download {url}: {str(e)}"
            self.logger.warning(error_msg)
            
            if self.progress_callback:
                self.progress_callback({
                    'status': 'failed',
                    'url': url,
                    'error': str(e),
                    'total_failed': self.failed_count
                })
            
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    def search_images(self, query: str, max_images: Optional[int] = None) -> List[str]:
        """
        Search for images using multiple search engines.
        
        Args:
            query: Search query
            max_images: Maximum number of image URLs to return
            
        Returns:
            List of image URLs
        """
        self.logger.info(f"Searching for images: '{query}'")
        
        all_urls = set()
        
        for engine in self.search_engines:
            try:
                self.logger.debug(f"Searching on {engine['name']}")
                
                # Format search URL
                search_url = engine['url'].format(query.replace(' ', '+'))
                
                # Make request
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                # Extract image URLs
                urls = self.extract_direct_image_urls(response.text, search_url)
                all_urls.update(urls)
                
                self.logger.debug(f"Found {len(urls)} URLs from {engine['name']}")
                
                # Add delay between search engines
                time.sleep(self.get_random_delay())
                
                # Stop if we have enough URLs
                if max_images and len(all_urls) >= max_images:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Failed to search on {engine['name']}: {e}")
                continue
        
        image_urls = list(all_urls)
        if max_images:
            image_urls = image_urls[:max_images]
        
        self.logger.info(f"Found {len(image_urls)} total image URLs")
        return image_urls
    
    def download_images(
        self,
        query: str,
        max_images: int = 10,
        min_size_mb: Optional[float] = None,
        output_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search and download images.
        
        Args:
            query: Search query
            max_images: Maximum number of images to download
            min_size_mb: Minimum image size in MB
            output_directory: Directory to save images
            
        Returns:
            Dictionary with download results
        """
        self.logger.info(f"Starting image download: '{query}' (max: {max_images})")
        
        # Validate inputs
        if not query:
            raise ValidationError("Search query cannot be empty")
        
        if max_images < 1:
            raise ValidationError("Maximum images must be at least 1")
        
        min_size_mb = min_size_mb or self.default_min_size_mb
        min_size_kb = int(min_size_mb * 1024)
        
        # Setup output directory
        output_directory = output_directory or self.default_output_dir
        folder_name = sanitize_filename(query.replace(' ', '_'))
        output_folder = os.path.join(output_directory, folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # Reset counters
        self.downloaded_count = 0
        self.failed_count = 0
        
        try:
            # Search for images
            image_urls = self.search_images(query, max_images * 3)  # Get more URLs than needed
            
            if not image_urls:
                return {
                    'success': False,
                    'query': query,
                    'error': 'No image URLs found'
                }
            
            # Download images concurrently
            results = {
                'query': query,
                'requested_images': max_images,
                'found_urls': len(image_urls),
                'downloaded': [],
                'failed': [],
                'total_downloaded': 0,
                'output_folder': output_folder
            }
            
            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                # Submit download tasks
                futures = []
                for url in image_urls[:max_images * 2]:  # Try more than requested
                    if self.downloaded_count >= max_images:
                        break
                    
                    future = executor.submit(
                        self.download_single_image,
                        url,
                        output_folder,
                        min_size_kb
                    )
                    futures.append(future)
                    
                    # Add delay between requests
                    time.sleep(self.get_random_delay() / 4)
                
                # Collect results
                for future in as_completed(futures):
                    if self.downloaded_count >= max_images:
                        # Cancel remaining tasks
                        for f in futures:
                            f.cancel()
                        break
                    
                    try:
                        result = future.result()
                        if result['success']:
                            results['downloaded'].append(result)
                        else:
                            results['failed'].append(result)
                    except Exception as e:
                        self.logger.error(f"Task failed: {e}")
            
            results['total_downloaded'] = self.downloaded_count
            results['total_failed'] = self.failed_count
            
            self.logger.info(
                f"Download complete: {self.downloaded_count} downloaded, "
                f"{self.failed_count} failed"
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to download images for '{query}': {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e