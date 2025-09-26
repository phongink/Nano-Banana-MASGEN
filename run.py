import google.generativeai as genai
from PIL import Image
from io import BytesIO
import os
import time

# ==============================================================================
# SECTION 1: CONFIGURATION - YOU ONLY NEED TO EDIT HERE
# ==============================================================================

# TODO: Paste your Google API Key here.
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

# Image generation model name.
MODEL_NAME = "gemini-2.5-flash-image-preview"

# The directory where all generated images will be saved.
OUTPUT_DIR = "generated_character_images"

# --- NEW CONFIGURATION ---
# The name of the file containing your prompts.
PROMPT_FILE_PATH = "prompts.txt"

# Path to the first character reference image.
REFERENCE_IMAGE_1_PATH = "character_ref_1.png"
# Path to the second character reference image.
REFERENCE_IMAGE_2_PATH = "character_ref_2.png"

# ==============================================================================
# SECTION 2: MAIN LOGIC - NO CHANGES NEEDED BELOW THIS LINE
# ==============================================================================

print("--- Starting batch image generation with character reference ---")

# --- A. Configure and Initialize ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"Successfully loaded model: {MODEL_NAME}")
except Exception as e:
    print(f"Error configuring API or model: {e}")
    print("Please check your GOOGLE_API_KEY and model name.")
    exit()

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- B. Read Prompts from the Text File ---
try:
    with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
        # Read each line, strip whitespace, and ignore empty lines
        prompts = [line.strip() for line in f if line.strip()]
    if not prompts:
        print(f"Error: The file '{PROMPT_FILE_PATH}' is empty or contains no valid prompts.")
        exit()
    print(f"Successfully read {len(prompts)} prompts from '{PROMPT_FILE_PATH}'.")
except FileNotFoundError:
    print(f"Error: Prompt file not found at '{PROMPT_FILE_PATH}'.")
    print("Please create this file and add your prompts.")
    exit()

# --- C. Load Reference Images ---
try:
    print(f"Loading reference image 1: '{REFERENCE_IMAGE_1_PATH}'")
    ref_image_1 = Image.open(REFERENCE_IMAGE_1_PATH)
    print(f"Loading reference image 2: '{REFERENCE_IMAGE_2_PATH}'")
    ref_image_2 = Image.open(REFERENCE_IMAGE_2_PATH)
    print("Reference images loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: Reference image file not found. {e}")
    print("Please check the file paths in the configuration section.")
    exit()

# --- D. Processing Loop for Image Generation ---
total_prompts = len(prompts)
for i, base_prompt in enumerate(prompts):
    print(f"\n[{i+1}/{total_prompts}] Processing prompt: \"{base_prompt[:70]}...\"")

    try:
        # Append the 16:9 aspect ratio request to each prompt for better results
        final_prompt = f"{base_prompt}, cinematic style, 16:9 aspect ratio, photorealistic, ultra high detail"

        # **IMPORTANT**: Create the content payload including the two images and the prompt.
        # This is how you "show" the AI your character.
        contents_to_send = [
            ref_image_1,
            ref_image_2,
            final_prompt
        ]

        # Send the generation request
        response = model.generate_content(contents_to_send)

        # Extract image data from the response
        image_part = response.parts[0]
        if image_part.inline_data:
            image_data = image_part.inline_data.data
            image = Image.open(BytesIO(image_data))

            # Create a safe and unique filename from the prompt
            safe_prompt_name = "".join([c for c in base_prompt if c.isalnum() or c in " _-"]).rstrip()
            filename = f"{i+1:03d}_{safe_prompt_name[:50]}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Save the image
            image.save(filepath)
            print(f"  -> Success! Image saved to: {filepath}")
        else:
            print(f"  -> Error: No image data received for this prompt.")
            if response.prompt_feedback:
                print(f"  -> API Feedback: {response.prompt_feedback}")

    except Exception as e:
        print(f"  -> A critical error occurred while processing the prompt: {e}")

    # Pause for 2 seconds between API calls to avoid rate limiting
    time.sleep(2)

print("\n--- BATCH PROCESS COMPLETE ---")
print(f"All images have been saved in the '{OUTPUT_DIR}' directory.")
