"""
Graphic Score Analyzer and OSC Transmitter by Leslie Garcia _ 2024 
----------------------------------------

This script analyzes graphical scores or images and converts visual information into OSC (Open Sound Control) data
for real-time musical/sonic interpretation. It provides two main modes of analysis:

1. Static Analysis (Press 'a'):
   - Detects keypoints using SIFT (Scale-Invariant Feature Transform)
   - Analyzes contrast, object count, and proximity of elements
   - Transmits object count via OSC to port 8000

2. Dynamic Scanning (Press 'b'):
   - Performs a left-to-right scan of the image
   - Analyzes features in real-time as the scan progresses
   - Transmits continuous data about object count and size metrics
   - Visual feedback shows scanning progress and analyzed areas

Controls:
- Press 'a' for static analysis
- Press 'b' for dynamic scanning
- Press 'r' to reverse scanning direction
- Press 'f' to forward scanning direction
- Press 'n' for next page
- Press 'p' for previous page
- Press 'ESC' to exit

Usage:
    python graph_score.py

Requirements:
    - OpenCV (cv2)
    - numpy
    - python-osc
    - tkinter
"""

import cv2
import numpy as np
from pythonosc import udp_client
import argparse
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os

#todo 
# add L loop functionality to play the score
# add R to reverse scan

class ScoreManager:
    def __init__(self):
        self.scores = []  # List of (path, duration) tuples
        self.current_index = 0
        self.analyzed_pages = {}  # Dictionary to store analyzed page data
        self.auto_scanning = False  # Flag for auto-scanning mode
        
    def add_score(self, path, duration):
        self.scores.append((path, float(duration)))
        
    def remove_score(self, index):
        if 0 <= index < len(self.scores):
            self.scores.pop(index)
            # Clean up analyzed data if it exists
            if index in self.analyzed_pages:
                del self.analyzed_pages[index]
            
    def get_current_score(self):
        if not self.scores:
            return None, None
        return self.scores[self.current_index]
    
    def get_total_duration(self):
        return sum(duration for _, duration in self.scores)
    
    def store_analysis(self, index, analysis_data):
        self.analyzed_pages[index] = analysis_data
    
    def get_analysis(self, index):
        return self.analyzed_pages.get(index)
    
    def has_next_score(self):
        return len(self.scores) > 1 and self.current_index < len(self.scores) - 1
    
    def analyze_all_pages(self):
        """Analyze all pages in the score set"""
        for i in range(len(self.scores)):
            path, _ = self.scores[i]
            print(f"\nAnalyzing page {i + 1}/{len(self.scores)}: {os.path.basename(path)}")
            
            # Load and resize image
            temp_image = cv2.resize(cv2.imread(path), (1424, 848))
            temp_display = temp_image.copy()
            
            # Perform analysis
            c, oc, _, p, _, _, _, _ = analyze_image(temp_image, temp_display)
            
            # Store analysis data
            analysis_data = {
                'keypoints_image': temp_display.copy(),
                'contrast': c,
                'object_count': oc,
                'proximity': p,
                'original_image': temp_image.copy()  # Store original image for scanning
            }
            self.store_analysis(i, analysis_data)
            print(f"✓ Found {oc} objects")
        print("\nAnalysis complete! All pages are ready.")
    
    def next_score(self):
        if self.scores:
            self.current_index = (self.current_index + 1) % len(self.scores)
            return self.get_current_score()
        return None, None
    
    def previous_score(self):
        if self.scores:
            self.current_index = (self.current_index - 1) % len(self.scores)
            return self.get_current_score()
        return None, None

class ScoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphic Score Manager")
        self.score_manager = ScoreManager()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create score list
        self.score_frame = ttk.LabelFrame(self.main_frame, text="Scores", padding="5")
        self.score_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Score listbox with scrollbar
        self.score_listbox = tk.Listbox(self.score_frame, width=50, height=10)
        scrollbar = ttk.Scrollbar(self.score_frame, orient="vertical", command=self.score_listbox.yview)
        self.score_listbox.configure(yscrollcommand=scrollbar.set)
        self.score_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        
        # Bind listbox selection event
        self.score_listbox.bind('<<ListboxSelect>>', self.on_select_score)
        
        # Total duration label
        self.duration_label = ttk.Label(self.score_frame, text="Total Duration: 0s")
        self.duration_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Current score label
        self.current_score_label = ttk.Label(self.score_frame, text="No score selected")
        self.current_score_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Button frame
        self.button_frame = ttk.Frame(self.score_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Add score buttons with state handling
        self.add_button = ttk.Button(self.button_frame, text="Add Score", command=self.add_score)
        self.add_button.grid(row=0, column=0, padx=5)
        
        self.remove_button = ttk.Button(self.button_frame, text="Remove Score", 
                                      command=self.remove_score, state='disabled')
        self.remove_button.grid(row=0, column=1, padx=5)
        
        # Control buttons frame
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="5")
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Analysis buttons
        self.analyze_button = ttk.Button(self.control_frame, text="Start Analysis", 
                                       command=self.start_analysis, state='disabled')
        self.analyze_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.auto_play_button = ttk.Button(self.control_frame, text="Start Auto Play", 
                                         command=self.start_auto_play, state='disabled')
        self.auto_play_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready - Add scores to begin")
        self.status_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.score_frame.columnconfigure(0, weight=1)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize analysis window reference
        self.analysis_window = None
        
    def on_select_score(self, event):
        selection = self.score_listbox.curselection()
        if selection:
            path, duration = self.score_manager.scores[selection[0]]
            self.current_score_label.config(text=f"Selected: {os.path.basename(path)}")
            self.remove_button.config(state='normal')
            self.analyze_button.config(state='normal')
            self.auto_play_button.config(state='normal')
        else:
            self.current_score_label.config(text="No score selected")
            self.remove_button.config(state='disabled')
        
    def update_duration_label(self):
        total_duration = self.score_manager.get_total_duration()
        minutes = int(total_duration // 60)
        seconds = total_duration % 60
        self.duration_label.config(text=f"Total Duration: {minutes}m {seconds:.1f}s")
        
    def add_score(self):
        self.status_label.config(text="Selecting file...")
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if file_path:
            duration_dialog = tk.Toplevel(self.root)
            duration_dialog.title("Set Duration")
            duration_dialog.geometry("200x100")
            duration_dialog.transient(self.root)
            duration_dialog.grab_set()
            
            ttk.Label(duration_dialog, text="Duration (seconds):").pack(pady=5)
            duration_var = tk.StringVar(value="30")
            duration_entry = ttk.Entry(duration_dialog, textvariable=duration_var)
            duration_entry.pack(pady=5)
            
            def confirm():
                try:
                    duration = float(duration_var.get())
                    self.score_manager.add_score(file_path, duration)
                    self.update_score_list()
                    self.update_duration_label()
                    self.status_label.config(text=f"Added: {os.path.basename(file_path)}")
                    self.analyze_button.config(state='normal')
                    self.auto_play_button.config(state='normal')
                    duration_dialog.destroy()
                except ValueError:
                    tk.messagebox.showerror("Error", "Please enter a valid number")
            
            ttk.Button(duration_dialog, text="OK", command=confirm).pack(pady=5)
            
            # Center dialog
            duration_dialog.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        else:
            self.status_label.config(text="Ready")
    
    def remove_score(self):
        selection = self.score_listbox.curselection()
        if selection:
            self.score_manager.remove_score(selection[0])
            self.update_score_list()
            self.status_label.config(text="Score removed")
            if not self.score_manager.scores:
                self.analyze_button.config(state='disabled')
                self.auto_play_button.config(state='disabled')
                self.remove_button.config(state='disabled')
                self.current_score_label.config(text="No score selected")
            
    def update_score_list(self):
        self.score_listbox.delete(0, tk.END)
        for path, duration in self.score_manager.scores:
            self.score_listbox.insert(tk.END, f"{os.path.basename(path)} ({duration}s)")
        if self.score_manager.scores:
            self.score_listbox.selection_set(0)
            self.on_select_score(None)
            
    def start_analysis(self):
        if not self.score_manager.scores:
            tk.messagebox.showerror("Error", "Please add at least one score")
            return
        
        self.status_label.config(text="Analysis in progress...")
        self.disable_buttons()
        self.root.withdraw()
        self.analyze_scores()
        
    def start_auto_play(self):
        if not self.score_manager.scores:
            tk.messagebox.showerror("Error", "Please add at least one score")
            return
        
        self.status_label.config(text="Auto play in progress...")
        self.disable_buttons()
        self.root.withdraw()
        self.analyze_scores(auto_play=True)
        
    def analyze_scores(self, auto_play=False):
        path, duration = self.score_manager.get_current_score()
        if path and duration:
            main(path, duration, self.score_manager, auto_play)
        self.root.deiconify()
        self.enable_buttons()
        self.status_label.config(text="Ready")
        
    def disable_buttons(self):
        self.add_button.config(state='disabled')
        self.remove_button.config(state='disabled')
        self.analyze_button.config(state='disabled')
        self.auto_play_button.config(state='disabled')
        
    def enable_buttons(self):
        self.add_button.config(state='normal')
        if self.score_listbox.curselection():
            self.remove_button.config(state='normal')
            self.analyze_button.config(state='normal')
            self.auto_play_button.config(state='normal')
            
    def on_closing(self):
        if self.analysis_window:
            cv2.destroyAllWindows()
        self.root.destroy()

def analyze_image(image, display_image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    
    # Detect keypoints and compute descriptors
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    
    # Draw keypoints on the display image with green and blue colors
    for i, kp in enumerate(keypoints):
        color = (0, 255, 0) if i % 2 == 0 else (0, 0, 0)  # Alternate between green and blue
        cv2.drawKeypoints(display_image, [kp], display_image, color, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    # Analyze keypoints
    contrast = gray.std()
    object_count = len(keypoints)
    sizes = [kp.size for kp in keypoints]
    
    # Calculate size metrics
    min_size = min(sizes) if sizes else 0
    avg_size = np.mean(sizes) if sizes else 0
    max_size = max(sizes) if sizes else 0
    
    # Calculate proximity as the average distance of keypoints from the center
    center_x, center_y = gray.shape[1] // 2, gray.shape[0] // 2
    proximity = np.mean([np.sqrt((kp.pt[0] - center_x) ** 2 + (kp.pt[1] - center_y) ** 2) for kp in keypoints])
    
    # Calculate positions for OSC transmission
    positions = [(kp.pt[0] / gray.shape[1], kp.pt[1] / gray.shape[0]) for kp in keypoints]
    
    return contrast, object_count, sizes, proximity, min_size, avg_size, max_size, positions

def add_info_box(image, contrast, object_count, proximity, duration, current_page=0, total_pages=1, total_duration=None, scan_data=None, scan_object_count=None):
    # Create a black rectangle in the lower right corner
    h, w = image.shape[:2]
    start_x = w - 140  # 140 pixels from right
    start_y = h - 140  # Increased height for additional info
    image[start_y:h, start_x:w] = (0, 0, 0)  # Black rectangle
    
    # Add text with white color
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    color = (255, 255, 255)  # White color
    thickness = 1
    
    # Ensure we have valid values
    current_page = 0 if current_page is None else current_page
    total_pages = 1 if total_pages is None else total_pages
    total_duration = duration if total_duration is None else total_duration
    
    if scan_data is not None:
        # Calculate metrics for the scanned area
        scan_array = np.array(scan_data)
        scan_mean = np.mean(scan_array)
        scan_std = np.std(scan_array)
        scan_max = np.max(scan_array)
        
        texts = [
            f"Page: {current_page + 1}/{total_pages}",
            f"Total Time: {total_duration:.1f}s",
            f"Duration: {duration:.1f}s",
            f"Total Objects: {object_count}",
            f"Scan Objects: {scan_object_count}",
            f"Scan Mean: {scan_mean:.1f}"
        ]
    else:
        texts = [
            f"Page: {current_page + 1}/{total_pages}",
            f"Total Time: {total_duration:.1f}s",
            f"Duration: {duration:.1f}s",
            f"Contrast: {contrast:.1f}",
            f"Objects: {object_count}",
            f"Proximity: {proximity:.1f}"
        ]
    
    # Position and draw each line of text
    for i, text in enumerate(texts):
        y_position = start_y + 20 + (i * 20)
        cv2.putText(image, text, (start_x + 5, y_position), 
                   font, font_scale, color, thickness)

def main(image_path, duration, score_manager=None, auto_play=False):
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return
    
    # Resize image to 1424 x 848
    image = cv2.resize(image, (1424, 848))
    display_image = image.copy()
    client = udp_client.SimpleUDPClient("127.0.0.1", 8000)
    
    # Initialize scanning direction and position
    reverse_scan = False
    current_position = 0
    keypoints_image = None
    
    # Get page information
    if score_manager:
        current_page = score_manager.current_index
        total_pages = len(score_manager.scores)
        total_duration = score_manager.get_total_duration()
        
        # Load existing analysis if available
        existing_analysis = score_manager.get_analysis(current_page)
        if existing_analysis:
            keypoints_image = existing_analysis['keypoints_image'].copy()
            image = existing_analysis['original_image'].copy()
            contrast = existing_analysis['contrast']
            object_count = existing_analysis['object_count']
            proximity = existing_analysis['proximity']
            display_image = keypoints_image.copy()
        else:
            # Perform initial analysis if not available
            contrast, object_count, _, proximity, _, _, _, _ = analyze_image(image, display_image)
            keypoints_image = display_image.copy()
    else:
        current_page = 0
        total_pages = 1
        total_duration = duration
        contrast, object_count, _, proximity, _, _, _, _ = analyze_image(image, display_image)
        keypoints_image = display_image.copy()
    
    # Store analysis data if not already stored
    if score_manager and score_manager.get_analysis(current_page) is None:
        analysis_data = {
            'keypoints_image': keypoints_image.copy(),
            'original_image': image.copy(),
            'contrast': contrast,
            'object_count': object_count,
            'proximity': proximity
        }
        score_manager.store_analysis(current_page, analysis_data)
    
    start_time = cv2.getTickCount()
    page_duration = duration * 1000  # Convert to milliseconds
    
    while True:
        # Use analyzed image if available
        if keypoints_image is not None:
            display_image = keypoints_image.copy()
            
        add_info_box(display_image, contrast, object_count, proximity, duration,
                    current_page, total_pages, total_duration)
        
        cv2.imshow("Image with Analysis", display_image)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('a'):
            if score_manager:
                print("\nStarting analysis of all pages...")
                score_manager.analyze_all_pages()
                
                # Update current page analysis after analyzing all
                existing_analysis = score_manager.get_analysis(current_page)
                if existing_analysis:
                    keypoints_image = existing_analysis['keypoints_image'].copy()
                    image = existing_analysis['original_image'].copy()
                    contrast = existing_analysis['contrast']
                    object_count = existing_analysis['object_count']
                    proximity = existing_analysis['proximity']
                    display_image = keypoints_image.copy()
                    
                    # Send only the object count as an OSC message
                    client.send_message("/image/object_count", object_count)
                    print(f"Sent OSC: /image/object_count {object_count}")
                    
                    # Show updated analysis
                    add_info_box(display_image, contrast, object_count, proximity, duration,
                               current_page, total_pages, total_duration)
                    cv2.imshow("Image with Analysis", display_image)
            else:
                # Single page analysis
                display_image = image.copy()
                contrast, object_count, sizes, proximity, min_size, avg_size, max_size, positions = analyze_image(image, display_image)
                keypoints_image = display_image.copy()
                
                # Send only the object count as an OSC message
                client.send_message("/image/object_count", object_count)
                print(f"Sent OSC: /image/object_count {object_count}")
            
            print(f"Current page has {object_count} objects")
        
        elif key == ord('n') and score_manager:
            path, duration = score_manager.next_score()
            if path:
                return main(path, duration, score_manager, auto_play)
        
        elif key == ord('p') and score_manager:
            path, duration = score_manager.previous_score()
            if path:
                return main(path, duration, score_manager, auto_play)
        
        elif key == ord('b'):
            # Ensure we have analysis before scanning
            if keypoints_image is None:
                if score_manager and score_manager.get_analysis(current_page):
                    analysis = score_manager.get_analysis(current_page)
                    keypoints_image = analysis['keypoints_image'].copy()
                    contrast = analysis['contrast']
                    object_count = analysis['object_count']
                    proximity = analysis['proximity']
                else:
                    keypoints_image = image.copy()
                    contrast, object_count, sizes, proximity, min_size, avg_size, max_size, positions = analyze_image(image, keypoints_image)
            
            scanning = True
            while scanning:
                # Perform scanning for current page
                scan_width = 60
                scan_height = 848
                num_steps = (image.shape[1] - scan_width) + 1
                step_duration = duration / num_steps
                
                current_position = 0 if not reverse_scan else num_steps - 1
                
                while scanning and 0 <= current_position < num_steps:
                    key = cv2.waitKey(int(step_duration * 1000)) & 0xFF
                    
                    if key == ord('r'):
                        reverse_scan = True
                    elif key == ord('f'):
                        reverse_scan = False
                    elif key == 27:  # ESC key
                        scanning = False
                        break
                    
                    start_x = current_position
                    end_x = start_x + scan_width
                    
                    display_image = keypoints_image.copy()
                    scan_area = display_image[:, start_x:end_x].copy()
                    scan_area = cv2.bitwise_not(scan_area)
                    
                    _, scan_object_count, scan_sizes, _, min_size, avg_size, max_size, positions = analyze_image(
                        image[:, start_x:end_x], scan_area)
                    
                    display_image[:, start_x:end_x] = scan_area
                    cv2.rectangle(display_image, (start_x, 0), (end_x, scan_height), (0, 255, 0), 2)
                    
                    # Send OSC messages for dynamic scanning
                    client.send_message("/image/scan_object_count", scan_object_count)
                    client.send_message("/image/scan_min_size", min_size)
                    client.send_message("/image/scan_avg_size", avg_size)
                    client.send_message("/image/scan_max_size", max_size)
                    
                    # Print OSC messages
                    print(f"Sent OSC: /image/scan_object_count {scan_object_count}")
                    print(f"Sent OSC: /image/scan_min_size {min_size}")
                    print(f"Sent OSC: /image/scan_avg_size {avg_size}")
                    print(f"Sent OSC: /image/scan_max_size {max_size}")
                    
                    add_info_box(display_image, contrast, object_count, proximity, duration,
                               current_page, total_pages, total_duration,
                               scan_data=scan_area.flatten(), scan_object_count=scan_object_count)
                    
                    cv2.imshow("Image with Analysis", display_image)
                    
                    if reverse_scan:
                        current_position -= 1
                    else:
                        current_position += 1
                
                # Check if we should move to next page
                if scanning and score_manager and score_manager.has_next_score():
                    path, duration = score_manager.next_score()
                    if path:
                        print(f"Moving to next page: {score_manager.current_index + 1}/{total_pages}")
                        return main(path, duration, score_manager, auto_play)
                else:
                    scanning = False
        
        elif key == 27:  # ESC key to exit
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreGUI(root)
    root.mainloop()