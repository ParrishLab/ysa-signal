#!/usr/bin/env python3
"""
YSA Signal - Standalone Signal Analyzer

Process .brw/.h5 files and save/load processed data.
Supports both CLI and GUI modes.

Developer: Jake Cahoon
"""

import os
import sys
import argparse

# Check if C++ extensions are available
try:
    from helper_functions import (
        process_and_store,
        save_processed_data,
        load_processed_data,
        get_channel_data,
        CPP_AVAILABLE,
    )
except ImportError:
    CPP_AVAILABLE = False
    print("Error: Could not import helper_functions.")
    print("Please run the setup wizard first: python setup_wizard.py")
    sys.exit(1)


def cli_mode(input_file, output_file, do_analysis=False):
    """
    Run in CLI mode.

    Args:
        input_file: Input file path (.brw/.h5)
        output_file: Output file path (.h5)
        do_analysis: Whether to perform seizure/SE analysis
    """
    print("=" * 70)
    print("YSA Signal - CLI Mode")
    print("=" * 70)

    if not CPP_AVAILABLE:
        print("\nError: C++ extensions not available.")
        print("Please run the setup wizard: python setup_wizard.py")
        return 1

    try:
        # Process raw file
        print(f"\nProcessing file: {input_file}")
        print(f"Analysis enabled: {do_analysis}")

        processed_data = process_and_store(
            input_file, do_analysis=do_analysis)

        # Save processed data
        save_processed_data(processed_data, output_file)

        print("\n" + "=" * 70)
        print("Processing complete!")
        print("=" * 70)
        print(f"\nOutput file: {output_file}")
        print(f"Channels processed: {len(processed_data.active_channels)}")
        print(
            f"Recording length: {processed_data.recording_length:.2f} seconds")
        print(f"Sampling rate: {processed_data.sampling_rate} Hz")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


