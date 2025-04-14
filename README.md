
# EEG ERP Excel Preprocess

This project is designed to process EEG ERP (Event-Related Potential) data and perform preprocessing in Excel format.

## 📋 Features

- Easy and fast preprocessing of EEG ERP data.
- Support for input and output in Excel format.
- Powerful tools for data visualization and analysis.
- Modular architecture for scalability and maintainability.

## 🚀 Getting Started

Follow the steps below to get started by cloning the project to your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/YakupErbilir/EEG-erp-Excel-Preprocess.git
cd EEG-erp-Excel-Preprocess
```

### 2. Install Dependencies

Set up your Python environment and install the required dependencies:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Usage

Run the project using:

```bash
python main.py
```

## 📂 Project Structure

```
excel_erp_processor/
├── main.py                  # Entry point for application
├── data_processor.py        # Core data processing logic
├── electrode_manager.py     # Electrode grouping and selection
├── file_handler.py          # File operations and conversions
├── gui/
│   ├── main_window.py       # Main interface
│   ├── electrode_panel.py   # Electrode selection visualization
│   └── report_generator.py  # Processing report functions
└── resources/
    └── electrode_layouts/   # Predefined electrode groups
```

## 🤝 Contributing

If you'd like to contribute, please create a **Pull Request (PR)**. All contributions are welcome!

## 📜 License

This project is licensed under the [MIT License](LICENSE).

## 📧 Contact

For any questions, feel free to reach out to [YakupErbilir](https://github.com/YakupErbilir).
