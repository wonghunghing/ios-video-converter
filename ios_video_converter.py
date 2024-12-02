import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import sys
import io

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.output = text_widget
        self.buffer = io.StringIO()

    def write(self, string):
        # Write to both the text widget and the buffer
        self.output.insert(tk.END, string)
        self.output.see(tk.END)
        self.buffer.write(string)

    def flush(self):
        # Ensure the text widget updates
        self.output.update_idletasks()
        self.buffer.flush()

    def getvalue(self):
        return self.buffer.getvalue()

class VideoCodecConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Video Codec Converter")
        master.geometry("600x500")

        # Directory Selection
        self.dir_label = tk.Label(master, text="Select Root Directory:")
        self.dir_label.pack(pady=(10, 0))

        self.dir_path = tk.StringVar()
        self.dir_entry = tk.Entry(master, textvariable=self.dir_path, width=70)
        self.dir_entry.pack(pady=(0, 10))

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_directory)
        self.browse_button.pack(pady=(0, 10))

        # Create button frame for layout
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=(0, 10))
        
        # Move convert button to frame and add stop button
        self.convert_button = tk.Button(self.button_frame, text="Start Conversion", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.button_frame, text="Stop Conversion", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Progress Text Area
        self.progress_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=70, height=20)
        self.progress_text.pack(pady=(0, 10))

        # Total Progress
        self.total_progress_label = tk.Label(master, text="Total Progress: 0%")
        self.total_progress_label.pack(pady=(0, 10))

        # Redirect stdout and stderr to the text widget
        self.console_redirector = ConsoleRedirector(self.progress_text)
        sys.stdout = self.console_redirector
        sys.stderr = self.console_redirector

    def browse_directory(self):
        """Open directory selection dialog"""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.dir_path.set(selected_dir)

    def is_compatible(self, file_path):
        """Check codec compatibility"""
        try:
            # Video codec check
            video_result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", 
                 "-show_entries", "stream=codec_name", 
                 "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            video_codec = video_result.stdout.strip()
            
            # Audio codec check
            audio_result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a:0", 
                 "-show_entries", "stream=codec_name", 
                 "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            audio_codec = audio_result.stdout.strip()

            # Check if codecs are compatible with iOS (H.264 video + AAC audio)
            return video_codec == "h264" and audio_codec in ["aac", "mp3"]
        except Exception as e:
            print(f"Error checking compatibility for {file_path}: {e}")
            return False

    def convert_file(self, file_path, output_path):
        """Convert video file"""
        try:
            # Use subprocess with capture to print verbose output
            process = subprocess.Popen(
                ["ffmpeg", "-i", file_path, "-c:v", "libx264", 
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", 
                 output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )

            # Print real-time output
            for line in process.stdout:
                print(line.strip())

            # Wait for the process to complete and check return code
            return_code = process.wait()
            if return_code == 0:
                print(f"Converted: {file_path} -> {output_path}")
            else:
                print(f"Conversion failed for {file_path}")
        except Exception as e:
            print(f"Error converting {file_path}: {e}")

    def process_videos(self):
        """Main video processing function"""
        root_dir = self.dir_path.get()
        if not root_dir:
            messagebox.showerror("Error", "Please select a directory")
            return

        # Disable buttons during conversion
        self.convert_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)

        try:
            # Clear previous progress
            self.progress_text.delete('1.0', tk.END)
            
            # Enable stop button, disable convert and browse
            self.stop_button.config(state=tk.NORMAL)
            self.convert_button.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)

            # Collect all MP4 files
            mp4_files = []
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if filename.lower().endswith(".mp4"):
                        mp4_files.append(os.path.join(dirpath, filename))

            total_files = len(mp4_files)
            converted_files = 0

            # Process files
            for file_path in mp4_files:
                if not self.is_compatible(file_path):
                    print(f"Incompatible file found: {file_path}")
                    output_path = os.path.join(
                        os.path.dirname(file_path), 
                        f"{os.path.splitext(os.path.basename(file_path))[0]}_converted.mp4"
                    )
                    self.convert_file(file_path, output_path)
                    converted_files += 1
                else:
                    print(f"File is compatible: {file_path}")

                # Update total progress
                progress_percentage = int((converted_files / total_files) * 100)
                self.total_progress_label.config(text=f"Total Progress: {progress_percentage}%")
                self.master.update_idletasks()

            # Final message
            messagebox.showinfo("Conversion Complete", 
                                f"Processed {total_files} files\n"
                                f"Converted {converted_files} incompatible files")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            # Re-enable/disable buttons
            self.convert_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_cancelled = False

    def start_conversion(self):
        """Start conversion in a separate thread"""
        # Start processing in a separate thread to keep GUI responsive
        conversion_thread = threading.Thread(target=self.process_videos)
        conversion_thread.start()

    def stop_conversion(self):
        """Stop the current conversion"""
        self.is_cancelled = True

def main():
    root = tk.Tk()
    app = VideoCodecConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()