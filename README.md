# Jarvis

Voice-activated AI assistant for macOS. Say "Jarvis" to activate commands.

## Quick Start

```bash
cd ~/jarvis
pip3 install -r requirements.txt
brew install yt-dlp    # for YouTube
brew install ollama    # for AI (optional)

# Start Ollama and pull a model (one time)
ollama serve &
ollama pull llama3.2

# Build the app and run from dock
python3 -m jarvis build
open Jarvis.app
```

Say "Jarvis" → "Yes?" → your command.

## Commands

### Run modes
```bash
python3 -m jarvis run         # foreground with terminal
python3 -m jarvis build        # build Jarvis.app for dock
python3 -m jarvis install      # background service on login
python3 -m jarvis status       # check if running
python3 -m jarvis uninstall   # remove background service
python3 -m jarvis test-mic     # test microphone
```

### What you can say
- Open apps: "Open Chrome", "Open Spotify", "Open Terminal"
- Play music: "Play Drake on Spotify", "Play cooking tutorial on YouTube"
- Volume/brightness: "Turn up volume", "Mute", "Make screen brighter"
- Media controls: "Pause", "Next song", "Previous track"
- Text messages: "Text mom saying I'll be home at 8"
- Free-form AI (with Ollama): "What's the capital of France?"

## Setup

Configure contacts in `~/.jarvis/contacts.json`:
```json
{
  "mom": "+15551234567",
  "john": "john@example.com"
}
```

Grant permissions in System Settings → Privacy & Security:
- Microphone
- Accessibility
- Automation (Spotify, Messages, Chrome)

## Requirements

- macOS
- Internet (speech recognition)
- Spotify app (for Spotify commands)
- yt-dlp (YouTube)
- Ollama + llama3.2 (optional, for AI)
