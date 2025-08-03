# Speech to Text Overlay

**Speech to Text Overlay** is a simple, open-source desktop application that displays your spoken words as text on your screen in real time.  
It uses [Vosk](https://alphacephei.com/vosk/) for offline speech recognition and supports multiple languages.  
Perfect for streamers, presenters, accessibility needs, or anyone who wants live captions on their desktop!

---

## Features

- **Live speech-to-text overlay** on your screen
- **Supports multiple languages** (Italian, English, Spanish)
- **Multiple audio sources** - Listen from microphone or running applications (Discord, Teams, Zoom, etc.)
- **Process detection** - Automatically detects common communication and media applications
- **Automatic download of language models**
- **Customizable font, size, opacity, position, and duration**
- **No internet required after first model download**
- **Easy to use, no technical knowledge required**

---

## Installation

### Python (I'm going to make it an easy to run .exe, but for now this is the only way)

1. Clone this repository:
   ```
   git clone https://github.com/airjairj/speech-to-text-overlay.git
   cd speech-to-text-overlay
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   python speech_to_text_overlay.py
   ```

---

## Usage

### Basic Setup
1. **Select your language** and customize the overlay appearance.
2. **Choose audio source:**
   - **Microphone**: Capture from your default microphone
   - **Application**: Select from running applications (Discord, Teams, Zoom, browsers, etc.)
3. Click **Start listening**.
4. Speak into your microphone or let the selected application play audio.
5. Your words will appear as an overlay on your screen.
6. Click **Stop listening** to end.

### Audio Source Selection
- **"Listening from" dropdown**: Choose between microphone and detected applications
- **Refresh button (🔄)**: Update the list of running applications
- **Supported applications**: Discord, Teams, Zoom, Skype, Chrome, Firefox, Spotify, VLC, OBS, and many more

### Use Cases
- **Gaming**: Display Discord voice chat as text while gaming
- **Video calls**: Show captions for Teams/Zoom meetings
- **Streaming**: Add live captions to your stream
- **Accessibility**: Real-time captions for hearing-impaired users
- **Content creation**: Caption YouTube videos or media playback

---

## FAQ

**Q: Is my speech sent to the internet?**  
A: No. All recognition is done locally on your computer.

**Q: Why does the app download a model?**  
A: The first time you use a language, the app downloads a small offline speech model (~50MB).

**Q: Can I use this for streaming or presentations?**  
A: Yes! The overlay is designed to be unobtrusive and customizable.

**Q: How do I capture audio from Discord/Teams/other apps?**  
A: Select the application from the "Listening from" dropdown. Note: You may need to configure your system's audio routing (like enabling "Stereo Mix") to capture application audio.

**Q: Why don't I see my application in the list?**  
A: Click the refresh button (it's supposed to look like this 🔄, but is kinda wierd) to update the list, or make sure the application is currently running.

**Q: How do I move the overlay?**  
A: Use the position and preset controls in the app window.

---

## Troubleshooting

- **Microphone not detected:** Make sure your microphone is plugged in and selected as the default recording device.
- **Model download fails:** Check your internet connection and try again.
- **Overlay not visible:** Try adjusting opacity, font size, or position.
- **Application not in list:** Make sure the application is running and click the refresh button.
- **No audio from applications:** You may need to enable "Stereo Mix" in Windows sound settings or use virtual audio cable software.

---

## Contributing

Pull requests and suggestions are welcome!  
Feel free to open issues for bugs or feature requests.

---

## License

This project is licensed under the MIT License.

---

## Credits

- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [psutil](https://github.com/giampaolo/psutil)

---

## Contact

For questions or support, open an issue