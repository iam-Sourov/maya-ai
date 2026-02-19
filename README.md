# Maya AI - Advanced Desktop Assistant

Maya is a powerful, locally-hosted AI assistant designed to be your intelligent desktop companion. Inspired by JARVIS, she bridges the gap between voice, web automation, and system control.

She is optimized for **South Asian English accents** and runs completely offline using local LLMs suitable for privacy-conscious users.

## 🚀 Key Features

### 🗣️ Natural Voice & Hearing
-   **Voice**: Uses **`en-IN-PradeepNeural`** (Professional Indian English Male).
-   **Hearing**: Optimized for Indian/Bangladeshi English accents (`en-IN` engine).
-   **Conversation**: Powered by **Llama 3** (via Ollama), Maya has a witty, sarcastic, and concise personality.
-   **Smart Listening**:
    -   **Self-Hearing Prevention**: She deafens herself while speaking to prevent echo loops.
    -   **Phonetic Autocorrect**: Automatically fixes common misheard words (e.g., "momo" -> "moho").

### ⚡ Desktop Automation
Control your Windows PC entirely with voice commands:

| Action | Voice Command | Description |
| :--- | :--- | :--- |
| **Play Music** | "Play [Song Name]" | *New!* Auto-launches Chrome, searches YouTube, and plays the video. |
| **Volume** | "Volume Up" / "Down" / "Mute" | Adjusts system volume. |
| **App Switching** | "Switch Window" / "Switch to Chrome" | Uses Alt+Tab or Windows Search to switch apps. |
| **Open Apps** | "Open YouTube", "Open Google" | Launches websites/apps instantly. |
| **Window** | "Maximize", "Minimize", "Close Window" | Manages active windows. |
| **Typing** | "Type [Text]" | Types whatever you dictate. |
| **Scrolling** | "Scroll Down" / "Up" | Scrolls the active page. |

### 🛑 Global Kill Switch
-   **Emergency Stop**: Press **`ESC`** at any time to instantly kill the program, stop speaking, and stop listening.

## 🛠️ Installation

### 1. Prerequisites
-   **Python 3.10+**
-   **Google Chrome** (for Selenium automation)
-   **Ollama**: [Download here](https://ollama.com/) and pull the model:
    ```bash
    ollama run llama3:latest
    # OR for faster performance:
    ollama run llama3.2:3b
    ```

### 2. Setup
Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/maya-ai.git
cd maya-ai
pip install edge-tts pygame SpeechRecognition ollama pyautogui keyboard selenium webdriver-manager
```
*(Note: Windows users might need to install `pyaudio` manualy if pip fails)*

## 🎮 Usage

### Start the Assistant
```bash
python maya.py
```
*Wait for the "Maya: Online and ready" message.*

## ⚙️ Customization

You can adjust settings in `maya.py`:

```python
# Change Voice (e.g., to Female English)
VOICE = "en-IN-NeerjaNeural"

# Change Model (for speed vs intelligence)
MODEL = "llama3.2:3b" 
```

## 🤝 Contributing
Contributions are welcome! Feel free to add new automation skills or improve the AI performance.
