# face_sorter_backend.py

import os
from moviepy import VideoFileClip
import numpy as np
import face_recognition

FRAME_INTERVAL = 2.0
TOLERANCE = 0.5


def load_known_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise ValueError(f"No face found in image: {image_path}")
    return encodings[0]


def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def find_person_timestamps_multi(video_path, known_people):
    results = {name: [] for name, _ in known_people}
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        for t in np.arange(0, duration, FRAME_INTERVAL):
            frame = clip.get_frame(t)
            face_locations = face_recognition.face_locations(frame)
            frame_encodings = face_recognition.face_encodings(frame, face_locations)
            matched_names_this_frame = set()
            for face_enc in frame_encodings:
                for name, known_enc in known_people:
                    if name in matched_names_this_frame:
                        continue
                    if face_recognition.compare_faces([known_enc], face_enc, tolerance=TOLERANCE)[0]:
                        results[name].append(round(t, 2))
                        matched_names_this_frame.add(name)
        clip.reader.close()
        clip.audio.reader.close_proc()
    except Exception as e:
        print(f"Error processing {video_path}: {e}")

    for name in results:
        results[name] = sorted(set(results[name]))
    return results

def scan_and_save_all(known_people, video_dir, output_dir, progress_callback=None):
    """
    Scans videos for known people and saves merged timestamp results
    just like your CLI script.

    If progress_callback is provided, it will be called as:
        progress_callback(current_index, total_videos, current_video_name)
    """
    video_files = [f for f in os.listdir(video_dir) if f.lower().endswith(".mp4")]
    total_videos = len(video_files)
    all_results = {name: {} for name, _ in known_people}

    for idx, filename in enumerate(video_files, start=1):
        video_path = os.path.join(video_dir, filename)
        video_results = find_person_timestamps_multi(video_path, known_people)
        for name, timestamps in video_results.items():
            if timestamps:
                if filename not in all_results[name]:
                    all_results[name][filename] = []
                all_results[name][filename].extend(timestamps)

        # Report progress for each video processed
        if progress_callback:
            progress_callback(idx, total_videos, filename)

    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    for name in all_results:
        output_file = os.path.join(output_dir, f"{name}_videos.txt")
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

        saved_files.append(output_file)

    return saved_files
