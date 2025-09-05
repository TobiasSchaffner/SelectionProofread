# SelectionProofread

SelectionProofread is a Python script that allows you to proofread and improve selected text using OpenAI's GPT models. The script is designed to be bound to a key combination in your window manager, making it easy to use while working in any application.

## Features

- Automatically copies the selected text.
- Sends the text to OpenAI's API for proofreading and improvement.
- Replaces the selected text with the improved version.
- Currently only supports X11 window managers.

## Requirements

- Python 3.6 or higher
- `openai` Python library
- `pyperclip` Python library
- `xdotool` (for X11)
- A valid OpenAI API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/selectionproofread.git
    ```

2. Install the required Python packages and ensure you have `xdotool` (for X11) installed:

    - On Debian/Ubuntu:
    ```bash
    sudo apt install python3-openai python3-pyperclip xdotool
    ```

3. Create the configuration file and change permissions to secure your API Key:
    ```bash
    mkdir -p ~/.config/selectionproofread
    nano ~/.config/selectionproofread/config.json
    chmod 600 ~/.config/selectionproofread/config.json
    ```
    Example `config.json`:
    ```json
    {
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "your_openai_api_key",
        "model": "gpt-4",
        "prompt": "Proofread and improve this text"
    }
    ```

## Usage

1. Bind the script (selectionproofread/selectionproofread/main.py) to a key combination in your window manager.

2. Select the text you want to proofread in any application.

3. Press the configured key combination (e.g., `Mod+p`).

4. The script will:
    - Copy the selected text.
    - Send it to OpenAI for proofreading.
    - Replace the selected text with the improved version.

## Logs

Logs are stored in `/var/tmp/selectionproofread.log`. Check this file for debugging information if something goes wrong.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
