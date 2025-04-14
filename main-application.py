import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
import threading
import time
from datetime import datetime

class ElectrodePanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.selected_electrodes = set()
        self.left_electrodes = set()
        self.right_electrodes = set()
        self.midline_electrodes = set()
        self.electrode_buttons = {}
        
        # Define 64-channel 10-20 EEG system electrodes
        self.all_electrodes = [
            'Fp1', 'Fpz', 'Fp2', 'AF7', 'AF3', 'AFz', 'AF4', 'AF8',
            'F7', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 'F8',
            'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8',
            'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
            'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8',
            'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8',
            'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'O1', 'Oz', 'O2'
        ]
        
        # Categorize electrodes
        for electrode in self.all_electrodes:
            if electrode.endswith('z') or 'z' in electrode:
                self.midline_electrodes.add(electrode)
            elif any(c.isdigit() and int(c) % 2 == 1 for c in electrode):
                self.left_electrodes.add(electrode)
            elif any(c.isdigit() and int(c) % 2 == 0 for c in electrode):
                self.right_electrodes.add(electrode)
        
        # Create predefined groups
        self.electrode_groups = {
            "All": self.all_electrodes,
            "Left Hemisphere": list(self.left_electrodes),
            "Right Hemisphere": list(self.right_electrodes),
            "Midline": list(self.midline_electrodes),
            "Frontal": [e for e in self.all_electrodes if e.startswith('F') or e.startswith('Fp') or e.startswith('AF')],
            "Central": [e for e in self.all_electrodes if e.startswith('C') or e.startswith('FC') or e.startswith('CP')],
            "Temporal": [e for e in self.all_electrodes if e.startswith('T') or e.startswith('FT') or e.startswith('TP')],
            "Parietal": [e for e in self.all_electrodes if e.startswith('P')],
            "Occipital": [e for e in self.all_electrodes if e.startswith('O') or e.startswith('PO')]
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Electrode selection panel
        electrode_frame = tk.LabelFrame(self, text="Electrode Selection")
        electrode_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Group selection
        group_frame = tk.Frame(electrode_frame)
        group_frame.pack(fill=tk.X, padx=5, pady=5)
        
        group_label = tk.Label(group_frame, text="Predefined Groups:")
        group_label.pack(side=tk.LEFT, padx=5)
        
        for group_name in self.electrode_groups:
            btn = tk.Button(group_frame, text=group_name, 
                           command=lambda g=group_name: self.select_electrode_group(g))
            btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = tk.Button(group_frame, text="Clear Selection", command=self.clear_selection)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Electrode grid display
        self.electrode_canvas = tk.Canvas(electrode_frame, width=500, height=400, bg="white")
        self.electrode_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create electrode buttons in a layout resembling the 10-20 system
        self._create_electrode_layout()
    
    def _create_electrode_layout(self):
        # This is a simplified layout. In a real application, you would position
        # electrodes according to their actual positions on the scalp.
        cols = 8
        row_spacing = 40
        col_spacing = 60
        
        # Create a rough layout of electrodes
        for i, electrode in enumerate(self.all_electrodes):
            row = i // cols
            col = i % cols
            x = 50 + col * col_spacing
            y = 50 + row * row_spacing
            
            # Create electrode button
            btn = self.electrode_canvas.create_oval(x-15, y-15, x+15, y+15, fill="red", tags=electrode)
            self.electrode_canvas.create_text(x, y, text=electrode, tags=f"text_{electrode}")
            
            # Bind click event
            self.electrode_canvas.tag_bind(electrode, "<Button-1>", lambda event, e=electrode: self.toggle_electrode(e))
            self.electrode_canvas.tag_bind(f"text_{electrode}", "<Button-1>", lambda event, e=electrode: self.toggle_electrode(e))
    
    def toggle_electrode(self, electrode):
        if electrode in self.selected_electrodes:
            self.selected_electrodes.remove(electrode)
            color = "red"
        else:
            self.selected_electrodes.add(electrode)
            if electrode in self.left_electrodes:
                color = "green"
            elif electrode in self.right_electrodes:
                color = "blue"
            else:  # midline
                color = "purple"
        
        # Update color
        self.electrode_canvas.itemconfig(electrode, fill=color)
    
    def select_electrode_group(self, group_name):
        electrodes = self.electrode_groups[group_name]
        for electrode in self.all_electrodes:
            if electrode in electrodes:
                if electrode not in self.selected_electrodes:
                    self.selected_electrodes.add(electrode)
                    if electrode in self.left_electrodes:
                        color = "green"
                    elif electrode in self.right_electrodes:
                        color = "blue"
                    else:  # midline
                        color = "purple"
                    self.electrode_canvas.itemconfig(electrode, fill=color)
            else:
                if electrode in self.selected_electrodes:
                    self.selected_electrodes.remove(electrode)
                    self.electrode_canvas.itemconfig(electrode, fill="red")
    
    def clear_selection(self):
        self.selected_electrodes.clear()
        for electrode in self.all_electrodes:
            self.electrode_canvas.itemconfig(electrode, fill="red")
    
    def get_selected_electrodes(self):
        return list(self.selected_electrodes)

class FileProcessor:
    def __init__(self):
        self.input_dir = ""
        self.output_dir = ""
        self.backup_dir = ""
        self.files_to_process = []
        self.latency_cols = []
        self.amplitude_cols = []
        self.selected_electrodes = []
        self.custom_variables = []
    
    def set_directories(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.backup_dir = os.path.join(output_dir, "_backup")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def scan_files(self):
        """Scan the input directory for CSV and TXT files"""
        self.files_to_process = []
        if not self.input_dir:
            return []
        
        for file in os.listdir(self.input_dir):
            if file.lower().endswith(('.csv', '.txt')):
                self.files_to_process.append(os.path.join(self.input_dir, file))
        
        return self.files_to_process
    
    def backup_file(self, file_path):
        """Create a backup of the original file"""
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, file_name)
        try:
            with open(file_path, 'r') as source:
                with open(backup_path, 'w') as target:
                    target.write(source.read())
            return True
        except Exception as e:
            print(f"Error backing up file: {e}")
            return False
    
    def process_file(self, file_path, selected_electrodes):
        """Process a single file with the selected electrodes"""
        # Load the file
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # .txt
            df = pd.read_csv(file_path, delimiter='\t')
        
        # Create backup
        self.backup_file(file_path)
        
        # Identify electrode columns (in real application, we'd have more sophisticated detection)
        # For this example, we'll assume electrode names are in column headers
        electrode_cols = {}
        for electrode in selected_electrodes:
            # Look for latency columns
            latency_col = next((col for col in df.columns if electrode in col and 'latency' in col.lower()), None)
            if latency_col:
                if 'latency' not in electrode_cols:
                    electrode_cols['latency'] = {}
                electrode_cols['latency'][electrode] = latency_col
            
            # Look for amplitude columns
            amplitude_col = next((col for col in df.columns if electrode in col and 'amplitude' in col.lower()), None)
            if amplitude_col:
                if 'amplitude' not in electrode_cols:
                    electrode_cols['amplitude'] = {}
                electrode_cols['amplitude'][electrode] = amplitude_col
        
        # Calculate standard variables
        if 'latency' in electrode_cols:
            # Left hemisphere latency average
            left_electrodes = [e for e in selected_electrodes if e in self.left_electrodes]
            left_latency_cols = [electrode_cols['latency'][e] for e in left_electrodes if e in electrode_cols['latency']]
            if left_latency_cols:
                df['Avg_Left_Latency'] = df[left_latency_cols].mean(axis=1)
            
            # Right hemisphere latency average
            right_electrodes = [e for e in selected_electrodes if e in self.right_electrodes]
            right_latency_cols = [electrode_cols['latency'][e] for e in right_electrodes if e in electrode_cols['latency']]
            if right_latency_cols:
                df['Avg_Right_Latency'] = df[right_latency_cols].mean(axis=1)
        
        if 'amplitude' in electrode_cols:
            # Left hemisphere amplitude average
            left_amplitude_cols = [electrode_cols['amplitude'][e] for e in left_electrodes if e in electrode_cols['amplitude']]
            if left_amplitude_cols:
                df['Avg_Left_Amplitude'] = df[left_amplitude_cols].mean(axis=1)
            
            # Right hemisphere amplitude average
            right_amplitude_cols = [electrode_cols['amplitude'][e] for e in right_electrodes if e in electrode_cols['amplitude']]
            if right_amplitude_cols:
                df['Avg_Right_Amplitude'] = df[right_amplitude_cols].mean(axis=1)
        
        # Save processed file
        file_name = os.path.basename(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        output_path = os.path.join(self.output_dir, f"{file_base}_edited.xlsx")
        df.to_excel(output_path, index=False)
        
        return output_path, electrode_cols
    
    def batch_process(self, selected_electrodes, callback=None):
        """Process all files in the input directory"""
        self.selected_electrodes = selected_electrodes
        
        results = []
        for i, file_path in enumerate(self.files_to_process):
            output_path, electrode_cols = self.process_file(file_path, selected_electrodes)
            results.append({
                'input': file_path,
                'output': output_path,
                'electrodes': electrode_cols
            })
            
            if callback:
                progress = (i + 1) / len(self.files_to_process) * 100
                callback(progress, f"Processed {os.path.basename(file_path)}")
        
        # Generate report
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results):
        """Generate a summary report of the processing"""
        report_path = os.path.join(self.output_dir, f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(report_path, 'w') as f:
            f.write("EEG ERP Processing Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input Directory: {self.input_dir}\n")
            f.write(f"Output Directory: {self.output_dir}\n")
            f.write(f"Files Processed: {len(results)}\n\n")
            
            f.write("Selected Electrodes:\n")
            f.write(", ".join(self.selected_electrodes) + "\n\n")
            
            f.write("File Processing Details:\n")
            f.write("-" * 50 + "\n")
            
            for result in results:
                f.write(f"Input: {os.path.basename(result['input'])}\n")
                f.write(f"Output: {os.path.basename(result['output'])}\n")
                
                f.write("Detected Electrodes:\n")
                for measure, electrodes in result['electrodes'].items():
                    f.write(f"  {measure.capitalize()}:\n")
                    for electrode, column in electrodes.items():
                        f.write(f"    {electrode}: {column}\n")
                
                f.write("\n")
            
            f.write("=" * 50 + "\n")
            f.write("End of Report\n")
        
        return report_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EEG ERP Pre-Processor")
        self.geometry("900x700")
        
        self.processor = FileProcessor()
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dir_frame, text="Input Directory:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.input_dir_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_input_dir).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(dir_frame, text="Output Directory:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(dir_frame, text="Scan Files", command=self.scan_files).grid(row=2, column=1, padx=5, pady=5)
        
        # File list
        file_frame = ttk.LabelFrame(main_frame, text="Files to Process")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(file_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(file_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Electrode selection panel
        self.electrode_panel = ElectrodePanel(main_frame)
        self.electrode_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Processing buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Process Files", command=self.process_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.quit).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_frame = ttk.LabelFrame(main_frame, text="Processing Progress")
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar()
        ttk.Label(self.progress_frame, textvariable=self.status_var).pack(padx=5, pady=2)
    
    def browse_input_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir_var.set(directory)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def scan_files(self):
        input_dir = self.input_dir_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories.")
            return
        
        self.processor.set_directories(input_dir, output_dir)
        files = self.processor.scan_files()
        
        self.file_listbox.delete(0, tk.END)
        for file in files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
        
        messagebox.showinfo("Files Found", f"Found {len(files)} files to process.")
    
    def update_progress(self, progress, status):
        self.progress_var.set(progress)
        self.status_var.set(status)
        self.update_idletasks()
    
    def process_files(self):
        selected_electrodes = self.electrode_panel.get_selected_electrodes()
        if not selected_electrodes:
            messagebox.showerror("Error", "Please select at least one electrode.")
            return
        
        if not self.processor.files_to_process:
            messagebox.showerror("Error", "No files to process. Please scan for files first.")
            return
        
        # Start processing in a separate thread to avoid UI freezing
        self.status_var.set("Starting processing...")
        self.progress_var.set(0)
        
        def processing_thread():
            try:
                results = self.processor.batch_process(selected_electrodes, self.update_progress)
                self.after(100, lambda: self.processing_complete(results))
            except Exception as e:
                self.after(100, lambda: messagebox.showerror("Processing Error", str(e)))
        
        threading.Thread(target=processing_thread).start()
    
    def processing_complete(self, results):
        messagebox.showinfo("Processing Complete", 
                           f"Successfully processed {len(results)} files.\n"
                           f"Results saved to {self.output_dir_var.get()}")
        self.status_var.set("Processing complete")

if __name__ == "__main__":
    app = App()
    app.mainloop()
