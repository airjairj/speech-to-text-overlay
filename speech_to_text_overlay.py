import tkinter as tk
from tkinter import font
from tkinter import ttk
import threading
import speech_recognition as sr
import vosk
import json
import pyaudio
import os
import urllib.request
import zipfile
import tkinter.messagebox
import psutil  # Add this import

try:
    import vosk
    import pyaudio
    import psutil
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vosk", "pyaudio", "psutil"])

class SpeechToTextOverlay:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Speech to Text Overlay")
            self.root.geometry("350x330")
            self.root.minsize(350, 330)
            self.root.resizable(True, False)

            # Get screen size
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()

            # Predefined positions (calculated dynamically)
            self.position_presets = self.calculate_position_presets()

            # Default settings
            self.selected_font = tk.StringVar(value="Arial")
            self.font_size = tk.IntVar(value=32)
            self.duration = tk.IntVar(value=3)
            self.opacity = tk.DoubleVar(value=0.8)
            center_bottom_x, center_bottom_y = self.position_presets["Center Bottom"]
            self.pos_x = tk.IntVar(value=center_bottom_x)
            self.pos_y = tk.IntVar(value=center_bottom_y)
            self.selected_preset = tk.StringVar(value="Center Bottom")
            self.is_listening = False

            # Language and Vosk model
            self.language_options = {
                "Italian": "vosk-model-small-it-0.22",
                "English": "vosk-model-small-en-us-0.15",
                "Spanish": "vosk-model-small-es-0.42"
            }
            self.selected_language = tk.StringVar(value="Italian")

            # Listening source selection
            self.listening_sources = self.get_listening_sources()
            self.selected_listening_source = tk.StringVar(value="Audio device")

            # Audio device selection
            self.audio_devices = self.get_audio_devices()
            self.selected_device = tk.StringVar(value="Default")

            self.create_widgets()
            self.overlay = None
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
        except Exception as e:
            print(f"Error during initialization: {e}")

    def get_listening_sources(self):
        try:
            sources = {"Audio device": "microphone"}
            
            # Get running processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    # Expanded filter for common audio/video apps
                    audio_apps = ['discord', 'teams', 'zoom', 'skype', 'chrome', 'firefox', 
                                'edge', 'opera', 'brave', 'spotify', 'vlc', 'obs', 'streamlabs', 
                                'whatsapp', 'telegram', 'youtube', 'msedge', 'iexplore', 'safari']
                    
                    if any(app in proc_name for app in audio_apps):
                        sources[f"{proc.info['name']} (PID: {proc.info['pid']})"] = f"process_{proc.info['pid']}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
            return sources
        except Exception as e:
            print(f"Error getting listening sources: {e}")
            return {"Audio device": "microphone"}

    def refresh_listening_sources(self):
        """Refresh the listening sources dropdown"""
        try:
            # Update listening sources
            self.listening_sources = self.get_listening_sources()
            
            # Update the dropdown menu
            menu = self.listening_source_menu['menu']
            menu.delete(0, 'end')
            
            for source in self.listening_sources.keys():
                menu.add_command(label=source, command=tk._setit(self.selected_listening_source, source))
            
            # Reset to default if current selection no longer exists
            if self.selected_listening_source.get() not in self.listening_sources:
                self.selected_listening_source.set("Audio device")
                
        except Exception as e:
            print(f"Error refreshing listening sources: {e}")

    def get_audio_devices(self):
        try:
            p = pyaudio.PyAudio()
            devices = {"Default": None}
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:  # Only input devices
                    devices[f"{info['name']} (ID: {i})"] = i
            p.terminate()
            return devices
        except Exception as e:
            print(f"Error getting audio devices: {e}")
            return {"Default": None}

    def calculate_position_presets(self):
        try:
            w = self.screen_width
            h = self.screen_height
            margin = 20  # small margin from the edge
            presets = {
                "Top Left": (margin, margin),
                "Bottom Left": (margin, h - margin - 100),
                "Center Top": (w // 2 - 200, margin),
                "Center Bottom": (w // 2 - 200, h - margin - 100),
                "Top Right": (w - margin - 400, margin),
                "Bottom Right": (w - margin - 400, h - margin - 100)
            }
            return presets
        except Exception as e:
            print(f"Error calculating positions: {e}")
            return {}

    def create_widgets(self):
        try:
            row = 0
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=1, minsize=120)

            pad_right = {'padx': (0, 20)}

            tk.Label(self.root, text="Font:").grid(row=row, column=0, sticky="ew")
            fonts = list(font.families())
            fonts.sort()
            tk.OptionMenu(self.root, self.selected_font, *fonts).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Text size:").grid(row=row, column=0, sticky="ew")
            tk.Spinbox(self.root, from_=10, to_=100, textvariable=self.font_size).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Duration (s):").grid(row=row, column=0, sticky="ew")
            tk.Spinbox(self.root, from_=1, to_=10, textvariable=self.duration).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Opacity (0-1):").grid(row=row, column=0, sticky="ew")
            tk.Scale(self.root, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, variable=self.opacity).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Language:").grid(row=row, column=0, sticky="ew")
            tk.OptionMenu(self.root, self.selected_language, *self.language_options.keys()).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            # Listening source selection with refresh button
            tk.Label(self.root, text="Listening from:").grid(row=row, column=0, sticky="ew")
            listening_frame = tk.Frame(self.root)
            listening_frame.grid(row=row, column=1, sticky="ew", **pad_right)
            listening_frame.grid_columnconfigure(0, weight=1)
            listening_frame.grid_columnconfigure(1, weight=0)
            
            self.listening_source_menu = tk.OptionMenu(listening_frame, self.selected_listening_source, *self.listening_sources.keys())
            self.listening_source_menu.grid(row=0, column=0, sticky="ew")
            
            refresh_btn = tk.Button(listening_frame, text="🔄", width=3, command=self.refresh_listening_sources)
            refresh_btn.grid(row=0, column=1, sticky="e", padx=(5, 0))
            row += 1

            # Audio device selection
            tk.Label(self.root, text="Audio device:").grid(row=row, column=0, sticky="ew")
            tk.OptionMenu(self.root, self.selected_device, *self.audio_devices.keys()).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Preset position:").grid(row=row, column=0, sticky="ew")
            presets = list(self.position_presets.keys()) + ["Custom"]
            tk.OptionMenu(self.root, self.selected_preset, *presets, command=self.set_preset_position).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Position X:").grid(row=row, column=0, sticky="ew")
            tk.Spinbox(self.root, from_=0, to=1920, textvariable=self.pos_x, command=self.set_custom_position).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            tk.Label(self.root, text="Position Y:").grid(row=row, column=0, sticky="ew")
            tk.Spinbox(self.root, from_=0, to=1080, textvariable=self.pos_y, command=self.set_custom_position).grid(row=row, column=1, sticky="ew", **pad_right)
            row += 1

            self.start_btn = tk.Button(self.root, text="Start listening", command=self.toggle_listen)
            self.start_btn.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew", padx=20)
        except Exception as e:
            print(f"Error creating widgets: {e}")

    def set_preset_position(self, value):
        try:
            if value in self.position_presets:
                x, y = self.position_presets[value]
                self.pos_x.set(x)
                self.pos_y.set(y)
            else:
                # Custom: do not change anything
                pass
        except Exception as e:
            print(f"Error setting preset position: {e}")

    def set_custom_position(self, *args):
        try:
            # If user manually changes X or Y, set preset to Custom
            if self.selected_preset.get() != "Custom":
                self.selected_preset.set("Custom")
        except Exception as e:
            print(f"Error setting custom position: {e}")

    def toggle_listen(self):
        try:
            if not self.is_listening:
                self.is_listening = True
                self.start_btn.config(text="Stop listening")
                threading.Thread(target=self.listen_microphone_vosk, daemon=True).start()
            else:
                self.is_listening = False
                self.start_btn.config(text="Start listening")
        except Exception as e:
            print(f"Error toggling listening: {e}")

    def show_progress_window(self, title, message):
        self.progress_win = tk.Toplevel(self.root)
        self.progress_win.title(title)
        self.progress_win.geometry("350x100")
        self.progress_win.resizable(False, False)
        tk.Label(self.progress_win, text=message).pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.progress_win, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar["value"] = 0
        self.progress_win.update()

    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.progress_win.update()

    def close_progress_window(self):
        self.progress_win.destroy()

    def listen_microphone_vosk(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_folder = self.language_options[self.selected_language.get()]
            model_path = os.path.join(base_dir, model_folder)
            if not os.path.exists(model_path):
                response = tkinter.messagebox.askyesno(
                    "Download Vosk model",
                    f"The model '{model_folder}' is not present.\nDo you want to download it now (~50MB)?"
                )
                if not response:
                    print("Model download cancelled by user.")
                    return
                print(f"Vosk model '{model_folder}' not found, downloading...")
                urls = {
                    "vosk-model-small-it-0.22": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip",
                    "vosk-model-small-en-us-0.15": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                    "vosk-model-small-es-0.42": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
                }
                url = urls.get(model_folder)
                zip_path = os.path.join(base_dir, f"{model_folder}.zip")
                self.show_progress_window("Downloading model", "Download in progress...")
                try:
                    def reporthook(blocknum, blocksize, totalsize):
                        percent = int(blocknum * blocksize * 100 / totalsize)
                        self.update_progress(percent)
                    urllib.request.urlretrieve(url, zip_path, reporthook)
                    self.update_progress(100)
                    self.progress_win.title("Extracting model")
                    self.progress_win.children['!label'].config(text="Extracting...")
                    self.progress_win.update()
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(base_dir)
                    self.close_progress_window()
                    print("Extraction completed.")
                    os.remove(zip_path)
                except Exception as e:
                    self.close_progress_window()
                    print(f"Error during model download/extraction: {e}")
                    return
            model = vosk.Model(model_path)
            rec = vosk.KaldiRecognizer(model, 16000)
            p = pyaudio.PyAudio()
            
            # Get selected device
            device_id = self.audio_devices[self.selected_device.get()]
            
            stream = p.open(
                format=pyaudio.paInt16, 
                channels=1, 
                rate=16000, 
                input=True, 
                input_device_index=device_id,
                frames_per_buffer=8000
            )
            stream.start_stream()
            buffer = ""
            last_text = ""
            while self.is_listening:
                try:
                    data = stream.read(4000, exception_on_overflow=False)
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text and text != last_text:
                            last_text = text
                            self.show_overlay(text)
                    else:
                        partial = json.loads(rec.PartialResult()).get("partial", "")
                        if partial and partial != buffer:
                            buffer = partial
                            self.show_overlay(partial)
                except Exception as e:
                    print(f"Error during Vosk streaming: {e}")
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error initializing Vosk: {e}")
            
    def show_overlay(self, text):
        try:
            # Create overlay only once
            if not hasattr(self, 'overlay') or self.overlay is None or not self.overlay.winfo_exists():
                self.overlay = tk.Toplevel(self.root)
                self.overlay.overrideredirect(True)
                self.overlay.attributes("-topmost", True)
                self.overlay.attributes("-alpha", self.opacity.get())
                self.overlay.geometry(f"+{self.pos_x.get()}+{self.pos_y.get()}")
                self.overlay_label = tk.Label(
                    self.overlay,
                    text=text,
                    font=(self.selected_font.get(), self.font_size.get()),
                    bg="black",
                    fg="white"
                )
                self.overlay_label.pack(ipadx=10, ipady=10)
            else:
                # Update text, position, and opacity
                self.overlay_label.config(text=text, font=(self.selected_font.get(), self.font_size.get()))
                self.overlay.geometry(f"+{self.pos_x.get()}+{self.pos_y.get()}")
                self.overlay.attributes("-alpha", self.opacity.get())
                self.overlay.deiconify()
            # Cancel previous hide timer if exists
            if hasattr(self, 'after_id') and self.after_id is not None:
                self.overlay.after_cancel(self.after_id)
            # Set new hide timer
            self.after_id = self.overlay.after(self.duration.get() * 1000, self.overlay.withdraw)
        except Exception as e:
            print(f"Error showing overlay: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SpeechToTextOverlay(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