def gui_mode():
    """Run in GUI mode with tkinter"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("Error: tkinter not available. Please install tkinter.")
        return 1

    if not CPP_AVAILABLE:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Setup Required",
            "C++ extensions not available.\n\nPlease run the setup wizard first:\npython setup_wizard.py"
        )
        return 1

    class YSASignalGUI:
        def __init__(self, master):
            self.master = master
            master.title("YSA Signal Analyzer")

            # Calculate screen size and set window to fullscreen with margin
            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()
            margin = 100
            window_width = screen_width - (2 * margin)
            window_height = screen_height - (2 * margin)
            x_position = margin
            y_position = margin

            master.geometry(
                f"{window_width}x{window_height}+{x_position}+{y_position}")
            master.resizable(True, True)

            # Create notebook (tabbed interface)
            self.notebook = ttk.Notebook(master)
            self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

            # Create tabs
            self.process_tab = ttk.Frame(self.notebook)
            self.viewer_tab = ttk.Frame(self.notebook)

            self.notebook.add(self.process_tab, text="Process Files")
            self.notebook.add(self.viewer_tab, text="View Signals")

            # Initialize tabs
            self.init_process_tab()
            self.init_viewer_tab()

        def init_process_tab(self):
            """Initialize the process files tab"""
            main_frame = ttk.Frame(self.process_tab, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Title
            title = ttk.Label(main_frame, text="YSA Signal Analyzer",
                              font=("Helvetica", 20, "bold"))
            title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

            # Subtitle
            subtitle = ttk.Label(main_frame,
                                 text="Process .brw/.h5 files",
                                 font=("Helvetica", 10))
            subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 30))

            # Input file selection
            input_frame = ttk.LabelFrame(
                main_frame, text="Input File", padding="10")
            input_frame.grid(row=3, column=0, columnspan=2,
                             sticky=(tk.W, tk.E), pady=(0, 10))

            self.input_file = tk.StringVar()
            ttk.Label(input_frame, text="Select raw .brw/.h5 file:").grid(
                row=0, column=0, sticky=tk.W, pady=(0, 5))

            input_entry_frame = ttk.Frame(input_frame)
            input_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

            ttk.Label(input_entry_frame, textvariable=self.input_file,
                      relief="sunken", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(input_entry_frame, text="Browse...",
                       command=self.browse_input).pack(side=tk.RIGHT, padx=(5, 0))

            # Analysis option
            analysis_frame = ttk.Frame(main_frame)
            analysis_frame.grid(
                row=3, column=0, columnspan=2, pady=(0, 10))

            self.do_analysis = tk.BooleanVar(value=False)
            ttk.Checkbutton(analysis_frame,
                            text="Perform seizure/SE detection analysis",
                            variable=self.do_analysis).pack(anchor=tk.W)

            # Output file selection
            output_frame = ttk.LabelFrame(
                main_frame, text="Output File", padding="10")
            output_frame.grid(row=4, column=0, columnspan=2,
                              sticky=(tk.W, tk.E), pady=(0, 20))

            ttk.Label(output_frame, text="Save processed data as:").grid(
                row=0, column=0, sticky=tk.W, pady=(0, 5))

            self.output_file = tk.StringVar()
            output_entry_frame = ttk.Frame(output_frame)
            output_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

            ttk.Label(output_entry_frame, textvariable=self.output_file,
                      relief="sunken", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(output_entry_frame, text="Browse...",
                       command=self.browse_output).pack(side=tk.RIGHT, padx=(5, 0))

            # Process button
            self.process_button = ttk.Button(main_frame, text="Process File",
                                             command=self.process_file)
            self.process_button.grid(
                row=5, column=0, columnspan=2, pady=(0, 10))

            # Progress/Status
            self.status_text = tk.Text(
                main_frame, height=10, width=70, state='disabled')
            self.status_text.grid(
                row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Scrollbar for status
            scrollbar = ttk.Scrollbar(
                main_frame, command=self.status_text.yview)
            scrollbar.grid(row=6, column=2, sticky=(tk.N, tk.S))
            self.status_text['yscrollcommand'] = scrollbar.set

            # Configure grid weights
            self.process_tab.columnconfigure(0, weight=1)
            self.process_tab.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(6, weight=1)
            input_frame.columnconfigure(0, weight=1)
            output_frame.columnconfigure(0, weight=1)

            self.log("Ready. Select a file to process.")

        def init_viewer_tab(self):
            """Initialize the signal viewer tab"""
            try:
                import matplotlib
                matplotlib.use('TkAgg')
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                from matplotlib.figure import Figure
                self.matplotlib_available = True
            except ImportError:
                self.matplotlib_available = False

            main_frame = ttk.Frame(self.viewer_tab, padding="20")
            main_frame.pack(fill='both', expand=True)

            if not self.matplotlib_available:
                ttk.Label(main_frame, text="Matplotlib not available. Please install it to view signals.",
                          font=("Helvetica", 12)).pack(pady=20)
                return

            # File selection
            file_frame = ttk.LabelFrame(
                main_frame, text="Load Processed File", padding="10")
            file_frame.pack(fill='x', pady=(0, 10))

            self.viewer_file = tk.StringVar()
            file_entry_frame = ttk.Frame(file_frame)
            file_entry_frame.pack(fill='x')

            ttk.Entry(file_entry_frame, textvariable=self.viewer_file).pack(
                side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(file_entry_frame, text="Browse...", command=self.browse_viewer_file).pack(
                side=tk.RIGHT, padx=(5, 0))
            ttk.Button(file_entry_frame, text="Load",
                       command=self.load_viewer_file).pack(side=tk.RIGHT)

            # Channel selection with fuzzy search
            channel_frame = ttk.LabelFrame(
                main_frame, text="Select Channel", padding="10")
            channel_frame.pack(fill='x', pady=(0, 10))

            ttk.Label(channel_frame, text="Search:").pack(
                side=tk.LEFT, padx=(0, 5))

            self.channel_search = tk.StringVar()
            self.channel_search.trace('w', self.filter_channels)
            search_entry = ttk.Entry(
                channel_frame, textvariable=self.channel_search, width=15)
            search_entry.pack(side=tk.LEFT, padx=(0, 10))

            # Listbox for filtered channels
            list_frame = ttk.Frame(channel_frame)
            list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.channel_listbox = tk.Listbox(
                list_frame, height=5, exportselection=False)
            self.channel_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.channel_listbox.bind(
                '<<ListboxSelect>>', self.on_channel_select)
            self.channel_listbox.bind(
                '<Double-Button-1>', lambda e: self.plot_signal())

            list_scrollbar = ttk.Scrollbar(
                list_frame, command=self.channel_listbox.yview)
            list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.channel_listbox.config(yscrollcommand=list_scrollbar.set)

            ttk.Button(channel_frame, text="Plot Signal", command=self.plot_signal).pack(
                side=tk.LEFT, padx=(10, 0))

            # Store all channels and selected channel
            self.all_channels = []
            self.selected_channel = None

            # Plot area
            self.fig = Figure(figsize=(8, 5), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Voltage (V)')
            self.ax.set_title('Select a file and channel to view')
            self.ax.grid(True, alpha=0.3)

            self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)

            # Store loaded data
            self.viewer_data = None

        def browse_input(self):
            """Browse for input file"""
            filetypes = [("BRW/H5 files", "*.brw *.h5"),
                         ("All files", "*.*")]

            filename = filedialog.askopenfilename(
                title="Select Input File",
                filetypes=filetypes
            )
            if filename:
                self.input_file.set(filename)

                # Auto-suggest output filename
                base = os.path.splitext(filename)[0]
                self.output_file.set(f"{base}_processed.h5")

        def browse_output(self):
            """Browse for output file"""
            filename = filedialog.asksaveasfilename(
                title="Save Processed Data As",
                defaultextension=".h5",
                filetypes=[("H5 files", "*.h5"), ("All files", "*.*")]
            )
            if filename:
                self.output_file.set(filename)

        def log(self, message):
            """Log message to status text"""
            self.status_text.config(state='normal')
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state='disabled')
            self.master.update()

        def process_file(self):
            """Process the selected file"""
            input_file = self.input_file.get()
            output_file = self.output_file.get()

            if not input_file:
                messagebox.showerror("Error", "Please select an input file.")
                return

            if not output_file:
                messagebox.showerror("Error", "Please select an output file.")
                return

            if not os.path.exists(input_file):
                messagebox.showerror(
                    "Error", f"Input file not found: {input_file}")
                return

            # Disable button during processing
            self.process_button.config(state='disabled')
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state='disabled')

            try:
                self.log(f"Processing file: {input_file}")
                self.log(f"Analysis enabled: {self.do_analysis.get()}")
                self.log("Please wait, this may take a few minutes...")
                self.log("")

                # Suppress stdout during processing
                import io
                import sys
                from contextlib import redirect_stdout, redirect_stderr

                old_stdout = sys.stdout
                old_stderr = sys.stderr

                try:
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    processed_data = process_and_store(
                        input_file,
                        do_analysis=self.do_analysis.get()
                    )
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                self.log(
                    f"Processing complete! Processed {len(processed_data.active_channels)} channels.")
                self.log("")
                self.log(f"Saving processed data to: {output_file}")

                try:
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    save_processed_data(processed_data, output_file)
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                self.log("Successfully saved processed data")

                self.log("\n" + "=" * 60)
                self.log("Processing complete!")
                self.log("=" * 60)
                self.log(f"Output file: {output_file}")
                self.log(
                    f"Channels processed: {len(processed_data.active_channels)}")
                self.log(
                    f"Recording length: {processed_data.recording_length:.2f} seconds")
                self.log(f"Sampling rate: {processed_data.sampling_rate} Hz")

                messagebox.showinfo("Success", "Processing complete!")

            except Exception as e:
                self.log(f"\nError: {e}")
                import traceback
                self.log(traceback.format_exc())
                messagebox.showerror("Error", f"An error occurred:\n{e}")

            finally:
                self.process_button.config(state='normal')

        def filter_channels(self, *args):
            """Filter channel list based on search text"""
            search_text = self.channel_search.get().lower()

            # Clear listbox
            self.channel_listbox.delete(0, tk.END)

            # Filter and display channels
            for row, col in self.all_channels:
                channel_str = f"({row}, {col})"
                search_str = f"{row}{col}"

                # Fuzzy match: check if all characters in search appear in order
                if not search_text or self.fuzzy_match(search_text, search_str):
                    self.channel_listbox.insert(tk.END, channel_str)

        def fuzzy_match(self, pattern, text):
            """Simple fuzzy matching: all chars in pattern must appear in order in text"""
            pattern_idx = 0
            for char in text:
                if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                    pattern_idx += 1
            return pattern_idx == len(pattern)

        def on_channel_select(self, event):
            """Handle channel selection from listbox"""
            selection = self.channel_listbox.curselection()
            if selection:
                selected_text = self.channel_listbox.get(selection[0])
                # Parse "(row, col)" format
                selected_text = selected_text.strip('()')
                parts = selected_text.split(',')
                if len(parts) == 2:
                    row = int(parts[0].strip())
                    col = int(parts[1].strip())
                    self.selected_channel = (row, col)

        def browse_viewer_file(self):
            """Browse for processed file to view"""
            filename = filedialog.askopenfilename(
                title="Select Processed H5 File",
                filetypes=[("Processed H5 files", "*.h5"),
                           ("All files", "*.*")]
            )
            if filename:
                self.viewer_file.set(filename)

        def load_viewer_file(self):
            """Load processed file for viewing"""
            if not self.matplotlib_available:
                messagebox.showerror("Error", "Matplotlib not available")
                return

            filename = self.viewer_file.get()
            if not filename:
                messagebox.showerror("Error", "Please select a file")
                return

            if not os.path.exists(filename):
                messagebox.showerror("Error", f"File not found: {filename}")
                return

            try:
                # Suppress stdout during loading
                import io
                import sys

                old_stdout = sys.stdout
                old_stderr = sys.stderr

                try:
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    self.viewer_data = load_processed_data(filename)
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                # Populate channel list
                self.all_channels = sorted(self.viewer_data.active_channels)
                self.filter_channels()  # Display all channels initially

                # Select first channel by default
                if self.all_channels:
                    self.selected_channel = self.all_channels[0]
                    self.channel_listbox.selection_set(0)

                messagebox.showinfo("Success",
                                    f"Loaded {len(self.viewer_data.active_channels)} channels\n"
                                    f"Sampling rate: {self.viewer_data.sampling_rate} Hz\n"
                                    f"Recording length: {self.viewer_data.recording_length:.2f} seconds")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

        def plot_signal(self):
            """Plot the selected channel signal"""
            if not self.matplotlib_available:
                messagebox.showerror("Error", "Matplotlib not available")
                return

            if self.viewer_data is None:
                messagebox.showerror("Error", "Please load a file first")
                return

            if self.selected_channel is None:
                messagebox.showerror(
                    "Error", "Please select a channel from the list")
                return

            row, col = self.selected_channel

            try:
                channel_data = get_channel_data(self.viewer_data, row, col)

                if channel_data is None:
                    messagebox.showerror("Error",
                                         f"Channel ({row}, {col}) has no data.\n"
                                         f"Active channels: {len(self.viewer_data.active_channels)}")
                    return

                # Clear previous plot
                self.ax.clear()

                # Plot signal
                signal = channel_data['signal']
                time = self.viewer_data.time_vector[:len(signal)]

                self.ax.plot(time, signal, 'b-', linewidth=0.5, label='Signal')

                # Plot seizure times if available
                if len(channel_data['SzTimes']) > 0:
                    for sz in channel_data['SzTimes']:
                        self.ax.axvspan(sz[0], sz[1], alpha=0.3, color='blue',
                                        label='Seizure' if sz[0] == channel_data['SzTimes'][0][0] else '')

                # Plot SE times if available
                if len(channel_data['SETimes']) > 0:
                    for se in channel_data['SETimes']:
                        self.ax.axvspan(se[0], se[1], alpha=0.3, color='orange',
                                        label='SE' if se[0] == channel_data['SETimes'][0][0] else '')

                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Voltage (V)')
                self.ax.set_title(
                    f'Channel ({row}, {col}) - {len(signal)} samples @ {self.viewer_data.sampling_rate} Hz')
                self.ax.grid(True, alpha=0.3)

                # Add legend if there are events
                if len(channel_data['SzTimes']) > 0 or len(channel_data['SETimes']) > 0 or len(channel_data['DischargeTimes']) > 0:
                    self.ax.legend(loc='upper right')

                self.canvas.draw()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to plot signal:\n{e}")
                import traceback
                traceback.print_exc()

    # Create and run GUI
    root = tk.Tk()

    # Bring window to front and focus
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.focus_force()

    gui = YSASignalGUI(root)
    root.mainloop()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="YSA Signal - Process and analyze .brw/.h5 signal files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a raw file without analysis (default):
  python ysa_signal.py input.brw output_processed.h5

  # Process with analysis:
  python ysa_signal.py input.brw output_processed.h5 --do-analysis

  # Launch GUI (no arguments):
  python ysa_signal.py
        """
    )

    parser.add_argument('input_file', nargs='?',
                        help='Input file path (.brw/.h5)')
    parser.add_argument('output_file', nargs='?',
                        help='Output file path (.h5)')
    parser.add_argument('--do-analysis', action='store_true',
                        help='Perform seizure/SE detection analysis')

    args = parser.parse_args()

    # Determine mode
    if args.input_file and args.output_file:
        # CLI mode
        return cli_mode(args.input_file, args.output_file,
                        do_analysis=args.do_analysis)
    elif args.input_file or args.output_file:
        print("Error: Both input and output files must be specified for CLI mode.")
        print("Run with --help for usage information.")
        return 1
    else:
        # GUI mode
        return gui_mode()


if __name__ == "__main__":
    sys.exit(main())
