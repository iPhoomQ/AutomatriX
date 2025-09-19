"""
image_to_streetview_coordinate.py

Match a local image to Google Street View and identify its coordinates using Google Cloud Vision and Google Maps APIs.
"""

import os
from google.cloud import vision
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Step 1: Use Google Cloud Vision to extract landmarks from the image
def detect_landmark(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    if not landmarks:
        print("No landmark detected.")
        return None
    # Use the first detected landmark
    landmark = landmarks[0]
    print(f"Detected landmark: {landmark.description}")
    lat_lng = landmark.locations[0].lat_lng
    print(f"Coordinates: {lat_lng.latitude}, {lat_lng.longitude}")
    return lat_lng.latitude, lat_lng.longitude

# Step 2: Use Google Maps Street View API to get the closest street view image
def get_streetview_image(lat, lng, output_path="streetview.jpg"):
    url = (
        f"https://maps.googleapis.com/maps/api/streetview?size=600x400"
        f"&location={lat},{lng}&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Street View image saved to {output_path}")
    else:
        print("Failed to fetch Street View image.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Match image to Google Street View and get coordinates.")
    parser.add_argument("--image", required=True, help="Path to the local image file")
    args = parser.parse_args()

    coords = detect_landmark(args.image)
    if coords:
        get_streetview_image(*coords)
