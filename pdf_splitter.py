import os
import re
import platform
import subprocess
import threading
from pathlib import Path
from typing import Callable, Tuple

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pypdf import PdfReader, PdfWriter

# --- Constants ---
PAGE_PATTERN = re.compile(r"Page\s*:\s*(\d+)\s*of\s*(\d+)")
PO_PATTERN = re.compile(r"Purchase Order No\.:\s*(\d+)")


# --- Helper Functions ---
def open_folder(path: Path):
    """Opens the specified folder in the default file explorer."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
    except Exception as e:
        print(f"Failed to open folder: {e}")


def get_unique_filepath(path: Path) -> Path:
    """
    Checks if a file path exists. If it does, appends a counter.
    e.g., 'file.pdf' -> 'file (1).pdf'
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


# --- Core Splitting Logic ---
def split_pdf_by_marker(
    input_path: Path,
    output_dir: Path,
    progress_callback: Callable[[float], None]
) -> Tuple[bool, str]:
    """
    Splits a PDF based on 'Page X of X' markers and renames using PO number.

    CHANGED:
    - Uses pathlib.Path for all file operations.
    - Scans all pages in a sub-document for a PO number, not just the first.
    - Uses get_unique_filepath to avoid overwriting files.
    - Accepts a progress_callback to update the GUI.
    """
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        if total_pages == 0:
            return (False, "The selected PDF is empty or corrupted.")

        pages_for_current_doc = []
        files_created_count = 0

        for i, page in enumerate(reader.pages):
            progress_callback( (i + 1) / total_pages * 100 ) # Update progress
            pages_for_current_doc.append(page)
            text = page.extract_text() or ""
            page_match = PAGE_PATTERN.search(text)

            # Split when find the last page of a sub-document
            if page_match and page_match.group(1) == page_match.group(2):
                output_filename = f"Document_{files_created_count + 1}.pdf"
                
                # Search all pages in the buffer for the PO number
                po_number_found = None
                for doc_page in pages_for_current_doc:
                    first_page_text = doc_page.extract_text() or ""
                    po_match = PO_PATTERN.search(first_page_text)
                    if po_match:
                        po_number_found = po_match.group(1)
                        output_filename = f"PO_{po_number_found}.pdf"
                        break # Found it, no need to search more pages
                
                # Get a unique path to avoid overwriting existing files
                output_path = get_unique_filepath(output_dir / output_filename)

                writer = PdfWriter()
                for p in pages_for_current_doc:
                    writer.add_page(p)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

                files_created_count += 1
                pages_for_current_doc = [] # Reset for the next document

        if files_created_count == 0:
            return (False, "No documents split. Check if PDF contains 'Page X of X' markers.")

        return (True, f"Success! {files_created_count} files created.")

    except Exception as e:
        return (False, f"An unexpected error occurred: {e}")


# --- GUI Application Class ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Splitter Pro")
        self.geometry("550x380")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.input_path = ctk.StringVar()
        self.output_path = ctk.StringVar()

        # Center frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # --- Input File Selection ---
        self.input_button = ctk.CTkButton(self.main_frame, text="1. Select Input PDF", command=self.select_input_file)
        self.input_button.pack(pady=(10, 5), padx=20, fill="x")
        self.input_label = ctk.CTkLabel(self.main_frame, text="No file selected", text_color="gray")
        self.input_label.pack()

        # --- Output Folder Selection ---
        self.output_button = ctk.CTkButton(self.main_frame, text="2. Select Output Folder", command=self.select_output_folder)
        self.output_button.pack(pady=(15, 5), padx=20, fill="x")
        self.output_label = ctk.CTkLabel(self.main_frame, text="No folder selected", text_color="gray")
        self.output_label.pack()

        # --- Run Button ---
        self.run_button = ctk.CTkButton(self.main_frame, text="Split PDF", font=("", 14, "bold"), fg_color="#28a745", hover_color="#218838", command=self.run_process_in_thread)
        self.run_button.pack(pady=30, padx=20, fill="x", ipady=5)
        
        # --- Progress Bar and Status Label ---
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="")
        self.status_label.pack(pady=(5, 10))

    def select_input_file(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.input_path.set(filepath)
            # Use theme-aware color
            label_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            self.input_label.configure(text=Path(filepath).name, text_color=label_color)
            self.reset_status()

    def select_output_folder(self):
        folderpath = ctk.filedialog.askdirectory()
        if folderpath:
            self.output_path.set(folderpath)
            # Theme-aware color
            label_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            self.output_label.configure(text=folderpath, text_color=label_color)
            self.reset_status()

    def set_ui_state(self, is_enabled: bool):
        """Helper to enable/disable controls during processing."""
        state = "normal" if is_enabled else "disabled"
        self.input_button.configure(state=state)
        self.output_button.configure(state=state)
        self.run_button.configure(state=state)
        self.run_button.configure(text="Split PDF" if is_enabled else "Processing...")

    def reset_status(self):
        """Resets progress bar and status text."""
        self.progress_bar.set(0)
        self.status_label.configure(text="")

    def update_progress(self, value: float):
        """Callback to update progress bar from the thread."""
        self.progress_bar.set(value / 100)
        self.status_label.configure(text=f"Processing... {value:.0f}%")

    def run_process_in_thread(self):
        """Runs the main logic in a separate thread to keep the GUI responsive."""
        input_pdf = self.input_path.get()
        output_dir = self.output_path.get()

        if not input_pdf or not output_dir:
            CTkMessagebox(title="Error", message="Please select both an input file and an output folder.", icon="cancel")
            return
            
        self.set_ui_state(is_enabled=False)
        self.reset_status()

        # Create and start the worker thread
        thread = threading.Thread(
            target=self.processing_worker,
            args=(Path(input_pdf), Path(output_dir))
        )
        thread.daemon = True # Allows main app to exit even if thread is running
        thread.start()
        
    def processing_worker(self, input_pdf: Path, output_dir: Path):
        """The function that runs in the background thread."""
        success, message = split_pdf_by_marker(
            input_pdf,
            output_dir,
            lambda val: self.after(0, self.update_progress, val) # Safely update GUI
        )
        # Schedule the final result message to be shown on the main thread
        self.after(0, self.on_processing_complete, success, message, output_dir)

    def on_processing_complete(self, success: bool, message: str, output_dir: Path):
        """NEW: Handles the result from the worker thread."""
        self.set_ui_state(is_enabled=True)
        self.status_label.configure(text=message)

        if success:
            msg_box = CTkMessagebox(title="Success", message=message, icon="check", option_1="Open Folder", option_2="OK")
            if msg_box.get() == "Open Folder":
                open_folder(output_dir)
        else:
            CTkMessagebox(title="Error", message=message, icon="cancel")


if __name__ == "__main__":
    app = App()
    app.mainloop()