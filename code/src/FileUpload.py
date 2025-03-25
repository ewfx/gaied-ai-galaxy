import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Button, filedialog, Text, Scrollbar, Toplevel
import json
from ttkbootstrap.dialogs import Messagebox

from detect_duplicate import insert_vector, is_duplicate_email
from model import classify_request, extract_emailBody_attachments, extract_entities, get_email_embeddings

class EmailProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hackathon 2025")
        self.root.geometry("800x600")
        self.files = []
        self.processed_data = []

        # Bulk File Upload Section
        self.upload_label = ttk.Label(root, text="Bulk Files Upload:", font=("Arial", 12))
        self.upload_label.pack(pady=10)

        self.file_display = Text(root, height=5, width=80, state=DISABLED)
        self.file_display.pack(pady=5)

        # Create a frame to hold buttons side by side
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=5)

        self.browse_button = ttk.Button(button_frame, text="Browse", command=self.browse_files)
        self.browse_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear Selection", command=self.clear_selection, bootstyle="danger")
        self.clear_button.pack(side="left", padx=5)

        # Process Emails Button
        self.process_button = ttk.Button(root, text="Process Emails", command=self.process_emails)
        self.process_button.pack(pady=20)

        # Output Section
        self.output_label = ttk.Label(root, text="Output:", font=("Arial", 12))
        self.output_label.pack(pady=10)

        self.view_json_button = ttk.Button(root, text="View JSON", command=self.view_json, state=DISABLED)
        self.view_json_button.pack(pady=5)

        self.table_frame = ttk.Frame(root)
        self.table_frame.pack(pady=10, fill=X)

    def browse_files(self):
        file_types = [("PDF files", "*.pdf"), ("Email files", "*.eml"), ("Text files", "*.txt")]
        selected_files = filedialog.askopenfilenames(filetypes=file_types)
        if selected_files:
            self.files.extend(selected_files)
            self.update_file_display()

    def clear_selection(self):
        """Clears the selected files and updates the UI."""
        self.file_display.config(state=NORMAL)  # Enable text widget for updates
        self.file_display.delete("1.0", tk.END)  # Clear text box
        self.file_display.config(state=DISABLED)  # Disable text widget after clearing
        self.files.clear()  # Clear stored file list
        self.processed_data = []  # Clear any extracted data

        # Disable View JSON button as well
        self.view_json_button.config(state=DISABLED)

        # Force UI refresh
        self.file_display.update_idletasks()

    def update_file_display(self):
        self.file_display.config(state=NORMAL)
        self.file_display.delete(1.0, "end")
        for file in self.files:
            self.file_display.insert("end", f"{file}\n")
        self.file_display.config(state=DISABLED)

    def process_emails(self):
        if not self.files:
            Messagebox.show_error("No files selected for processing.")
            return

        processed_data = []
        for file in self.files:
            # Extract email content
            email_body = extract_emailBody_attachments(file)

            # Generate embeddings
            email_embeddings = get_email_embeddings(email_body)

            # Check for duplicates
            is_duplicate, request, sub_request, entities, confidence_score = is_duplicate_email(email_embeddings, email_body)
            print(type(request))
            if is_duplicate:
                processed_data.append({
                    "Request Type": request,
                    "Sub-Request Type": sub_request,
                    "Extracted Fields": entities,
                    "Duplicate": True,
                    "Confidence Score": confidence_score
                })
            else:
                # Classify request type and extract entities
                request = classify_request(email_body)
                entities = extract_entities(email_body)

                # Store in Pinecone
                insert_vector(email_embeddings, email_body, request["request_type"], request["sub_request_type"], entities, request["confidence_score"])
                print(type(request))
                processed_data.append({
                    "Request Type": request["request_type"],
                    "Sub-Request Type": request["sub_request_type"],
                    "Extracted Fields": entities,
                    "Duplicate": False,
                    "Confidence Score": request["confidence_score"]
                })
            

        self.processed_data = processed_data
        # Clear the file list
        
        self.view_json_button.config(state=NORMAL)
        self.display_table()
        self.clear_selection()

    def view_json(self):
        if not self.processed_data:
            return

        json_window = Toplevel(self.root)
        json_window.title("JSON Output")
        json_window.geometry("600x400")

        json_text = Text(json_window, wrap="none")
        json_text.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(json_window, command=json_text.yview)
        scrollbar.pack(side="right", fill="y")

        json_text.config(yscrollcommand=scrollbar.set)
        json_text.insert("end", json.dumps(self.processed_data, indent=4))
        json_text.config(state=DISABLED)

    def show_json_popup(self, json_data):
        """ Display extracted fields in a popup window """
        popup = Toplevel()
        popup.title("Extracted Fields JSON")
        popup.geometry("400x300")

        text_widget = Text(popup, wrap="word", font=("Arial", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", json.dumps(json_data, indent=4))
        text_widget.config(state="disabled")  # Make it read-only

        close_button = Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=5)

    def display_table(self):
        # Clear previous table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Corrected Table Headers
        headers = ["Request Type", "Sub Request Type", "Extracted Fields", "Confidence Score", "Duplicate"]
        
        for col, header in enumerate(headers):
            header_label = ttk.Label(self.table_frame, text=header, font=("Arial", 10, "bold"), anchor="center")
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")

        # Populate table rows
        for row, data in enumerate(self.processed_data, start=1):
            ttk.Label(self.table_frame, text=data["Request Type"], anchor="center").grid(row=row, column=0, padx=10, pady=5, sticky="nsew")
            ttk.Label(self.table_frame, text=data["Sub-Request Type"], anchor="center").grid(row=row, column=1, padx=10, pady=5, sticky="nsew")

            # Add "View JSON" button in Extracted Fields column
            extracted_fields_button = Button(self.table_frame, text="View Extracted Data", command=lambda d=json.loads(data["Extracted Fields"]): self.show_json_popup(d))
            extracted_fields_button.grid(row=row, column=2, padx=10, pady=5)

            ttk.Label(self.table_frame, text=str(data["Confidence Score"]), anchor="center").grid(row=row, column=3, padx=10, pady=5, sticky="nsew")
            ttk.Label(self.table_frame, text=str(data["Duplicate"]), anchor="center").grid(row=row, column=4, padx=10, pady=5, sticky="nsew")

        # Make the columns expand evenly
        for i in range(len(headers)):
            self.table_frame.columnconfigure(i, weight=1)

                
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = EmailProcessorApp(root)
    root.mainloop()