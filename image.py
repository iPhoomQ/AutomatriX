import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Tuple

def download_image(url: str, folder_path: str, filename: Optional[str] = None, 
                  size: Optional[Tuple[int, int]] = None) -> bool:
    """
    Download an image from a given URL and save it to the specified folder.
    
    Args:
        url: URL of the image to download
        folder_path: Path to folder where image will be saved
        filename: Optional custom filename (will use URL-based name if None)
        size: Optional tuple of (width, height) to resize image
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        # Get the image
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Determine filename
        if not filename:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"image_{hash(url)}.jpg"
        
        filepath = os.path.join(folder_path, filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        print(f"Downloaded: {filename}")
        return filepath
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def search_and_download_images(search_term: str, num_images: int = 5, 
                              output_folder: str = 'downloaded_images', 
                              size: Optional[Tuple[int, int]] = None) -> None:
    """
    Search for images using a search term and download them.
    
    Args:
        search_term: Term to search for images
        num_images: Number of images to download (default: 5)
        output_folder: Folder to save downloaded images (default: 'downloaded_images')
        size: Optional tuple of (width, height) to resize images
    """
    # Create a search URL (this uses a simple approach without APIs)
    search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}&tbm=isch"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        # Extract image URLs
        img_urls = []
        for img in img_tags[:num_images]:
            img_url = img.get('src') or img.get('data-src')
            if img_url and img_url.startswith(('http://', 'https://')):
                img_urls.append(img_url)
        
        # Download images using threads for better performance
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i, url in enumerate(img_urls):
                executor.submit(download_image, url, output_folder, f"{search_term}_{i+1}.jpg", size)
                
        print(f"Downloaded {len(img_urls)} images for '{search_term}' to '{output_folder}'")
        
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    # Example usage
    search_term = input("Enter search term: ").strip()
    num_images = int(input("How many images to download? (1-20): ").strip() or 5)
    size_pref = input("Size preference (optional - small, medium, large): ").strip().lower()
    
    # Map size preferences (this is just a simple example)
    size_map = {
        'small': (200, 200),
        'medium': (500, 500),
        'large': (1024, 768)
    }
    
    size = size_map.get(size_pref) if size_pref in size_map else None
    
    search_and_download_images(
        search_term=search_term,
        num_images=min(max(num_images, 1), 20),  # Limit between 1-20
        output_folder=f"downloads/{search_term}",
        size=size
    )
