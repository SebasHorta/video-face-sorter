# group_faces.py

import os
import sys
import face_recognition
from moviepy import VideoFileClip
from tqdm import tqdm
import numpy as np
from colorama import init, Fore, Style
from PIL import UnidentifiedImageError
import pillow_heif  # 🔁 HEIC support
pillow_heif.register_heif_opener()  # ✅ Enable HEIC loading in PIL

# Initialize colorama
init(autoreset=True)

VIDEO_DIR = "videos"
OUTPUT_DIR = "output"
FRAME_INTERVAL = 2.0  # seconds
TOLERANCE = 0.5       # face matching threshold

def load_known_face(image_path):
    print(f"Loading reference image from: {image_path}")
    try:
        image = face_recognition.load_image_file(image_path)
    except (UnidentifiedImageError, FileNotFoundError) as e:
        raise ValueError(f"Cannot open image file: {e}")
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise ValueError("No face found in the reference image.")
    return encodings[0]

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def find_person_timestamps_multi(video_path, known_people):
    """
    known_people: list of tuples (name, encoding)
    Returns dict: { name: [timestamps] }
    """
    results = {name: [] for name, _ in known_people}
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration

        for t in np.arange(0, duration, FRAME_INTERVAL):
            frame = clip.get_frame(t)
            face_locations = face_recognition.face_locations(frame)
            frame_encodings = face_recognition.face_encodings(frame, face_locations)

            # For each detected face, check all known people
            matched_names_this_frame = set()
            for face_enc in frame_encodings:
                for name, known_enc in known_people:
                    if name in matched_names_this_frame:
                        continue  # Already matched this person for this frame
                    match = face_recognition.compare_faces([known_enc], face_enc, tolerance=TOLERANCE)[0]
                    if match:
                        results[name].append(round(t, 2))
                        matched_names_this_frame.add(name)

        clip.reader.close()
        clip.audio.reader.close_proc()
    except Exception as e:
        print(f"Error processing {video_path}: {e}")

    # Remove duplicates and sort timestamps per person
    for name in results:
        results[name] = sorted(set(results[name]))
    return results

def main():
    while True:
        known_people = []

        # Collect multiple people before scanning
        while True:
            image_path = input("👉 Drag and drop the image of the person here, then press Enter: ").strip().strip('"').strip("'")
            if not os.path.exists(image_path):
                print(f"{Fore.RED}❌ Image not found. Please try again.{Style.RESET_ALL}")
                continue

            try:
                known_encoding = load_known_face(image_path)
            except ValueError as e:
                print(f"{Fore.RED}❌ {e}{Style.RESET_ALL}")
                choice = input("Would you like to try another photo? (y/n): ").strip().lower()
                if choice != 'y':
                    print("Exiting program. Goodbye!")
                    sys.exit(0)
                else:
                    continue

            name = input("Enter the person's name: ").strip()
            if not name:
                print(f"{Fore.RED}❌ Name cannot be empty.{Style.RESET_ALL}")
                continue

            known_people.append((name, known_encoding))

            add_more = input("Would you like to add another person? (y/n): ").strip().lower()
            if add_more != 'y':
                break

        if not known_people:
            print(f"{Fore.RED}No people to scan for. Exiting.{Style.RESET_ALL}")
            sys.exit(0)

        print(f"\n🔍 Scanning videos for {len(known_people)} person(s)...")

        video_files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(".mp4")]

        all_results = {name: {} for name, _ in known_people}

        for filename in tqdm(video_files, desc="Processing videos"):
            video_path = os.path.join(VIDEO_DIR, filename)
            video_results = find_person_timestamps_multi(video_path, known_people)
            for name, timestamps in video_results.items():
                if timestamps:
                    if filename not in all_results[name]:
                        all_results[name][filename] = []
                    all_results[name][filename].extend(timestamps)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for name in all_results:
            output_file = os.path.join(OUTPUT_DIR, f"{name}_videos.txt")
            existing_entries = {}
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    for line in f:
                        if ':' in line:
                            vid, times_str = line.strip().split(":", 1)
                            existing_entries[vid.strip()] = times_str.strip()

            for video, times in all_results[name].items():
                formatted_times = [format_timestamp(t) for t in times]
                times_str = ", ".join(formatted_times)
                if video in existing_entries:
                    old_times = set(existing_entries[video].split(", "))
                    new_times = set(formatted_times)
                    combined = sorted(old_times.union(new_times))
                    existing_entries[video] = ", ".join(combined)
                else:
                    existing_entries[video] = times_str

            with open(output_file, "w") as f:
                for video, times_str in sorted(existing_entries.items()):
                    f.write(f"{video}: {times_str}\n")

            if existing_entries:
                print(f"\n{Fore.GREEN}✅ Done for {name}!\n")
                print(f"{Style.BRIGHT}{name} was found in the following videos at these timestamps (MM:SS):\n")
                for video, times_str in sorted(existing_entries.items()):
                    print(f"  {Fore.CYAN}- {Style.BRIGHT}{video}{Style.RESET_ALL}: {Fore.YELLOW}{times_str}")
                print(f"\n{Fore.MAGENTA}The list has been saved/updated at '{output_file}'.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}{Style.BRIGHT}{name} was NOT found in any of the videos.{Style.RESET_ALL}")

        # Ask if want to scan another person or quit
        again = input("\nWould you like to scan for another person (or people)? (y/n): ").strip().lower()
        if again != 'y':
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
