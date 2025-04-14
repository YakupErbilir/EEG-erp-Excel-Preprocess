# Electrode definitions and grouping functionality
class ElectrodeManager:
    def __init__(self):
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
        
        # Categorize electrodes by hemisphere
        self.left_electrodes = set()
        self.right_electrodes = set()
        self.midline_electrodes = set()
        
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
    
    def get_all_electrodes(self):
        """Return all electrodes in the system"""
        return self.all_electrodes
    
    def get_electrode_group(self, group_name):
        """Return electrodes in a specific group"""
        return self.electrode_groups.get(group_name, [])
    
    def get_all_groups(self):
        """Return all available group names"""
        return list(self.electrode_groups.keys())
    
    def get_hemisphere(self, electrode):
        """Return the hemisphere ('left', 'right', or 'midline') for an electrode"""
        if electrode in self.left_electrodes:
            return 'left'
        elif electrode in self.right_electrodes:
            return 'right'
        else:
            return 'midline'
    
    def detect_electrodes_in_columns(self, column_names):
        """Detect which columns might contain electrode data"""
        electrode_columns = {}
        
        for column in column_names:
            for electrode in self.all_electrodes:
                if electrode in column:
                    # Detect if it's latency or amplitude
                    if 'latency' in column.lower():
                        if 'latency' not in electrode_columns:
                            electrode_columns['latency'] = {}
                        electrode_columns['latency'][electrode] = column
                    elif 'amplitude' in column.lower() or 'amp' in column.lower():
                        if 'amplitude' not in electrode_columns:
                            electrode_columns['amplitude'] = {}
                        electrode_columns['amplitude'][electrode] = column
        
        return electrode_columns
    
    def create_custom_group(self, group_name, electrodes):
        """Create a new custom group of electrodes"""
        if group_name not in self.electrode_groups:
            self.electrode_groups[group_name] = list(set(electrodes) & set(self.all_electrodes))
            return True
        return False
