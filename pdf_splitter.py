import os
import re
import platform
import subprocess
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pypdf import PdfReader, PdfWriter

# --- Helper Function to Open Folder ---
def open_folder(path):
    """Opens the specified folder in the default file explorer."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin": # macOS
            subprocess.run(["open", path])
        else: # Linux
            subprocess.run(["xdg-open", path])
    except Exception as e:
        print(f"Failed to open folder: {e}")

# --- Core Splitting Logic ---
def split_pdf_on_page_count(input_path: str, output_dir: str):
    """
    Splits a PDF, extracts the PO number, and returns a status message.
    Returns:
        tuple: (bool, str) representing (success_status, message)
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_path)

        page_pattern = re.compile(r"Page\s*:\s*(\d+)\s*of\s*(\d+)")
        po_pattern = re.compile(r"Purchase Order No\.:\s*(\d+)")

        pages_for_current_doc = []
        files_created_count = 0

        for page in reader.pages:
            pages_for_current_doc.append(page)
            text = page.extract_text() or ""
            match = page_pattern.search(text)

            if match and match.group(1) == match.group(2):
                files_created_count += 1
                output_filename = f"Document_{files_created_count}.pdf"
                
                if pages_for_current_doc:
                    first_page_text = pages_for_current_doc[0].extract_text() or ""
                    po_match = po_pattern.search(first_page_text)
                    if po_match:
                        po_number = po_match.group(1)
                        output_filename = f"PO_{po_number}.pdf"

                output_path = os.path.join(output_dir, output_filename)
                
                writer = PdfWriter()
                for doc_page in pages_for_current_doc:
                    writer.add_page(doc_page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                pages_for_current_doc = []

        if files_created_count == 0:
            return (False, "No documents were found to split. Check if the PDF contains 'Page X of X' markers.")

        return (True, f"Success! {files_created_count} files were created.")

    except Exception as e:
        return (False, f"An unexpected error occurred: {e}")

# --- GUI Application Class ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("PDF Splitter Pro")
        self.geometry("550x300")
        ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
        ctk.set_default_color_theme("blue")

        # Data variables
        self.input_path_var = ctk.StringVar()
        self.output_path_var = ctk.StringVar()
        
        # Center frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Widgets
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
        self.run_button = ctk.CTkButton(self.main_frame, text="Split PDF", font=("", 14, "bold"), fg_color="#28a745", hover_color="#218838", command=self.run_process)
        self.run_button.pack(pady=30, padx=20, fill="x", ipady=5)

    def select_input_file(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.input_path_var.set(filepath)
            self.input_label.configure(text=os.path.basename(filepath), text_color="white") # Use system theme color

    def select_output_folder(self):
        folderpath = ctk.filedialog.askdirectory()
        if folderpath:
            self.output_path_var.set(folderpath)
            self.output_label.configure(text=folderpath, text_color="white")

    def run_process(self):
        input_pdf = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_pdf or not output_dir:
            CTkMessagebox(title="Error", message="Please select both an input file and an output folder.", icon="cancel")
            return

        self.run_button.configure(text="Processing...", state="disabled")
        self.update_idletasks() # Refresh the GUI to show the change

        # Run core logic
        success, message = split_pdf_on_page_count(input_pdf, output_dir)

        # Show final message
        if success:
            CTkMessagebox(title="Success", message=message, icon="check")
            open_folder(output_dir) # 📂 Open the destination folder!
            self.destroy() # Close the app
        else:
            CTkMessagebox(title="Error", message=message, icon="cancel")
            self.run_button.configure(text="Split PDF", state="normal") # Re-enable on error

if __name__ == "__main__":
    app = App()
    app.mainloop()