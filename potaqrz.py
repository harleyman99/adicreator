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
        self.geometry("560x420")
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
            font=ctk.CTkFont(size=12)
        )
        self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            file_input_frame, 
            text="Browse...", 
            width=100, 
            height=35, 
            command=self.browse_file
        )
        self.browse_btn.pack(side="right")

        # Action Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=(20, 5))

        # Save Button
        self.save_btn = ctk.CTkButton(
            btn_frame, 
            text="Process & Save New ADIF", 
            height=45, 
            fg_color="#1f6aa5", 
            hover_color="#144870",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.process_and_save
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Clear/Reset Button
        self.reset_btn = ctk.CTkButton(
            btn_frame, 
            text="Reset", 
            width=80,
            height=45, 
            fg_color="#4A4A4A", 
            hover_color="#333333",
            font=ctk.CTkFont(size=14),
            command=self.reset_form
        )
        self.reset_btn.pack(side="right")

        # Status Label
        self.status_label = ctk.CTkLabel(
            self, 
            text="Ready", 
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        )
        self.status_label.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select Source ADIF File",
            filetypes=[("ADIF Files", "*.adi *.adif"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_file_path = file_path
            
            # Safely write path to text box
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            
            self.status_label.configure(
                text=f"Loaded: {os.path.basename(file_path)}", 
                text_color="#2FA572"
            )

    def process_and_save(self):
        park_num = self.park_entry.get().strip().upper()

        if not park_num:
            messagebox.showerror("Input Error", "Please enter a POTA park number.", parent=self)
            return

        # Fallback to text box value if string variable wasn't updated
        current_path = self.file_path_entry.get().strip()
        if not current_path or not os.path.exists(current_path):
            messagebox.showerror("File Error", "Please select a valid ADIF source file.", parent=self)
            return

        # Prepare comment tag: <comment:N>PARK where N is the length of park_num
        comment_tag = f"<comment:{len(park_num)}>{park_num}"

        # Ask destination file
        default_filename = f"POTA_{park_num}_" + os.path.basename(current_path)
        save_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save New ADIF File As...",
            initialfile=default_filename,
            defaultextension=".adi",
            filetypes=[("ADIF Files", "*.adi"), ("All Files", "*.*")]
        )

        if not save_path:
            return  # User canceled save dialog

        try:
            with open(current_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Case-insensitive replacement of <EOR> or <eor> with <comment:N>PARK<eor>
            pattern = re.compile(r"(<EOR>)", re.IGNORECASE)
            matches = len(pattern.findall(content))

            if matches == 0:
                messagebox.showwarning("Warning", "No <EOR> tags found in the source file.", parent=self)
                return

            modified_content = pattern.sub(f"{comment_tag} \\1", content)

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(modified_content)

            messagebox.showinfo(
                "Success", 
                f"Successfully updated {matches} QSO records!\n\nFile saved to:\n{save_path}",
                parent=self
            )
            
            # Reset UI after successful completion
            self.reset_form()
            self.status_label.configure(
                text=f"Done! Updated {matches} record(s). Ready for next file.", 
                text_color="#2FA572"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{str(e)}", parent=self)

    def reset_form(self):
        """Clears inputs and resets state so buttons are ready for a new operation."""
        self.selected_file_path = ""
        self.file_path_entry.delete(0, tk.END)
        self.park_entry.delete(0, tk.END)
        self.status_label.configure(text="Ready", text_color="gray")


if __name__ == "__main__":
    app = PotaApp()
    app.mainloop()