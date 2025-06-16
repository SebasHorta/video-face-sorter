import os
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from face_sorter_backend import load_known_face, scan_and_save_all

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FaceSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("✨ Face Sorter Pro")
        self.geometry("820x640")
        # self.resizable(False, False)

        self.known_people = []
        self.video_dir = os.path.abspath("videos")
        self.output_dir = os.path.abspath("output")

        self.scan_start_time = None
        self.fun_messages = [
            "Discombobulating the combobulators...",
            "Calibrating face lasers...",
            "Summoning face spirits...",
            "Buffing pixels to perfection...",
            "Aligning digital goggles...",
            "Locating friendly faces...",
            "Please hold while we sort the pixels..."
        ]

        self.build_ui()

    def build_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="📷 Face Sorter Pro", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Input Frame
        input_frame = ctk.CTkFrame(self, corner_radius=15)
        input_frame.pack(pady=10, padx=20, fill="x")

        self.person_name_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter person name")
        self.person_name_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_person_btn = ctk.CTkButton(input_frame, text="➕ Add Person Image", command=self.add_person_image)
        self.add_person_btn.grid(row=0, column=1, padx=10, pady=10)

        input_frame.columnconfigure(0, weight=1)

        # Video folder selection
        self.video_dir_btn = ctk.CTkButton(self, text=f"🎞️ Select Videos Folder (Current: {self.video_dir})", command=self.select_video_dir)
        self.video_dir_btn.pack(pady=(5, 10), padx=20, fill="x")

        # Start scan
        self.start_scan_btn = ctk.CTkButton(self, text="🚀 Start Scanning", command=self.start_scanning, height=40)
        self.start_scan_btn.pack(pady=10, padx=20, fill="x")

        # Progress bar + percentage
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack(padx=20, pady=(5, 0), fill="x")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=12, corner_radius=10)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.percent_label = ctk.CTkLabel(progress_frame, text="0%", font=ctk.CTkFont(size=14, weight="bold"))
        self.percent_label.pack(side="right")

        # Output display
        self.output_box = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=13), height=280)
        self.output_box.pack(padx=20, pady=(15, 10), fill="both", expand=True)
        self.output_box.insert("end", "Welcome to Face Sorter Pro. Add a person and begin scanning.\n")
        self.output_box.configure(state="disabled")

    def log(self, text):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.see("end")
        self.output_box.configure(state="disabled")
        self.update()

    def add_person_image(self):
        name = self.person_name_entry.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter a name first.")
            return

        file_path = filedialog.askopenfilename(title="Select Reference Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.heic")])
        if not file_path:
            return

        try:
            encoding = load_known_face(file_path)
            self.known_people.append((name, encoding))
            self.log(f"✅ Added '{name}' from {os.path.basename(file_path)}")
            self.person_name_entry.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face encoding:\n{e}")

    def select_video_dir(self):
        folder = filedialog.askdirectory(title="Select Videos Folder")
        if folder:
            self.video_dir = folder
            self.video_dir_btn.configure(text=f"🎞️ Select Videos Folder (Current: {self.video_dir})")

    def start_scanning(self):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")

        if not self.known_people:
            messagebox.showerror("Error", "Please add at least one person to scan for.")
            return
        if not os.path.exists(self.video_dir):
            messagebox.showerror("Error", f"Videos folder does not exist:\n{self.video_dir}")
            return

        self.disable_ui()
        self.scan_start_time = time.time()
        self.progress_bar.set(0)
        self.percent_label.configure(text="0%")
        self.log("🔍 Starting scan across selected videos...\n")

        try:
            saved_files = scan_and_save_all(
                self.known_people,
                self.video_dir,
                self.output_dir,
                progress_callback=self.update_progress
            )

            if saved_files:
                self.log("\n✅ Scan complete! See matched results below:\n")
                for filepath in saved_files:
                    try:
                        self.log(f"📄 {os.path.basename(filepath)}:")
                        with open(filepath, "r") as f:
                            lines = ["    " + line.strip() for line in f.readlines() if line.strip()]
                            self.log("\n".join(lines) + "\n")
                    except Exception as read_err:
                        self.log(f"❌ Could not read {filepath}: {read_err}\n")
            else:
                self.log("⚠️ Scan finished but no matches were found.")

        except Exception as e:
            messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{e}")
        finally:
            self.enable_ui()
            self.progress_bar.set(1)
            self.percent_label.configure(text="100%")

    def update_progress(self, current_idx, total, video_name, *args):
        progress_fraction = current_idx / total
        percent = int(progress_fraction * 100)
        self.progress_bar.set(progress_fraction)
        self.percent_label.configure(text=f"{percent}%")

        elapsed = time.time() - self.scan_start_time
        eta = (elapsed / progress_fraction - elapsed) if progress_fraction > 0 else 0
        eta_str = time.strftime("%M:%S", time.gmtime(eta))

        fun_message = self.fun_messages[current_idx % len(self.fun_messages)]
        self.log(f"🎬 Video {current_idx}/{total}: {video_name} | ETA: {eta_str} | {fun_message}")

    def disable_ui(self):
        self.add_person_btn.configure(state="disabled")
        self.start_scan_btn.configure(state="disabled")
        self.video_dir_btn.configure(state="disabled")
        self.person_name_entry.configure(state="disabled")

    def enable_ui(self):
        self.add_person_btn.configure(state="normal")
        self.start_scan_btn.configure(state="normal")
        self.video_dir_btn.configure(state="normal")
        self.person_name_entry.configure(state="normal")

if __name__ == "__main__":
    app = FaceSorterApp()
    app.mainloop()