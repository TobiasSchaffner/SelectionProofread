#!/usr/bin/env python3

import os
import sys
import json
import pyperclip
import logging
import openai
import subprocess

LOG_FILE = "/var/tmp/selectionproofread.log"
CONFIG_PATH = os.path.expanduser("~/.config/selectionproofread/config.json")

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

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

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

def send_command(command):
    """Send a command to the system."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        sys.exit(1)

def send_keystroke(keystroke):
    """Send a keystroke using the appropriate tool based on the session type."""
    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    if session_type == 'wayland':
        send_command(["ydotool", "key", "--repeat", "1", keystroke])
    elif session_type == 'x11':
        send_command(["xdotool", "key", "--repeat", "1", "--clearmodifiers", keystroke])
    else:
        logging.error("Unknown or unsupported window manager.")
        sys.exit(1)

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
    send_keystroke("ctrl+c")
    selected_text = pyperclip.paste().strip()
    if not selected_text:
        logging.warning("No text selected.")
        sys.exit(0)

    full_prompt = f"{prompt_template} (KEEP THE ORIGINAL LANGUAGE AND ONLY RETURN THE FINAL ANSWER!)\n\n{selected_text}"
    logging.info(f"Sending text to OpenAI API using model: {model}")

    # Call OpenAI API
    try:
        client = openai.OpenAI(base_url=base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        result = response.choices[0].message.content if response.choices else ""
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

    if not result:
        logging.warning("No result from AI.")
        sys.exit(1)

    # Replace selected text with AI output
    logging.info("Replacing selected text with AI output...")
    pyperclip.copy(result)
    send_keystroke("ctrl+v")
    logging.info("Text replaced successfully")

if __name__ == "__main__":
    main()
