# Maya AI - The Advanced Bengali Desktop Assistant

Maya is a sophisticated, locally-hosted AI assistant designed to bridge the gap between voice, vision, and desktop automation. Inspired by JARVIS, she now speaks and understands **Bengali (Bangla)** fluently, making her a perfect companion for South Asian developers and users.

She features **Real-time Voice Interaction**, **Desktop Automation**, and **Hand Gesture Control**.

## 🚀 Key Features

### 🗣️ Fluent Bengali Voice Assistant
-   **Voice**: Uses **`bn-IN-TanishaaNeural`**, a high-quality, natural-sounding female Bengali voice.
-   **Understanding**: Optimized for **Bangla Speech Recognition** (`bn-BD` / `en-IN`), understanding natural phrases like _"কেমন আছো?"_ or _"গান শোনাও"_.
-   **Personality**: Witty, sarcastic, and concise—she replies entirely in Bengali.

### 🧠 Intelligent & Private
-   **Local LLM**: Powered by **Ollama** (running `llama3:latest` or `llama3.2:3b`), ensuring complete privacy and offline capability.
-   **Smart Listening**:
    -   **Self-Hearing Prevention**: Automatically "closes her ears" while speaking to prevent echo loops.
    -   **Dynamic Noise Adjustment**: Adapts to your room's background noise.

### ⚡ Hands-Free Automation (Bengali Commands)
Control your Windows PC entirely with voice:
| Action | Bengali Command | English Equivalent |
| :--- | :--- | :--- |
| **Volume** | "আওয়াজ বাড়াও" / "শব্দ কমাও" / "চুপ করো" | Volume Up/Down/Mute |
| **App Switching** | "অ্যাপ পরিবর্তন করো" / "উইন্ডো সরাও" | Switch Window (Alt+Tab) |
| **Open Apps** | "ইউটিউব খোল" / "ক্রোম চালু করো" | Open YouTube/Chrome |
| **Search** | "ইউটিউবে [Query] খোঁজ" | Search on YouTube |
| **Window** | "বড় করো" / "লুকান" / "বন্ধ করো" | Maximize/Minimize/Close |
| **Typing** | "লিখুন [Text]" | Type dictated text |
| **Scrolling** | "নিচে স্ক্রল করো" | Scroll Down |

## ️ Installation

### 1. Prerequisites
-   **Python 3.10+**
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
pip install edge-tts pygame SpeechRecognition ollama pyautogui
```
*(Note: Windows users might need to install `pyaudio` via pipwin or a .whl file if pip fails)*

## 🎮 Usage

### Start the Voice Assistant
```bash
python maya.py
```
*Wait for the "Maya: Online and ready" message.*

## ⚙️ Customization

You can adjust settings in `maya.py`:

```python
# Change Voice (e.g., to Male Bengali)
VOICE = "bn-BD-PradeepNeural"

# Change Model (for speed vs intelligence)
MODEL = "llama3.2:3b" 
```

## 🤝 Contributing
Contributions are welcome! Feel free to add new Bengali automation triggers or improve the vision model.
