import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import time
import random

def download_image(url, folder_path, filename=None):
    """
    Download an image from a given URL and save it to the specified folder.
    """
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        # Get the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Determine filename
        if not filename:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"image_{int(time.time())}_{random.randint(1000,9999)}.jpg"
        
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

def get_google_images(search_term, num_images=200, start=0):
    """
    Fetch image URLs from Google Images search
    """
    url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}&tbm=isch&start={start}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        # Extract image URLs
        img_urls = []
        for img in img_tags[1:]:  # Skip the first logo image
            img_url = img.get('src') or img.get('data-src')
            if img_url and (img_url.startswith('http://') or img_url.startswith('https://')):
                img_urls.append(img_url)
        
        return img_urls
        
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

def search_and_download_images(search_term, num_images=2000, output_folder='downloaded_images'):
    """
    Search for images using a search term and download them.
    """
    if num_images > 2000:
        num_images = 2000
        print("Maximum number of images limited to 2000")
    
    # Create output folder with search term
    output_folder = os.path.join(output_folder, search_term.replace(' ', '_'))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    try:
        all_img_urls = []
        start = 0
        batch_size = 20  # Google shows about 20 images per page
        
        # Fetch image URLs in batches
        while len(all_img_urls) < num_images:
            img_urls = get_google_images(search_term, batch_size, start)
            if not img_urls:
                break
                
            all_img_urls.extend(img_urls)
            start += batch_size
            
            # Avoid hitting Google too frequently
            time.sleep(random.uniform(1.0, 3.0))
        
        # Limit to requested number of images
        all_img_urls = all_img_urls[:num_images]
        
        # Download images using threads for better performance
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i, url in enumerate(all_img_urls):
                executor.submit(
                    download_image, 
                    url, 
                    output_folder, 
                    f"{search_term.replace(' ', '_')}_{i+1}.jpg"
                )
                # Small delay between downloads to avoid being blocked
                time.sleep(random.uniform(0.1, 0.5))
                
        print(f"\nDownloaded {len(all_img_urls)} images for '{search_term}' to '{output_folder}'")
        
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    # Example usage
    search_term = input("Enter search term: ").strip()
    if not search_term:
        print("Search term cannot be empty")
        exit()
    
    try:
        num_images = int(input("How many images to download? (1-2000): ").strip() or 100)
        num_images = max(1, min(num_images, 2000))  # Ensure between 1-2000
    except ValueError:
        print("Invalid number, defaulting to 100")
        num_images = 100
    
    search_and_download_images(
        search_term=search_term,
        num_images=num_images,
        output_folder="downloads"
    )
