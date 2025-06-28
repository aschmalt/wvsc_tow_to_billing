"""GUI for converting tow tickets to billing invoices."""
from pathlib import Path
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tow_conversion.cli.create_invoices import convert_tow_ticket_to_all_invoices
import os
import subprocess
import sys


class CreateInvoicesGUI(tk.Tk):
    """GUI application for converting tow tickets to billing invoices."""

    def __init__(self) -> None:
        """Initialize the GUI application."""
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

        # Output directory selection
        self.output_label = tk.Label(self, text="Output Directory:")
        self.output_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.output_frame = tk.Frame(self)
        self.output_frame.pack(fill="x", padx=10)
        self.output_entry = tk.Entry(self.output_frame, width=50)
        self.output_entry.pack(side="left", fill="x", expand=True)
        self.output_browse_button = tk.Button(
            self.output_frame, text="Browse...", command=self.browse_output_dir)
        self.output_browse_button.pack(side="left", padx=5)

        # Overwrite option
        self.overwrite_var = tk.BooleanVar(value=False)
        self.overwrite_check = tk.Checkbutton(
            self, text="Overwrite existing files", variable=self.overwrite_var)
        self.overwrite_check.pack(anchor="w", padx=10, pady=(5, 10))

        # Run button
        self.run_button = tk.Button(
            self, text="Run", command=self.run_conversion
        )
        self.run_button.pack(fill="x", padx=10, pady=(0, 10))

        # Output log
        self.log_text = scrolledtext.ScrolledText(
            self, height=15, state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Configure logging
        self.text_handler = TextWidgetHandler(
            lambda msg: self.after(0, self._append_log, msg))

        class LevelBasedFormatter(logging.Formatter):
            def format(self, record) -> str:
                if record.levelno == logging.INFO:
                    self._style._fmt = '%(message)s'
                elif record.levelno == logging.WARNING:
                    self._style._fmt = 'WARNING: %(message)s'
                elif record.levelno >= logging.ERROR:
                    self._style._fmt = 'ERROR: %(message)s'
                else:
                    self._style._fmt = '%(levelname)s: %(message)s'
                return super().format(record)

        formatter = LevelBasedFormatter()
        self.text_handler.setFormatter(formatter)

        # Remove all existing handlers from root logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.getLogger().addHandler(self.text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def browse_file(self) -> None:
        """Open a file dialog to select the tow ticket CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select Tow Ticket CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)

    def browse_output_dir(self) -> None:
        """Open a directory dialog to select the output directory."""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)

    def run_conversion(self) -> None:
        """Run the conversion process in a background thread."""
        input_file = self.input_entry.get().strip()
        output_dir = self.output_entry.get().strip()
        overwrite = self.overwrite_var.get()

        if not input_file:
            messagebox.showerror(title="Error",
                                 message="Please select a tow ticket CSV file.")
            return

        if not Path(input_file).is_file():
            messagebox.showerror(title="Error",
                                 message=f"File does not exist:\n{input_file}")
            return

        if not output_dir:
            messagebox.showerror(title="Error",
                                 message="Please select an output directory.")
            return
        if not Path(output_dir).is_dir():
            messagebox.showerror(title="Error",
                                 message=f"Output directory does not exist:\n{output_dir}")
            return

        invoice_file = Path(output_dir, "member_invoices.csv")
        vendor_file = Path(output_dir, "vendor_invoices.csv")

        if invoice_file.exists() and not overwrite:
            messagebox.showerror(title="Error",
                                 message=f"Member invoice file already exists:\n{invoice_file}\n"
                                         "Please choose a different output directory or enable overwrite.")
            return
        if vendor_file.exists() and not overwrite:
            messagebox.showerror(title="Error",
                                 message=f"Vendor invoice file already exists:\n{vendor_file}\n"
                                         "Please choose a different output directory or enable overwrite.")
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Running conversion...\n")
        self.log_text.config(state="disabled")
        self.run_button.config(state="disabled")

        try:
            convert_tow_ticket_to_all_invoices(
                tow_ticket_file=input_file,
                member_invoice_file=invoice_file,
                vendor_invoice_file=vendor_file
            )
            if not invoice_file.exists():
                raise FileNotFoundError(
                    f"Conversion failed: {invoice_file} not created.")
            if not vendor_file.exists():
                raise FileNotFoundError(
                    f"Conversion failed: {vendor_file} not created.")
            self.after(0, lambda: self._on_conversion_complete(success=True))
        except Exception as e:
            self.after(0, lambda: self._on_conversion_complete(
                success=False, error=str(e)))

    def _append_log(self, message) -> None:
        """Append a message to the log text area."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _on_conversion_complete(self, success: bool, error: str = None) -> None:
        """Callback when conversion thread finishes."""
        self.run_button.config(state="normal")
        if success:
            self._append_log("Conversion complete!\n")
            # Show a dialog with buttons to open the output files

            def open_file(path: str) -> None:
                try:
                    os.startfile(path)
                except AttributeError:
                    if sys.platform == "darwin":
                        subprocess.call(["open", path])
                    else:
                        subprocess.call(["xdg-open", path])

            def show_success_dialog():
                win = tk.Toplevel(self)
                win.title("Conversion Complete")
                win.geometry("400x150")
                tk.Label(win, text="Conversion complete!\n\nYou may now view the output files.",
                         justify="left").pack(pady=(10, 10))
                btn_frame = tk.Frame(win)
                btn_frame.pack(pady=(0, 10))
                tk.Button(btn_frame,
                          text="Open Member Invoice",
                          command=lambda: open_file(
                              str(Path(self.output_entry.get().strip(), "member_invoices.csv")))
                          ).pack(side="left", padx=10)
                tk.Button(btn_frame,
                          text="Open Vendor Invoice",
                          command=lambda: open_file(
                              str(Path(self.output_entry.get().strip(), "vendor_invoices.csv")))
                          ).pack(side="left", padx=10)
                tk.Button(win, text="Close", command=win.destroy).pack(
                    pady=(0, 5))
                win.transient(self)
                win.grab_set()
                self.wait_window(win)

            self.after(0, show_success_dialog)
        else:
            self._append_log(f"\nError: {error}\n")
            messagebox.showerror(
                "Error", f"An error occurred during conversion:\n{error}")


class TextWidgetHandler(logging.Handler):
    def __init__(self, append_func) -> None:
        super().__init__()
        self.append_func = append_func

    def emit(self, record) -> None:
        msg = self.format(record) + "\n"
        # Use after_idle to ensure thread safety with Tkinter
        self.append_func(msg)


if __name__ == "__main__":
    app = CreateInvoicesGUI()
    app.mainloop()
