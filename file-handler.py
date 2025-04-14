import os
import shutil
import pandas as pd
import datetime
import re
from typing import List, Dict, Tuple, Optional, Set


class FileHandler:
    """
    Handles file operations for the EEG ERP Data Processor application:
    - Loading and saving files in different formats
    - Converting between file formats
    - Creating backups
    - Managing batch file processing
    - Generating processing reports
    """
    
    def __init__(self):
        """Initialize FileHandler with default values"""
        self.input_folder = ""
        self.output_folder = ""
        self.backup_folder = ""
        self.supported_extensions = ['.csv', '.txt', '.xlsx', '.xls']
        self.processing_log = []
    
    def set_input_folder(self, folder_path: str) -> None:
        """
        Set the input folder for file operations
        
        Args:
            folder_path: Path to the input folder
        """
        if not os.path.isdir(folder_path):
            raise ValueError(f"Input folder does not exist: {folder_path}")
        
        self.input_folder = folder_path
    
    def set_output_folder(self, folder_path: str) -> None:
        """
        Set the output folder for file operations
        
        Args:
            folder_path: Path to the output folder
        """
        # Create the folder if it doesn't exist
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        
        self.output_folder = folder_path
        
        # Create backup folder inside output folder
        self.backup_folder = os.path.join(folder_path, "_backup")
        if not os.path.isdir(self.backup_folder):
            os.makedirs(self.backup_folder)
    
    def get_file_list(self) -> List[str]:
        """
        Get list of supported files in the input folder
        
        Returns:
            List of filenames with supported extensions
        """
        if not self.input_folder or not os.path.isdir(self.input_folder):
            return []
        
        file_list = []
        for file in os.listdir(self.input_folder):
            if any(file.lower().endswith(ext) for ext in self.supported_extensions):
                file_list.append(file)
        
        return sorted(file_list)
    
    def load_file(self, file_name: str) -> pd.DataFrame:
        """
        Load a file from the input folder
        
        Args:
            file_name: Name of the file to load
            
        Returns:
            DataFrame containing the file data
        """
        if not self.input_folder:
            raise ValueError("Input folder not set")
        
        file_path = os.path.join(self.input_folder, file_name)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                return pd.read_csv(file_path)
            elif file_ext == '.txt':
                # Try to detect delimiter
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    if '\t' in first_line:
                        delimiter = '\t'
                    elif ',' in first_line:
                        delimiter = ','
                    else:
                        delimiter = None  # Let pandas try to figure it out
                return pd.read_csv(file_path, delimiter=delimiter)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            raise IOError(f"Error loading file {file_name}: {str(e)}")
    
    def save_file(self, data: pd.DataFrame, file_name: str) -> str:
        """
        Save data to a file in the output folder
        
        Args:
            data: DataFrame to save
            file_name: Name of the file to save
            
        Returns:
            Path to the saved file
        """
        if not self.output_folder:
            raise ValueError("Output folder not set")
        
        # Ensure file has xlsx extension
        base_name, ext = os.path.splitext(file_name)
        if not base_name.endswith('_edited'):
            base_name = f"{base_name}_edited"
        
        output_file = f"{base_name}.xlsx"
        output_path = os.path.join(self.output_folder, output_file)
        
        try:
            data.to_excel(output_path, index=False)
            self.processing_log.append(f"Saved: {output_file}")
            return output_path
        except Exception as e:
            error_msg = f"Error saving file {output_file}: {str(e)}"
            self.processing_log.append(error_msg)
            raise IOError(error_msg)
    
    def backup_file(self, file_name: str) -> str:
        """
        Create a backup of the file in the backup folder
        
        Args:
            file_name: Name of the file to backup
            
        Returns:
            Path to the backup file
        """
        if not self.input_folder:
            raise ValueError("Input folder not set")
        
        if not self.backup_folder:
            raise ValueError("Backup folder not set")
        
        source_path = os.path.join(self.input_folder, file_name)
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"File not found: {source_path}")
        
        # Add timestamp to backup filename to avoid overwrites
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, ext = os.path.splitext(file_name)
        backup_file = f"{base_name}_{timestamp}{ext}"
        backup_path = os.path.join(self.backup_folder, backup_file)
        
        try:
            shutil.copy2(source_path, backup_path)
            self.processing_log.append(f"Backup created: {backup_file}")
            return backup_path
        except Exception as e:
            error_msg = f"Error creating backup for {file_name}: {str(e)}"
            self.processing_log.append(error_msg)
            raise IOError(error_msg)
    
    def process_file(self, file_name: str, processor_func) -> Tuple[str, str]:
        """
        Process a file using the provided processor function
        
        Args:
            file_name: Name of the file to process
            processor_func: Function that takes a DataFrame and returns a processed DataFrame
            
        Returns:
            Tuple of (input_path, output_path)
        """
        if not self.input_folder or not self.output_folder:
            raise ValueError("Input and output folders must be set")
        
        input_path = os.path.join(self.input_folder, file_name)
        
        # Create backup
        self.backup_file(file_name)
        
        # Load the file
        data = self.load_file(file_name)
        
        # Process the data
        processed_data = processor_func(data)
        
        # Save the processed data
        output_path = self.save_file(processed_data, file_name)
        
        return input_path, output_path
    
    def batch_process(self, file_list: List[str], processor_func, progress_callback=None) -> List[Tuple[str, str]]:
        """
        Process multiple files in batch
        
        Args:
            file_list: List of file names to process
            processor_func: Function that takes a DataFrame and returns a processed DataFrame
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of (input_path, output_path) tuples for each processed file
        """
        results = []
        total_files = len(file_list)
        
        for i, file_name in enumerate(file_list):
            try:
                # Process the file
                input_path, output_path = self.process_file(file_name, processor_func)
                results.append((input_path, output_path))
                
                # Update progress if callback provided
                if progress_callback:
                    progress = (i + 1) / total_files * 100
                    progress_callback(progress, file_name)
                
            except Exception as e:
                error_msg = f"Error processing {file_name}: {str(e)}"
                self.processing_log.append(error_msg)
                # Continue processing other files
        
        return results
    
    def generate_report(self, processed_files: List[str], electrode_info: Dict = None) -> str:
        """
        Generate a processing report
        
        Args:
            processed_files: List of processed file names
            electrode_info: Optional dictionary with electrode selection information
            
        Returns:
            Path to the generated report
        """
        if not self.output_folder:
            raise ValueError("Output folder not set")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"processing_report_{timestamp}.txt"
        report_path = os.path.join(self.output_folder, report_file)
        
        with open(report_path, 'w') as f:
            f.write("EEG ERP Data Processing Report\n")
            f.write("==============================\n\n")
            f.write(f"Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Processing Summary\n")
            f.write("-----------------\n")
            f.write(f"Total files processed: {len(processed_files)}\n")
            f.write(f"Input folder: {self.input_folder}\n")
            f.write(f"Output folder: {self.output_folder}\n\n")
            
            if electrode_info:
                f.write("Electrode Information\n")
                f.write("--------------------\n")
                if 'selected' in electrode_info:
                    f.write(f"Selected electrodes: {', '.join(sorted(electrode_info['selected']))}\n")
                if 'left' in electrode_info:
                    f.write(f"Left hemisphere: {', '.join(sorted(electrode_info['left']))}\n")
                if 'right' in electrode_info:
                    f.write(f"Right hemisphere: {', '.join(sorted(electrode_info['right']))}\n")
                if 'groups' in electrode_info:
                    f.write("Electrode groups:\n")
                    for group_name, electrodes in electrode_info['groups'].items():
                        f.write(f"  - {group_name}: {', '.join(sorted(electrodes))}\n")
                f.write("\n")
            
            f.write("Processed Files\n")
            f.write("--------------\n")
            for file_name in processed_files:
                f.write(f"- {file_name}\n")
            f.write("\n")
            
            f.write("Processing Log\n")
            f.write("-------------\n")
            for log_entry in self.processing_log:
                f.write(f"{log_entry}\n")
            
            f.write("\nEnd of Report\n")
        
        return report_path
    
    def clear_log(self) -> None:
        """Clear the processing log"""
        self.processing_log = []
    
    def convert_to_excel(self, file_path: str) -> str:
        """
        Convert a CSV or TXT file to Excel format
        
        Args:
            file_path: Path to the file to convert
            
        Returns:
            Path to the converted Excel file
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.xlsx', '.xls']:
            # Already an Excel file
            return file_path
        
        # Load the file
        if file_ext == '.csv':
            data = pd.read_csv(file_path)
        elif file_ext == '.txt':
            # Try to detect delimiter
            with open(file_path, 'r') as f:
                first_line = f.readline()
                if '\t' in first_line:
                    delimiter = '\t'
                elif ',' in first_line:
                    delimiter = ','
                else:
                    delimiter = None
            data = pd.read_csv(file_path, delimiter=delimiter)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Define the output path
        base_dir = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(base_dir, f"{base_name}.xlsx")
        
        # Save as Excel
        data.to_excel(output_path, index=False)
        
        return output_path
    
    def detect_electrode_columns(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Detect electrode-related columns in the data
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with 'latency' and 'amplitude' keys containing lists of column names
        """
        electrode_columns = {'latency': [], 'amplitude': []}
        
        # Common patterns for electrode column names
        latency_patterns = [
            r'^([A-Za-z]+\d*[zZ]?)[-_]?lat(ency)?$',    # Fz_lat, P3-latency
            r'^lat(ency)?[-_]?([A-Za-z]+\d*[zZ]?)$',    # lat_Fz, latency-P3
            r'^([A-Za-z]+\d*[zZ]?)[-_]?time$',          # Fz_time, P3-time
            r'^([A-Za-z]+\d*[zZ]?)[-_]?ms$'             # Fz_ms, P3-ms
        ]
        
        amplitude_patterns = [
            r'^([A-Za-z]+\d*[zZ]?)[-_]?amp(litude)?$',  # Fz_amp, P3-amplitude
            r'^amp(litude)?[-_]?([A-Za-z]+\d*[zZ]?)$',  # amp_Fz, amplitude-P3
            r'^([A-Za-z]+\d*[zZ]?)[-_]?volt$',          # Fz_volt, P3-volt
            r'^([A-Za-z]+\d*[zZ]?)[-_]?(μV|uV)$'        # Fz_μV, P3-uV
        ]
        
        for col in data.columns:
            col_str = str(col).strip()
            
            # Check latency patterns
            for pattern in latency_patterns:
                if re.match(pattern, col_str, re.IGNORECASE):
                    electrode_columns['latency'].append(col)
                    break
            
            # Check amplitude patterns
            for pattern in amplitude_patterns:
                if re.match(pattern, col_str, re.IGNORECASE):
                    electrode_columns['amplitude'].append(col)
                    break
        
        return electrode_columns
    
    def extract_electrode_name(self, column_name: str) -> Optional[str]:
        """
        Extract electrode name from a column name
        
        Args:
            column_name: Name of the column
            
        Returns:
            Electrode name or None if not recognized
        """
        # Common patterns for extracting electrode names
        patterns = [
            # Electrode_measurement patterns
            r'^([A-Za-z]+\d*[zZ]?)[-_]?lat(ency)?$',
            r'^([A-Za-z]+\d*[zZ]?)[-_]?amp(litude)?$',
            r'^([A-Za-z]+\d*[zZ]?)[-_]?time$',
            r'^([A-Za-z]+\d*[zZ]?)[-_]?ms$',
            r'^([A-Za-z]+\d*[zZ]?)[-_]?volt$',
            r'^([A-Za-z]+\d*[zZ]?)[-_]?(μV|uV)$',
            
            # Measurement_electrode patterns
            r'^lat(ency)?[-_]?([A-Za-z]+\d*[zZ]?)$',
            r'^amp(litude)?[-_]?([A-Za-z]+\d*[zZ]?)$'
        ]
        
        col_str = str(column_name).strip()
        
        for pattern in patterns:
            match = re.match(pattern, col_str, re.IGNORECASE)
            if match:
                # Extract the electrode name (first or second group, depending on pattern)
                electrode = match.group(1) if match.group(1) else match.group(2)
                return electrode
        
        return None
