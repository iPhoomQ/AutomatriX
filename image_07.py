import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from concurrent.futures import ThreadPoolExecutor
import time
import random
import re

def download_image(url, folder_path, filename=None, width=None, height=None):
    """
    Download an image from a given URL and save it to the specified folder.
    Optionally specify desired width and height (will try to find closest match).
    """
    try:
        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        # Get the image with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        # Modify URL to get higher resolution when possible
        if 'google.com' in url and ('=http' in url or 'imgurl=' in url):
            # Extract the actual image URL from Google's redirect
            url_match = re.search(r'imgurl=(.*?)(?:&|$)', url)
            if url_match:
                url = unquote(url_match.group(1))
        
        # If dimensions are specified, try to get exact size from Google
        if width or height:
            if 'google.com' not in url:
                # For non-Google URLs, try to modify URL if it supports size parameters
                if 'flickr.com' in url:
                    url = url.replace('_m.jpg', '_b.jpg')  # Flickr large size
                elif 'unsplash.com' in url:
                    url += f"?fit=crop&w={width}&h={height}" if width and height else ""
            else:
                # For Google URLs, we'll handle size filtering during search
                pass
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Determine filename with extension
        if not filename:
            filename = os.path.basename(urlparse(url).path)
            if not filename or len(filename) > 50:  # If too long or empty
                filename = f"image_{int(time.time())}_{random.randint(1000,9999)}.jpg"
            elif '.' not in filename[-5:]:  # If no extension
                filename += '.jpg'
        
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

def get_google_images(search_term, num_images=100, start=0, width=None, height=None):
    """
    Fetch image URLs from Google Images search with size filters
    """
    # Build size parameters
    size_param = ""
    if width and height:
        size_param = f"tbs=isz:ex,iszw:{width},iszh:{height}"
    elif width:
        size_param = f"tbs=isz:ex,iszw:{width}"
    elif height:
        size_param = f"tbs=isz:ex,iszh:{height}"
    else:
        size_param = "tbs=isz:l"  # Default to large if no size specified
    
    url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}&tbm=isch&{size_param}&start={start}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        img_elements = soup.find_all('div', {'class': 'isv-r'})  # Higher resolution container
        
        # Extract image URLs
        img_urls = []
        for img_div in img_elements[:num_images]:
            try:
                # Extract the JSON data containing high-res URL
                script = img_div.find('script').text
                url_match = re.search(r'var _ujd=\'(.*?)\';', script)
                if url_match:
                    img_url = url_match.group(1)
                    if img_url.startswith('http'):
                        img_urls.append(img_url)
            except:
                continue
        
        # Fallback to regular image extraction if no high-res found
        if not img_urls:
            img_tags = soup.find_all('img')
            for img in img_tags[1:]:  # Skip the first logo image
                img_url = img.get('data-src') or img.get('src')
                if img_url and (img_url.startswith('http://') or img_url.startswith('https://')):
                    img_urls.append(img_url)
        
        return img_urls[:num_images]
        
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

def search_and_download_images(search_term, num_images=200, output_folder='downloaded_images', width=None, height=None):
    """
    Search for images with specific dimensions and download them.
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
        batch_size = 100  # Number of images to fetch per batch
        
        # Fetch image URLs in batches
        while len(all_img_urls) < num_images:
            img_urls = get_google_images(search_term, batch_size, start, width, height)
            if not img_urls:
                break
                
            all_img_urls.extend(img_urls)
            start += batch_size
            
            # Avoid hitting Google too frequently
            time.sleep(random.uniform(2.0, 5.0))
            print(f"Fetched {len(all_img_urls)} image URLs so far...")
        
        # Limit to requested number of images
        all_img_urls = list(set(all_img_urls))[:num_images]  # Remove duplicates
        
        # Download images using threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i, url in enumerate(all_img_urls):
                executor.submit(
                    download_image, 
                    url, 
                    output_folder, 
                    f"{search_term.replace(' ', '_')}_{i+1}.jpg",
                    width,
                    height
                )
                # Small delay between downloads to avoid being blocked
                time.sleep(random.uniform(0.5, 1.5))
                
        print(f"\nDownloaded {len(all_img_urls)} images for '{search_term}' to '{output_folder}'")
        if width or height:
            print(f"Requested dimensions: {f'width={width}' if width else ''}{' ' if width and height else ''}{f'height={height}' if height else ''}")
        
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
    
    width = None
    height = None
    try:
        width_input = input("Desired width in pixels (leave empty for any): ").strip()
        if width_input:
            width = int(width_input)
        
        height_input = input("Desired height in pixels (leave empty for any): ").strip()
        if height_input:
            height = int(height_input)
    except ValueError:
        print("Invalid dimensions, using default size")
    
    search_and_download_images(
        search_term=search_term,
        num_images=num_images,
        output_folder="downloads",
        width=width,
        height=height
    )
