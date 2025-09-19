import requests
import time
import os
import random
from datetime import datetime
import openai
from dotenv import load_dotenv
import threading

PAGE_ID = "658931300641799"
PAGE_TOKEN = "EAAaDbVWWipQBPVsQMRujHnJtZAQxZC6KnqlAAMXprA5oS3Gf6Q159H5hxyweSNNm7SmjMVRIIA8zXazSGp5unFmmaSLQQSu8uTiUGN4Wx7HqHaqVnkmt51KZBTjlTBPhay0ZASkZCWa17Kt2wOTVgEV6mkiqYZABRkGIkjB5oRNPS77pwRg5WwLYSpftV76p8myWX2SV94UFHwx7daAhHs7re5caQQv7ZB8xaqKuIAkhXIZD"  # Updated Page token

url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/photos"

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Fetch API key from .env file

# Function to get a random image from the Downloads folder
def get_random_image():
    downloads_folder = os.path.expanduser("~/Downloads/ME")
    images = [f for f in os.listdir(downloads_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not images:
        raise FileNotFoundError("No images found in the Downloads folder.")
    return os.path.join(downloads_folder, random.choice(images))

# Function to get the current daytime
def get_daytime():
    return datetime.now().strftime("%A, %B %d, %Y")

# Function to fetch top 5 trending topics from X (Twitter)
def get_top_5_topics():
    # Placeholder for fetching trending topics from X
    # Replace with actual API call to Twitter/X API
    return ["Topic1", "Topic2", "Topic3", "Topic4", "Topic5"]

# Function to generate cool sentences using LLM
def generate_cool_sentences(topics):
    cool_sentences = []
    for topic in topics:
        prompt = f"Generate a cool and engaging sentence about {topic}:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        sentence = response['choices'][0]['message']['content'].strip()
        cool_sentences.append(sentence)
    return cool_sentences

# Function to fetch comments from a post
def fetch_comments(post_id):
    url = f"https://graph.facebook.com/v23.0/{post_id}/comments"
    params = {
        "access_token": PAGE_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print("Error fetching comments:", response.json())
        return []

# Function to generate a response using LLM
def generate_response(comment):
    prompt = f"Generate a polite and engaging response to the following comment: '{comment}'"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# Function to post a reply to a comment
def post_reply(comment_id, message):
    url = f"https://graph.facebook.com/v23.0/{comment_id}/comments"
    payload = {
        "message": message,
        "access_token": PAGE_TOKEN
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Reply posted successfully:", response.json())
    else:
        print("Error posting reply:", response.json())

def post_images_every_6_hours():
    while True:
        # --- Option 1: Image from URL ---
        payload = {
            "url": "assets/reply-image.png",  # Local folder path
            "caption": "Hello World Baby with image",
            "access_token": PAGE_TOKEN
        }
        response = requests.post(url, data=payload)
        print("From URL:", response.json())

        # --- Option 2: Local Image Upload ---
        try:
            random_image_path = get_random_image()
            with open(random_image_path, "rb") as image_file:
                files = {
                    "source": image_file
                }
                payload2 = {
                    "caption": f"Posting random image: {os.path.basename(random_image_path)}",
                    "access_token": PAGE_TOKEN
                }
                response2 = requests.post(url, files=files, data=payload2)
                print("From local random image:", response2.json())
        except FileNotFoundError as e:
            print(e)

        time.sleep(21600)  # Wait for 6 hours before posting again

def reply_to_comments_every_2_minutes():
    def get_latest_post_id():
        posts_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/posts"
        params = {"access_token": PAGE_TOKEN}
        response = requests.get(posts_url, params=params)
        if response.status_code == 200:
            posts = response.json().get("data", [])
            if posts:
                return posts[0]["id"]
        print("Error fetching posts:", response.json())
        return None

    def get_all_post_ids():
        posts_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/posts"
        params = {"access_token": PAGE_TOKEN}
        response = requests.get(posts_url, params=params)
        if response.status_code == 200:
            posts = response.json().get("data", [])
            return [post["id"] for post in posts]
        print("Error fetching posts:", response.json())
        return []

    def fetch_child_comments(parent_comment_id):
        url = f"https://graph.facebook.com/v23.0/{parent_comment_id}/comments"
        params = {"access_token": PAGE_TOKEN}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print("Error fetching child comments:", response.json())
            return []

    def fetch_post_info(post_id):
        url = f"https://graph.facebook.com/v23.0/{post_id}"
        # Remove deprecated 'attachments' field
        params = {
            "fields": "message,story,full_picture,created_time,privacy,type,icon",
            "access_token": PAGE_TOKEN
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching post info:", response.json())
            return {}

    while True:
        post_ids = get_all_post_ids()
        respond_time = 120  # Default respond time
        for post_id in post_ids:
            post_info = fetch_post_info(post_id)
            comments = fetch_comments(post_id)
            for comment in comments:
                comment_id = comment["id"]
                comment_message = comment["message"]
                # Prepare context for LLM
                # Extract more metadata for context
                post_message = post_info.get('message', '')
                post_story = post_info.get('story', '')
                post_picture = post_info.get('full_picture', '')
                post_caption = ''  # attachments field deprecated, skip
                main_post = post_message or post_story or post_picture or "No main post content available."
                # Download post image if available
                downloaded_image_path = None
                if post_picture:
                    try:
                        img_response = requests.get(post_picture)
                        if img_response.status_code == 200:
                            img_filename = f"downloaded_post_image_{post_info.get('id', 'unknown')}.jpg"
                            with open(img_filename, 'wb') as f:
                                f.write(img_response.content)
                            downloaded_image_path = img_filename
                    except Exception as e:
                        print(f"Error downloading post image: {e}")
                # Save post info to a local file for record
                post_info_filename = f"post_info_{post_info.get('id', 'unknown')}.txt"
                try:
                    with open(post_info_filename, 'w', encoding='utf-8') as f:
                        f.write(f"Message: {post_message}\n")
                        f.write(f"Story: {post_story}\n")
                        f.write(f"Image URL: {post_picture}\n")
                        f.write(f"Caption: {post_caption}\n")
                        f.write(f"Downloaded Image Path: {downloaded_image_path if downloaded_image_path else 'None'}\n")
                except Exception as e:
                    print(f"Error saving post info: {e}")
                post_context = f"Message: {post_message}\nStory: {post_story}\nImage URL: {post_picture}\nCaption: {post_caption}\nDownloaded Image Path: {downloaded_image_path if downloaded_image_path else 'None'}"
                if post_picture:
                    prompt = (
                        f"Here is the main post: {main_post}\n"
                        f"Given the following post context, try to guess the scene, people, and location using all available text and image URL. "
                        f"If the image URL is present, imagine what it could show based on the filename or context. "
                        f"If the location is unclear, make a reasonable guess and say so, e.g. 'it looks like the beach but I don't know exactly where.' "
                        f"Then, reply to this comment: '{comment_message}' in a polite and engaging way, referencing the post context if relevant.\n"
                        f"Post context: {post_context}"
                    )
                else:
                    prompt = (
                        f"Here is the main post: {main_post}\n"
                        f"There is no image in this post, so focus on the text and story to guess the scene, people, and location. "
                        f"If the location is unclear, make a reasonable guess and say so, e.g. 'it looks like a restaurant but I don't know exactly where.' "
                        f"Then, reply to this comment: '{comment_message}' in a polite and engaging way, referencing the post context if relevant.\n"
                        f"Post context: {post_context}"
                    )
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100
                )
                response_message = response['choices'][0]['message']['content'].strip()
                post_reply(comment_id, response_message)
                # Check and reply to child comments (replies)
                child_comments = fetch_child_comments(comment_id)
                if child_comments:
                    respond_time = 20  # If there are child comments, set respond time to 20 seconds
                    for child in child_comments:
                        child_id = child["id"]
                        child_message = child["message"]
                        if post_picture:
                            child_prompt = (
                                f"Here is the main post: {main_post}\n"
                                f"Given the following post context, try to guess the scene, people, and location using all available text and image URL. "
                                f"If the image URL is present, imagine what it could show based on the filename or context. "
                                f"If the location is unclear, make a reasonable guess and say so, e.g. 'it looks like the beach but I don't know exactly where.' "
                                f"Then, reply to this child comment: '{child_message}' in a human-like, conversational way, referencing the post context if relevant.\n"
                                f"Post context: {post_context}"
                            )
                        else:
                            child_prompt = (
                                f"Here is the main post: {main_post}\n"
                                f"There is no image in this post, so focus on the text and story to guess the scene, people, and location. "
                                f"If the location is unclear, make a reasonable guess and say so, e.g. 'it looks like a restaurant but I don't know exactly where.' "
                                f"Then, reply to this child comment: '{child_message}' in a human-like, conversational way, referencing the post context if relevant.\n"
                                f"Post context: {post_context}"
                            )
                        child_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": child_prompt}
                            ],
                            max_tokens=100
                        )
                        human_reply = child_response['choices'][0]['message']['content'].strip()
                        post_reply(child_id, human_reply)
        time.sleep(respond_time)  # Wait before checking for new comments

# Run both tasks in parallel
threading.Thread(target=post_images_every_6_hours, daemon=True).start()
threading.Thread(target=reply_to_comments_every_2_minutes, daemon=True).start()

# Keep the main thread alive
while True:
    time.sleep(1)