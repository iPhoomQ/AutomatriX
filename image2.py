import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

def is_large_image(url, min_size_kb=800):
    """
    Check if image is likely to be large by examining URL patterns and making HEAD request
    """
    try:
        # Check URL for common large image patterns
        large_keywords = ['large', 'original', 'highres', 'hd', 'full', 'max']
        if any(kw in url.lower() for kw in large_keywords):
            return True
        
        # Check file extension
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in ('.webp', '.bmp'):
            return False  # These are often smaller
            
        # Make HEAD request to check content-length
        response = requests.head(url, timeout=5, allow_redirects=True)
        if 'content-length' in response.headers:
            size_kb = int(response.headers['content-length']) / 1024
            return size_kb >= min_size_kb
            
        return True  # Assume large if we can't verify
    except:
        return False  # If we can't check, assume not large

def download_large_image(url, folder_path, filename=None, min_size_kb=800):
    """
    Download an image only if it meets minimum size requirements
    """
    try:
        if not is_large_image(url, min_size_kb):
            print(f"Skipping small image: {url}")
            return None
            
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        # Get the image with stream
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        
        # Verify actual downloaded size
        content_length = int(response.headers.get('content-length', 0))
        if content_length and (content_length / 1024) < min_size_kb:
            print(f"Image too small: {url} ({content_length/1024:.1f}KB)")
            return None
            
        # Determine filename
        if not filename:
            filename = os.path.basename(urlparse(url).path)
            if not filename or len(filename) > 100:
                filename = f"image_{hash(url)}.jpg"
            else:
                # Clean filename
                filename = re.sub(r'[^\w\-_.]', '_', filename)
        
        filepath = os.path.join(folder_path, filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        
        # Verify final file size
        file_size = os.path.getsize(filepath) / 1024
        if file_size < min_size_kb:
            os.remove(filepath)
            print(f"Deleted small file: {filename} ({file_size:.1f}KB)")
            return None
            
        print(f"Downloaded: {filename} ({file_size:.1f}KB)")
        return filepath
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def search_large_images(search_term, num_images=5, output_folder='large_images', min_size_kb=800):
    """
    Search for large images using search term with specialized queries
    """
    try:
        # Create specialized search queries more likely to return large images
        queries = [
            f"{search_term} high resolution",
            f"{search_term} large size",
            f"{search_term} original size",
            f"{search_term} HD",
            f"{search_term} wallpaper"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        img_urls = set()
        
        for query in queries[:2]:  # Try first two queries
            search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}&qft=+filterui:imagesize-large"
            
            try:
                response = requests.get(search_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                img_tags = soup.find_all('img', {'class': 'mimg'})
                
                for img in img_tags:
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and img_url.startswith(('http://', 'https://')):
                        # Convert thumbnail URL to full-size URL if possible
                        if 'th?id=' in img_url:
                            img_url = img_url.split('?')[0]  # Try to get original
                        img_urls.add(img_url)
                        if len(img_urls) >= num_images * 2:  # Get extra for filtering
                            break
                
            except Exception as e:
                print(f"Search query '{query}' failed: {e}")
                continue
                
        # Download images using threads
        with ThreadPoolExecutor(max_workers=3) as executor:
            for i, url in enumerate(list(img_urls)[:num_images*2]):
                executor.submit(
                    download_large_image, 
                    url, 
                    output_folder, 
                    f"{search_term}_{i+1}.jpg", 
                    min_size_kb
                )
                
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    search_term = input("Enter search term: ").strip()
    num_images = min(max(int(input("How many images to download? (1-10): ").strip() or 5), 10)
    min_size = int(input("Minimum image size in KB (e.g., 800 for ~1MB): ").strip() or 800)
    
    search_large_images(
        search_term=search_term,
        num_images=num_images,
        output_folder=f"large_images/{search_term}",
        min_size_kb=min_size
    )
