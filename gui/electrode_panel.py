"""
electrode_panel.py

This module provides visualization and selection functionality for EEG electrode groups.
"""

import matplotlib.pyplot as plt

class ElectrodePanel:
    def __init__(self, electrode_layout):
        """
        Initialize the ElectrodePanel with a predefined electrode layout.

        Args:
            electrode_layout (dict): Dictionary containing electrode names and their positions.
        """
        self.electrode_layout = electrode_layout

    def display_layout(self):
        """
        Visualizes the electrode layout on a 2D plot.
        """
        print("Displaying electrode layout...")
        x_coords = [pos[0] for pos in self.electrode_layout.values()]
        y_coords = [pos[1] for pos in self.electrode_layout.values()]
        labels = list(self.electrode_layout.keys())

        plt.figure(figsize=(8, 8))
        plt.scatter(x_coords, y_coords, c='blue', label='Electrodes')
        
        for label, x, y in zip(labels, x_coords, y_coords):
            plt.text(x, y, label, fontsize=9, ha='center', va='center')

        plt.title("Electrode Layout Visualization")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.legend()
        plt.grid(True)
        plt.show()

    def select_electrodes(self, selected_names):
        """
        Highlights selected electrodes on the layout.

        Args:
            selected_names (list): List of electrode names to highlight.
        """
        print(f"Highlighting selected electrodes: {selected_names}")
        x_coords = [pos[0] for pos in self.electrode_layout.values()]
        y_coords = [pos[1] for pos in self.electrode_layout.values()]
        labels = list(self.electrode_layout.keys())

        plt.figure(figsize=(8, 8))
        for label, x, y in zip(labels, x_coords, y_coords):
            if label in selected_names:
                plt.scatter(x, y, c='red', label='Selected', s=100)
            else:
                plt.scatter(x, y, c='blue', s=50)
            plt.text(x, y, label, fontsize=9, ha='center', va='center')

        plt.title("Selected Electrodes Visualization")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.legend()
        plt.grid(True)
        plt.show()


# Example usage
if __name__ == "__main__":
    # Example electrode layout (replace with actual data)
    example_layout = {
        "Fp1": (1, 8),
        "Fp2": (7, 8),
        "F3": (2, 6),
        "F4": (6, 6),
        "C3": (2, 4),
        "C4": (6, 4),
        "P3": (2, 2),
        "P4": (6, 2),
        "O1": (3, 0),
        "O2": (5, 0)
    }

    panel = ElectrodePanel(example_layout)
    panel.display_layout()
    panel.select_electrodes(["Fp1", "F4", "O2"])