PDF Splitter Pro
================

A desktop application that automatically splits a single, large PDF file containing multiple Purchase Order documents into separate files. It intelligently names each new file using the Purchase Order (PO) number found on the first page of each document.

Features
----------

-   **Modern Interface:** Built with Python for a reliable user experience.

-   **Intelligent Naming:** Automatically finds the text "Purchase Order No.: XXXXX" and names the output file `PO_XXXXX.pdf`.

-   **Automatic Splitting:** Detects the end of each sub-document by looking for "Page X of X" footers.

-   **Easy Installation:** Packaged with Inno Setup into a professional Windows installer (`.exe`) that creates desktop shortcuts and handles setup automatically.

Setup for Development
---------------------------

To alter or contribute to this project, follow these steps to set up a local development environment.

### Prerequisites

-   Python 3.10+

### Installation Steps

1.  **Clone the repository:**

    Bash

    ```
    git clone "https://github.com/aroizmand/Purchase-Order-Splitter"
    cd "https://github.com/aroizmand/Purchase-Order-Splitter"

    ```

2.  **Create and activate a virtual environment:** This keeps the project's dependencies isolated.

    PowerShell

    ```
    # Create the environment
    py -m venv venv

    # Activate it (on Windows PowerShell)
    .\venv\Scripts\Activate.ps1

    ```

3.  **Install the required packages:** All necessary packages are listed in the `requirements.txt` file.

    Bash

    ```
    pip install -r requirements.txt

    ```

Building the Application 
---------------------------

We use a two-step process to build the application: first compiling the Python script into an executable, and then wrapping it in an installer for distribution.

### Step 1: Compile the Executable

This bundles the Python script and all dependencies (including DLLs) into a single `.exe` file using PyInstaller.

1.  Ensure your virtual environment is activated.

2.  Run the build command:

    Bash

    ```
    pyinstaller --onefile --noconsole pdf_splitter.py

    ```

3.  The resulting file, `pdf_splitter.exe`, will be located in the `dist` folder.

### Step 2: Create the Installer

We use **Inno Setup** to create the final distribution file (`PDFSplitter_Installer.exe`).

1.  Install [Inno Setup](https://jrsoftware.org/isdl.php).

2.  Open the **Script Wizard** in Inno Setup.

3.  **Application Files:**

    -   **Main Executable:** Select `dist\pdf_splitter.exe` (created in Step 1).

    -   **Other Files:** Leave empty (the `--onefile` flag in Step 1 handled this).

4.  **Settings:** Ensure "Create a desktop shortcut" is checked.

5.  **Compile:** Run the script to generate the final installer.

The final installer will be located in the **Output** folder (or wherever you configured Inno Setup to save it). This is the file to share with end-users.
