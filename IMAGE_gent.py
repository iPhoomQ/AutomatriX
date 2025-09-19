from diffusers import StableDiffusionPipeline
import torch
import os

# Load model with optimizations for 4GB VRAM
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16
).to("cuda")  # use "cpu" if no GPU

# Disable the NSFW filter
pipe.safety_checker = lambda images, clip_input: (images, [False] * len(images))

# Enable attention slicing for memory optimization
pipe.enable_attention_slicing()

# Enable memory-efficient attention
pipe.enable_xformers_memory_efficient_attention()

# Generate image with higher resolution and more inference steps
prompt = "clear blue sky with clouds"
image = pipe(prompt, height=128, width=128, num_inference_steps=50).images[0]  # Adjust resolution and steps as needed

# Save with unique filename
output_dir = "output_images"
os.makedirs(output_dir, exist_ok=True)

counter = 1
while True:
    filename = os.path.join(output_dir, f"cyberpunk_{counter:02d}.png")
    if not os.path.exists(filename):
        image.save(filename)
        break
    counter += 1