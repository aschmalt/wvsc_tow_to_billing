import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import sys
import threading
import os


class CreateInvoicesGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tow Ticket to Billing Converter")
        self.geometry("600x400")

        # Input file selection
        self.input_label = tk.Label(self, text="Tow Ticket CSV File:")
        self.input_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill="x", padx=10)
        self.input_entry = tk.Entry(self.input_frame, width=50)
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = tk.Button(
            self.input_frame, text="Browse...", command=self.browse_file)
        self.browse_button.pack(side="left", padx=5)

        # Overwrite option
        self.overwrite_var = tk.BooleanVar()
        self.overwrite_check = tk.Checkbutton(
            self, text="Overwrite output files if they exist", variable=self.overwrite_var)
        self.overwrite_check.pack(anchor="w", padx=10, pady=(5, 10))

        # Run button
        self.run_button = tk.Button(
            self, text="Run", command=self.run_conversion)
        self.run_button.pack(pady=(0, 10))

        # Output log
        self.log_text = scrolledtext.ScrolledText(
            self, height=15, state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Tow Ticket CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)

    def run_conversion(self):
        input_file = self.input_entry.get().strip()
        overwrite = self.overwrite_var.get()

        if not input_file:
            messagebox.showerror(
                "Error", "Please select a tow ticket CSV file.")
            return

        if not os.path.isfile(input_file):
            messagebox.showerror(
                "Error", f"File does not exist:\n{input_file}")
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Running conversion...\n")
        self.log_text.config(state="disabled")
        self.run_button.config(state="disabled")

        # Run in a separate thread to keep GUI responsive
        threading.Thread(target=self._run_subprocess, args=(
            input_file, overwrite), daemon=True).start()

    def _run_subprocess(self, input_file, overwrite):
        cmd = [
            sys.executable,
            "-m", "tow_conversion.cli.create_invoices",
            input_file
        ]
        if overwrite:
            cmd.append("--overwrite")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            self._append_log(line)

        process.wait()
        if process.returncode == 0:
            self._append_log("Done.\n")
        else:
            self._append_log(
                f"Process exited with code {process.returncode}\n")
        self.run_button.config(state="normal")

    def _append_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")


if __name__ == "__main__":
    app = CreateInvoicesGUI()
    app.mainloop()
