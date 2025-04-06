import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

class ImprovedImageDownloader:
    def __init__(self):
        self.downloaded_count = 0
        self.failed_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.search_engines = [
            {'name': 'DuckDuckGo', 'url': 'https://duckduckgo.com/?q={}&iax=images&ia=images'},
            {'name': 'Bing', 'url': 'https://www.bing.com/images/search?q={}&qft=+filterui:imagesize-large'},
            {'name': 'Yahoo', 'url': 'https://images.search.yahoo.com/search/images?p={}&imgc=high'}
        ]

    def get_random_delay(self):
        """Return random delay between requests to avoid being blocked"""
        return random.uniform(1.0, 3.0)

    def clean_url(self, url):
        """Clean and normalize image URLs"""
        if not url:
            return None
        
        # Remove tracking parameters
        url = url.split('?')[0].split('#')[0]
        
        # Fix common URL issues
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            url = 'https://' + urlparse(url).netloc + url if urlparse(url).netloc else None
            
        return url if url and url.startswith('http') else None

    def extract_direct_image_urls(self, html):
        """Extract direct image URLs from HTML using multiple methods"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = set()
        
        # Common image tag patterns
        for img in soup.find_all('img'):
            for attr in ['src', 'data-src', 'data-original', 'data-url']:
                url = self.clean_url(img.get(attr))
                if url:
                    urls.add(url)
        
        # OpenGraph and Twitter meta tags
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['og:image', 'twitter:image']:
                url = self.clean_url(meta.get('content'))
                if url:
                    urls.add(url)
        
        return list(urls)

    def download_image(self, url, folder_path, min_size_kb=500, timeout=30):
        """Download and save an image with size verification"""
        try:
            # Skip obviously small images
            if any(x in url.lower() for x in ['thumbnail', 'icon', 'logo', 'small', 'thumb']):
                return False
                
            # Start download
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False
                
            # Check size during download
            content_length = int(response.headers.get('content-length', 0))
            if content_length > 0 and (content_length / 1024) < min_size_kb:
                return False
                
            # Create filename
            filename = os.path.basename(urlparse(url).path)
            if not filename or len(filename) > 100:
                filename = f"image_{int(time.time())}_{hash(url)}.jpg"
            filename = re.sub(r'[^\w\-_.]', '_', filename)
            filepath = os.path.join(folder_path, filename)
            
            # Download with size tracking
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Early size check
                        if downloaded < min_size_kb * 1024 * 0.1:  # Check after 10% downloaded
                            actual_size = downloaded / 1024
                            expected_size = content_length / 1024 if content_length else 0
                            if expected_size and expected_size < min_size_kb:
                                raise ValueError(f"Image too small: {expected_size:.1f}KB")
                            if downloaded > 1024 * 1024 and actual_size < min_size_kb * 0.5:
                                raise ValueError(f"Image likely too small: {actual_size:.1f}KB")
            
            # Verify final size
            file_size = os.path.getsize(filepath) / 1024
            if file_size < min_size_kb:
                os.remove(filepath)
                return False
                
            self.downloaded_count += 1
            print(f"Downloaded [{self.downloaded_count}]: {filename} ({file_size:.1f}KB)")
            return True
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False

    def search_images(self, query, max_images=None):
        """Search for images using multiple search engines"""
        image_urls = set()
        
        for engine in self.search_engines:
            try:
                time.sleep(self.get_random_delay())
                
                search_url = engine['url'].format(query.replace(' ', '+'))
                print(f"Searching {engine['name']}...")
                
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                # Extract image URLs
                urls = self.extract_direct_image_urls(response.text)
                for url in urls:
                    if url not in image_urls:
                        image_urls.add(url)
                        if max_images and len(image_urls) >= max_images * 2:  # Get extras
                            break
                
                if max_images and len(image_urls) >= max_images * 2:
                    break
                    
            except Exception as e:
                print(f"Search failed on {engine['name']}: {str(e)}")
                continue
                
        return list(image_urls)

    def run(self):
        """Main execution function"""
        print("=== Improved Image Downloader ===")
        query = input("Enter search term: ").strip()
        min_size_mb = float(input("Minimum image size in MB (e.g., 0.5, 1, 2): ").strip() or "0.5")
        min_size_kb = int(min_size_mb * 1024)
        
        max_images = None
        if input("Limit number of downloads? (y/n): ").lower() == 'y':
            max_images = int(input("Maximum images to download: ").strip() or "10")

        output_folder = os.path.join("downloaded_images", re.sub(r'[^\w\-_]', '_', query))
        os.makedirs(output_folder, exist_ok=True)

        print(f"\nSearching for '{query}' (min size: {min_size_mb}MB)...")
        image_urls = self.search_images(query, max_images)
        print(f"Found {len(image_urls)} potential images to download")

        # Download with progress
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for url in image_urls:
                if max_images and self.downloaded_count >= max_images:
                    break
                    
                futures.append(executor.submit(
                    self.download_image,
                    url,
                    output_folder,
                    min_size_kb
                ))
                time.sleep(self.get_random_delay() / 2)  # Space out requests

            for future in as_completed(futures):
                if max_images and self.downloaded_count >= max_images:
                    for f in futures:
                        f.cancel()
                    break

        print(f"\nDownload complete! Results:")
        print(f"- Successfully downloaded: {self.downloaded_count}")
        print(f"- Failed downloads: {len(image_urls) - self.downloaded_count}")
        print(f"- Images saved to: {os.path.abspath(output_folder)}")

if __name__ == "__main__":
    downloader = ImprovedImageDownloader()
    downloader.run()
