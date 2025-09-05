#!/usr/bin/env python3

import os
import sys
import json
import pyperclip
import logging
import openai
from evdev import UInput, ecodes as e

# Constants
LOG_FILE = "/var/tmp/selectionproofread.log"
CONFIG_PATH = os.path.expanduser("~/.config/selectionproofread/config.json")

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# Utility functions
def load_config():
    """Load configuration from the config file."""
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing config file: {e}")
        sys.exit(1)

def send_key_combination(key_combination):
    """Send a key combination using UInput."""
    try:
        vk = UInput({e.EV_KEY: key_combination})
        for key in key_combination:
            vk.write(e.EV_KEY, key, 1)  # Press key
        for key in reversed(key_combination):
            vk.write(e.EV_KEY, key, 0)  # Release key
        vk.syn()
    finally:
        vk.close()

def call_openai_api(base_url, api_key, model, prompt):
    """Call the OpenAI API with the given parameters."""
    try:
        client = openai.OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content if response.choices else ""
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

# Main function
def main():
    logging.info("=== SelectionProofread started ===")

    # Load configuration
    logging.info("Loading config...")
    config = load_config()
    base_url = config.get("api_base_url", "https://api.openai.com/v1")
    api_key = config.get("api_key")
    model = config.get("model", "gpt-4")
    prompt_template = config.get("prompt", "Proofread and improve this text")

    if not api_key:
        logging.error("API key missing in config.")
        sys.exit(1)

    # Copy selected text
    send_key_combination([e.KEY_LEFTCTRL, e.KEY_C])
    selected_text = pyperclip.paste().strip()
    if not selected_text:
        logging.warning("No text selected.")
        sys.exit(0)

    # Prepare prompt and call OpenAI API
    full_prompt = f"{prompt_template} (KEEP THE ORIGINAL LANGUAGE AND ONLY RETURN THE FINAL ANSWER!)\n\n{selected_text}"
    logging.info(f"Sending text to OpenAI API using model: {model}")
    result = call_openai_api(base_url, api_key, model, full_prompt)

    if not result:
        logging.warning("No result from AI.")
        sys.exit(1)

    # Replace selected text with AI output
    logging.info("Replacing selected text with AI output...")
    pyperclip.copy(result)
    send_key_combination([e.KEY_LEFTCTRL, e.KEY_V])
    logging.info("Text replaced successfully")

if __name__ == "__main__":
    main()
