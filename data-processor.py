import pandas as pd
import numpy as np
import os
import re
from typing import List, Dict, Set, Tuple, Optional


class ERPDataProcessor:
    """
    Handles processing of EEG ERP data files, including:
    - Loading and saving Excel/CSV/TXT files
    - Identifying electrode columns in data
    - Creating new variables based on user-defined electrode groups
    - Calculating averages for left and right hemisphere electrodes
    """
    
    def __init__(self):
        self.data = None
        self.file_path = None
        self.electrode_pattern = re.compile(r'^([A-Za-z]+\d*[zZ]?|[A-Za-z]+[zZ]\d*)[-_]?(Lat|Amp|Latency|Amplitude)$', re.IGNORECASE)
        
    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        Load data from file (CSV, TXT, or XLSX)
        
        Args:
            file_path: Path to the input file
            
        Returns:
            DataFrame containing the loaded data
        """
        self.file_path = file_path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                self.data = pd.read_csv(file_path)
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
                self.data = pd.read_csv(file_path, delimiter=delimiter)
            elif file_ext == '.xlsx' or file_ext == '.xls':
                self.data = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            return self.data
            
        except Exception as e:
            raise IOError(f"Error loading file {file_path}: {str(e)}")
    
    def save_file(self, output_path: str) -> str:
        """
        Save processed data to Excel file
        
        Args:
            output_path: Path where the file should be saved
            
        Returns:
            Path to the saved file
        """
        if self.data is None:
            raise ValueError("No data to save. Load data first.")
            
        try:
            self.data.to_excel(output_path, index=False)
            return output_path
        except Exception as e:
            raise IOError(f"Error saving file {output_path}: {str(e)}")
    
    def detect_electrode_columns(self) -> Dict[str, List[str]]:
        """
        Detect and categorize electrode columns (latency and amplitude) in the data
        
        Returns:
            Dictionary with 'latency' and 'amplitude' keys containing lists of column names
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
            
        electrode_columns = {'latency': [], 'amplitude': []}
        
        for col in self.data.columns:
            match = self.electrode_pattern.match(str(col))
            if match:
                electrode_name = match.group(1)
                measure_type = match.group(2).lower()
                
                if measure_type in ['lat', 'latency']:
                    electrode_columns['latency'].append(col)
                elif measure_type in ['amp', 'amplitude']:
                    electrode_columns['amplitude'].append(col)
        
        return electrode_columns
    
    def identify_electrode_name(self, column_name: str) -> Optional[str]:
        """
        Extract electrode name from a column name
        
        Args:
            column_name: Name of the column
            
        Returns:
            Electrode name or None if not recognized
        """
        match = self.electrode_pattern.match(str(column_name))
        if match:
            return match.group(1)
        return None
    
    def get_electrode_measure_type(self, column_name: str) -> Optional[str]:
        """
        Determine if a column represents amplitude or latency
        
        Args:
            column_name: Name of the column
            
        Returns:
            'latency', 'amplitude', or None if not recognized
        """
        match = self.electrode_pattern.match(str(column_name))
        if match:
            measure_type = match.group(2).lower()
            if measure_type in ['lat', 'latency']:
                return 'latency'
            elif measure_type in ['amp', 'amplitude']:
                return 'amplitude'
        return None
    
    def create_hemisphere_averages(self, left_electrodes: Set[str], right_electrodes: Set[str]) -> Dict[str, List[str]]:
        """
        Calculate average latency and amplitude for left and right hemisphere electrodes
        
        Args:
            left_electrodes: Set of electrodes in the left hemisphere
            right_electrodes: Set of electrodes in the right hemisphere
            
        Returns:
            Dictionary with names of created columns
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
            
        created_columns = {
            'latency': [],
            'amplitude': []
        }
        
        electrode_columns = self.detect_electrode_columns()
        
        # Create average latency for left hemisphere
        left_lat_cols = [col for col in electrode_columns['latency'] 
                         if self.identify_electrode_name(col) in left_electrodes]
        if left_lat_cols:
            col_name = 'LeftHemisphere_Latency_Avg'
            self.data[col_name] = self.data[left_lat_cols].mean(axis=1)
            created_columns['latency'].append(col_name)
        
        # Create average latency for right hemisphere
        right_lat_cols = [col for col in electrode_columns['latency'] 
                          if self.identify_electrode_name(col) in right_electrodes]
        if right_lat_cols:
            col_name = 'RightHemisphere_Latency_Avg'
            self.data[col_name] = self.data[right_lat_cols].mean(axis=1)
            created_columns['latency'].append(col_name)
        
        # Create average amplitude for left hemisphere
        left_amp_cols = [col for col in electrode_columns['amplitude'] 
                         if self.identify_electrode_name(col) in left_electrodes]
        if left_amp_cols:
            col_name = 'LeftHemisphere_Amplitude_Avg'
            self.data[col_name] = self.data[left_amp_cols].mean(axis=1)
            created_columns['amplitude'].append(col_name)
        
        # Create average amplitude for right hemisphere
        right_amp_cols = [col for col in electrode_columns['amplitude'] 
                          if self.identify_electrode_name(col) in right_electrodes]
        if right_amp_cols:
            col_name = 'RightHemisphere_Amplitude_Avg'
            self.data[col_name] = self.data[right_amp_cols].mean(axis=1)
            created_columns['amplitude'].append(col_name)
        
        return created_columns
    
    def create_custom_group_averages(self, group_name: str, electrodes: Set[str]) -> Dict[str, List[str]]:
        """
        Calculate average latency and amplitude for custom electrode groups
        
        Args:
            group_name: Name of the electrode group
            electrodes: Set of electrodes in the group
            
        Returns:
            Dictionary with names of created columns
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
            
        created_columns = {
            'latency': [],
            'amplitude': []
        }
        
        electrode_columns = self.detect_electrode_columns()
        
        # Create average latency for the group
        group_lat_cols = [col for col in electrode_columns['latency'] 
                         if self.identify_electrode_name(col) in electrodes]
        if group_lat_cols:
            col_name = f'{group_name}_Latency_Avg'
            self.data[col_name] = self.data[group_lat_cols].mean(axis=1)
            created_columns['latency'].append(col_name)
        
        # Create average amplitude for the group
        group_amp_cols = [col for col in electrode_columns['amplitude'] 
                         if self.identify_electrode_name(col) in electrodes]
        if group_amp_cols:
            col_name = f'{group_name}_Amplitude_Avg'
            self.data[col_name] = self.data[group_amp_cols].mean(axis=1)
            created_columns['amplitude'].append(col_name)
        
        return created_columns
    
    def create_hemisphere_difference(self) -> Dict[str, List[str]]:
        """
        Calculate the difference between left and right hemisphere averages
        
        Returns:
            Dictionary with names of created columns
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
            
        created_columns = {
            'latency': [],
            'amplitude': []
        }
        
        # Check if hemisphere averages exist
        if 'LeftHemisphere_Latency_Avg' in self.data.columns and 'RightHemisphere_Latency_Avg' in self.data.columns:
            col_name = 'LeftRight_Latency_Diff'
            self.data[col_name] = self.data['LeftHemisphere_Latency_Avg'] - self.data['RightHemisphere_Latency_Avg']
            created_columns['latency'].append(col_name)
        
        if 'LeftHemisphere_Amplitude_Avg' in self.data.columns and 'RightHemisphere_Amplitude_Avg' in self.data.columns:
            col_name = 'LeftRight_Amplitude_Diff'
            self.data[col_name] = self.data['LeftHemisphere_Amplitude_Avg'] - self.data['RightHemisphere_Amplitude_Avg']
            created_columns['amplitude'].append(col_name)
        
        return created_columns
    
    def create_laterality_index(self) -> Dict[str, List[str]]:
        """
        Calculate laterality index: (Left - Right) / (Left + Right)
        
        Returns:
            Dictionary with names of created columns
        """
        if self.data is None:
            raise ValueError("No data loaded. Load data first.")
            
        created_columns = {
            'latency': [],
            'amplitude': []
        }
        
        # Create laterality index for latency
        if 'LeftHemisphere_Latency_Avg' in self.data.columns and 'RightHemisphere_Latency_Avg' in self.data.columns:
            col_name = 'Latency_Laterality_Index'
            left = self.data['LeftHemisphere_Latency_Avg']
            right = self.data['RightHemisphere_Latency_Avg'] 
            self.data[col_name] = (left - right) / (left + right)
            created_columns['latency'].append(col_name)
        
        # Create laterality index for amplitude
        if 'LeftHemisphere_Amplitude_Avg' in self.data.columns and 'RightHemisphere_Amplitude_Avg' in self.data.columns:
            col_name = 'Amplitude_Laterality_Index'
            left = self.data['LeftHemisphere_Amplitude_Avg']
            right = self.data['RightHemisphere_Amplitude_Avg']
            self.data[col_name] = (left - right) / (left + right)
            created_columns['amplitude'].append(col_name)
        
        return created_columns
