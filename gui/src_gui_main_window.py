import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Dict
import os

class MainWindow:
    """Main application window with GUI controls."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Excel ERP Pre-Process")
        self.root.geometry("800x600")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize all UI components."""
        self._create_menu()
        self._create_file_frame()
        self._create_electrode_frame()
        self._create_progress_frame()
        
    def _create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Files", command=self.open_files)
        file_menu.add_command(label="Select Output Directory", command=self.select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Calculate Standard Variables", 
                             command=self.calculate_standard_vars)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        self.root.config(menu=menubar)
        
    def _create_file_frame(self):
        """Create the file management frame."""
        file_frame = ttk.LabelFrame(self.root, text="File Management", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Select Input Files", 
                  command=self.open_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Select Output Directory", 
                  command=self.select_output_dir).pack(side=tk.LEFT, padx=5)
        
    def _create_electrode_frame(self):
        """Create the electrode selection frame."""
        electrode_frame = ttk.LabelFrame(self.root, text="Electrode Selection", 
                                       padding=10)
        electrode_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Electrode group shortcuts
        groups_frame = ttk.Frame(electrode_frame)
        groups_frame.pack(fill=tk.X, pady=5)
        
        for group in ['Frontal', 'Temporal', 'Parietal', 'Occipital']:
            ttk.Button(groups_frame, text=group, 
                      command=lambda g=group: self.select_electrode_group(g)
                      ).pack(side=tk.LEFT, padx=2)
        
    def _create_progress_frame(self):
        """Create the progress tracking frame."""
        progress_frame = ttk.Frame(self.root, padding=10)
        progress_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
    def open_files(self):
        """Open file dialog for selecting input files."""
        filetypes = (
            ('CSV files', '*.csv'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )
        files = filedialog.askopenfilenames(
            title='Select input files',
            filetypes=filetypes
        )
        if files:
            self.process_files(files)
            
    def select_output_dir(self):
        """Open directory dialog for selecting output location."""
        directory = filedialog.askdirectory(
            title='Select output directory'
        )
        if directory:
            self.set_output_directory(directory)
            
    def run(self):
        """Start the main application loop."""
        self.root.mainloop()