import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Configure CustomTkinter theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PotaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("POTA ADIF Park Comment Inserter")
        self.geometry("550x380")
        self.resizable(False, False)

        self.selected_file_path = ""

        # UI Layout
        self._create_widgets()

    def _create_widgets(self):
        # Title Label
        title_label = ctk.CTkLabel(
            self, 
            text="POTA ADIF Comment Inserter", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Park Number Section
        park_frame = ctk.CTkFrame(self, fg_color="transparent")
        park_frame.pack(fill="x", padx=40, pady=10)

        park_label = ctk.CTkLabel(
            park_frame, 
            text="POTA Park Number:", 
            font=ctk.CTkFont(size=14)
        )
        park_label.pack(anchor="w", pady=(0, 5))

        self.park_entry = ctk.CTkEntry(
            park_frame, 
            placeholder_text="e.g. K-1234", 
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.park_entry.pack(fill="x")

        # File Selection Section
        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.pack(fill="x", padx=40, pady=10)

        file_label = ctk.CTkLabel(
            file_frame, 
            text="Source ADIF File:", 
            font=ctk.CTkFont(size=14)
        )
        file_label.pack(anchor="w", pady=(0, 5))

        file_input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_input_frame.pack(fill="x")

        self.file_path_entry = ctk.CTkEntry(
            file_input_frame, 
            placeholder_text="No file selected...", 
            height=35, 
            state="disabled"
        )
        self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            file_input_frame, 
            text="Browse...", 
            width=100, 
            height=35, 
            command=self.browse_file
        )
        browse_btn.pack(side="right")

        # Save Button
        self.save_btn = ctk.CTkButton(
            self, 
            text="Process & Save New ADIF", 
            height=45, 
            fg_color="#1f6aa5", 
            hover_color="#144870",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.process_and_save
        )
        self.save_btn.pack(fill="x", padx=40, pady=(25, 10))

        # Status Label
        self.status_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        )
        self.status_label.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Source ADIF File",
            filetypes=[("ADIF Files", "*.adi *.adif"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_path_entry.configure(state="normal")
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.file_path_entry.configure(state="disabled")
            self.status_label.configure(text="Source file loaded successfully.", text_color="#2FA572")

    def process_and_save(self):
        park_num = self.park_entry.get().strip().upper()

        if not park_num:
            messagebox.showerror("Input Error", "Please enter a POTA park number.")
            return

        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            messagebox.showerror("File Error", "Please select a valid ADIF source file.")
            return

        # Prepare comment string
        comment_tag = f"<comment:9>{park_num}"

        # Ask destination file
        default_filename = f"POTA_{park_num}_" + os.path.basename(self.selected_file_path)
        save_path = filedialog.asksaveasfilename(
            title="Save New ADIF File As...",
            initialfile=default_filename,
            defaultextension=".adi",
            filetypes=[("ADIF Files", "*.adi"), ("All Files", "*.*")]
        )

        if not save_path:
            return  # User canceled save dialog

        try:
            with open(self.selected_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Case-insensitive replacement of <EOR> or <eor> with <comment:9>PARK<eor>
            pattern = re.compile(r"(<EOR>)", re.IGNORECASE)
            
            # Count matches first for feedback
            matches = len(pattern.findall(content))
            
            if matches == 0:
                messagebox.showwarning("Warning", "No <EOR> tags found in the source file.")
                return

            modified_content = pattern.sub(f"{comment_tag} \\1", content)

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(modified_content)

            messagebox.showinfo(
                "Success", 
                f"Successfully updated {matches} QSO records!\n\nFile saved to:\n{save_path}"
            )
            self.status_label.configure(
                text=f"Saved {matches} record(s) to {os.path.basename(save_path)}", 
                text_color="#2FA572"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")


if __name__ == "__main__":
    app = PotaApp()
    app.mainloop()