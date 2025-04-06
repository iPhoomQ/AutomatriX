import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ImageDownloader:
    def __init__(self):
        self.downloaded_count = 0
        self.failed_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def is_large_image(self, url, min_size_kb=800):
        """Check if image meets size requirements without downloading the whole file"""
        try:
            # Skip known small image hosts
            if any(domain in url for domain in ['thumbnail', 'icon', 'logo', 'small']):
                return False

            # Make HEAD request to check content-length
            response = self.session.head(url, timeout=10, allow_redirects=True)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False

            # Check content length
            content_length = int(response.headers.get('content-length', 0))
            if content_length == 0:
                return True  # Can't verify size, proceed with download

            return (content_length / 1024) >= min_size_kb

        except Exception as e:
            print(f"Size check failed for {url}: {str(e)}")
            return False

    def download_image(self, url, folder_path, min_size_kb=800, retries=2):
        """Download and save an image with retries and size verification"""
        for attempt in range(retries + 1):
            try:
                if not self.is_large_image(url, min_size_kb):
                    return False

                # Create filename from URL
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or len(filename) > 100:
                    filename = f"image_{int(time.time())}_{hash(url)}.jpg"
                else:
                    filename = re.sub(r'[^\w\-_.]', '_', filename)

                filepath = os.path.join(folder_path, filename)

                # Stream download to handle large files
                response = self.session.get(url, stream=True, timeout=30)
                response.raise_for_status()

                # Check actual size during download
                content_length = int(response.headers.get('content-length', 0))
                downloaded = 0
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Early size check
                            if content_length and (downloaded / 1024) < min_size_kb and (content_length / 1024) < min_size_kb:
                                raise ValueError(f"Image too small: {downloaded/1024:.1f}KB")

                # Verify final size
                file_size = os.path.getsize(filepath) / 1024
                if file_size < min_size_kb:
                    os.remove(filepath)
                    raise ValueError(f"Final size too small: {file_size:.1f}KB")

                self.downloaded_count += 1
                print(f"Downloaded [{self.downloaded_count}]: {filename} ({file_size:.1f}KB)")
                return True

            except Exception as e:
                if attempt == retries:
                    self.failed_count += 1
                    print(f"Failed to download {url}: {str(e)}")
                else:
                    time.sleep(1)  # Wait before retry
        return False

    def search_images(self, query, max_images=None, min_size_kb=800):
        """Search for images using multiple search engines"""
        search_urls = [
            f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&qft=+filterui:imagesize-large",
            f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch&tbs=isz:l",
            f"https://search.yahoo.com/search/images?p={query.replace(' ', '+')}&imgc=high"
        ]

        image_urls = set()
        for url in search_urls:
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract image URLs from different search engines
                if 'bing.com' in url:
                    img_tags = soup.find_all('img', {'class': 'mimg'})
                elif 'google.com' in url:
                    img_tags = soup.find_all('img', {'class': 'rg_i'})
                else:  # Yahoo and others
                    img_tags = soup.find_all('img')

                for img in img_tags:
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and img_url.startswith(('http://', 'https://')):
                        # Clean URL and add to set
                        img_url = img_url.split('?')[0].split('#')[0]
                        image_urls.add(img_url)
                        if max_images and len(image_urls) >= max_images * 3:  # Get extras for filtering
                            break

                if max_images and len(image_urls) >= max_images * 3:
                    break

            except Exception as e:
                print(f"Search failed for {url}: {str(e)}")

        return list(image_urls)

    def run(self):
        """Main execution function with user input"""
        print("=== Unlimited Image Downloader ===")
        query = input("Enter search term: ").strip()
        min_size_mb = float(input("Minimum image size in MB (e.g., 0.5, 1, 2): ").strip() or "1")
        min_size_kb = int(min_size_mb * 1024)
        
        max_images = None
        if input("Limit number of downloads? (y/n): ").lower() == 'y':
            max_images = int(input("Maximum images to download: ").strip() or "10")

        output_folder = os.path.join("downloaded_images", re.sub(r'[^\w\-_]', '_', query))
        os.makedirs(output_folder, exist_ok=True)

        print(f"\nSearching for '{query}' (min size: {min_size_mb}MB)...")
        image_urls = self.search_images(query, max_images, min_size_kb)
        print(f"Found {len(image_urls)} potential images to download")

        # Parallel downloading with progress
        with ThreadPoolExecutor(max_workers=5) as executor:
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

            for future in as_completed(futures):
                if max_images and self.downloaded_count >= max_images:
                    for f in futures:
                        f.cancel()
                    break

        print(f"\nDownload complete! Results:")
        print(f"- Successfully downloaded: {self.downloaded_count}")
        print(f"- Failed downloads: {self.failed_count}")
        print(f"- Images saved to: {os.path.abspath(output_folder)}")

if __name__ == "__main__":
    downloader = ImageDownloader()
    downloader.run()
