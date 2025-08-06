# PDF Splitter Pro

A desktop application that automatically splits a single, large PDF file containing multiple Purchase Order documents into separate files. It intelligently names each new file using the Purchase Order (PO) number found on the first page of each document.

---

## Features ✨
* **Modern Interface**: Built with CustomTkinter for a user-friendly dark/light mode GUI.
* **Intelligent Naming**: Automatically finds the text "Purchase Order No.: XXXXX" and names the output file `PO_XXXXX.pdf`.
* **Automatic Splitting**: Detects the end of each sub-document by looking for "Page X of X" footers.
* **Standalone Application**: Packaged with PyInstaller into a single `.exe` file that requires no installation or dependencies for the end-user.

---

## Setup for Development 👨‍💻

To alter or contribute to this project, follow these steps to set up a local development environment.

### Prerequisites
* [Python 3.10+](https://www.python.org/downloads/)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    * This keeps the project's dependencies isolated.

    ```bash
    # Create the environment
    py -m venv venv

    # Activate it (on Windows PowerShell)
    .\venv\Scripts\Activate.ps1
    ```

3.  **Install the required packages:**
    * All necessary packages are listed in the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

---

## Building the Application 🚀

To package the script into the final `.exe` file, first ensure you have the correct, full path to the `customtkinter` library.

1.  **Find the customtkinter path (if needed):**
    ```bash
    py find_path.py
    ```

2.  **Run the PyInstaller build command:**
    * Replace `YOUR_FULL_PATH_TO_CUSTOMTKINTER` with the path from the step above.

    ```bash
    py -m PyInstaller --onefile --windowed --name="PDF Splitter Pro" --add-data "YOUR_FULL_PATH_TO_CUSTOMTKINTER;customtkinter" pdf_splitter_modern.py
    ```

3.  The final application, **`PDF Splitter Pro.exe`**, will be located in the **`dist`** folder.
