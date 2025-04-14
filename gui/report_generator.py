"""
report_generator.py

This module handles the generation of processing reports for EEG ERP data.
"""

import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        """
        Initialize the ReportGenerator.

        Args:
            output_dir (str): Directory where reports will be saved.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_summary_report(self, data_summary, file_name="summary_report.txt"):
        """
        Generates a summary report of the processed data.

        Args:
            data_summary (dict): A summary of the processed data.
            file_name (str): Name of the file to save the report.
        """
        report_path = os.path.join(self.output_dir, file_name)
        with open(report_path, "w") as file:
            file.write(f"EEG ERP Processing Report\n")
            file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write("Data Summary:\n")
            for key, value in data_summary.items():
                file.write(f"- {key}: {value}\n")
        print(f"Summary report saved at: {report_path}")

    def generate_error_report(self, errors, file_name="error_report.txt"):
        """
        Generates an error report for any issues encountered during processing.

        Args:
            errors (list): A list of error messages.
            file_name (str): Name of the file to save the report.
        """
        report_path = os.path.join(self.output_dir, file_name)
        with open(report_path, "w") as file:
            file.write(f"EEG ERP Error Report\n")
            file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write("Errors:\n")
            for error in errors:
                file.write(f"- {error}\n")
        print(f"Error report saved at: {report_path}")

# Example usage
if __name__ == "__main__":
    # Example data summary
    example_summary = {
        "Total Records Processed": 120,
        "Successful Processes": 115,
        "Failed Processes": 5,
        "Processing Time": "2 minutes 30 seconds"
    }

    # Example errors
    example_errors = [
        "File 'subject_01.xlsx' is missing required columns.",
        "Invalid data format in 'subject_03.xlsx'.",
        "Failed to save processed data for 'subject_07.xlsx'."
    ]

    # Create a report generator instance
    generator = ReportGenerator()

    # Generate reports
    generator.generate_summary_report(example_summary)
    generator.generate_error_report(example_errors)