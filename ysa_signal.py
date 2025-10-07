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

from _version import __version__

# Check if C++ extensions are available
try:
    from helper_functions import (
        process_and_store,
        save_processed_data,
        load_processed_data,
        get_channel_data,
        cpp_available,
    )
except ImportError:
    cpp_available = False
    print("Error: Could not import helper_functions.")
    print("Please run the setup wizard first: python setup_wizard.py")
    sys.exit(1)


def cli_mode(input_file: str, output_file: str, do_analysis: bool = False):
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

    if not cpp_available:
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
        save_processed_data(processed_data=processed_data,
                            output_file=output_file)

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
        print("Error: tkinter not available. Please install tkinter!")
        return 1

    if not cpp_available:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Setup Required",
            "C++ extensions not available.\n\nPlease run the setup wizard first:\npython setup_wizard.py"
        )
        return 1

    class YSASignalGUI:
        def __init__(self, master: tk.Tk):
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
            main_frame.grid(row=0, column=0, sticky="nsew")

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
                             sticky="ew", pady=(0, 10))

            self.input_file = tk.StringVar()
            ttk.Label(input_frame, text="Select raw .brw/.h5 file:").grid(
                row=0, column=0, sticky=tk.W, pady=(0, 5))

            input_entry_frame = ttk.Frame(input_frame)
            input_entry_frame.grid(row=1, column=0, sticky="ew")

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
                              sticky="ew", pady=(0, 20))

            ttk.Label(output_frame, text="Save processed data as:").grid(
                row=0, column=0, sticky=tk.W, pady=(0, 5))

            self.output_file = tk.StringVar()
            output_entry_frame = ttk.Frame(output_frame)
            output_entry_frame.grid(row=1, column=0, sticky="ew")

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
                row=6, column=0, columnspan=2, sticky="nsew")

            # Scrollbar for status
            scrollbar = ttk.Scrollbar(
                main_frame, command=self.status_text.yview)
            scrollbar.grid(row=6, column=2, sticky="ns")
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

            ttk.Label(file_entry_frame, textvariable=self.viewer_file,
                      relief="sunken", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(file_entry_frame, text="Load",
                       command=self.load_viewer_file).pack(side=tk.RIGHT)
            ttk.Button(file_entry_frame, text="Browse...", command=self.browse_viewer_file).pack(
                side=tk.RIGHT, padx=(0, 5))

            # Create horizontal layout: grid on left, plot on right
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill='both', expand=True)

            # Left side: Channel grid (larger)
            left_frame = ttk.Frame(content_frame)
            left_frame.pack(side=tk.LEFT, fill='both',
                            expand=True, padx=(0, 10))

            channel_frame = ttk.LabelFrame(
                left_frame, text="Select Channel", padding="10")
            channel_frame.pack(fill='both', expand=True)

            # Create canvas for grid (fills available space)
            self.grid_canvas = tk.Canvas(
                channel_frame, bg='white', highlightthickness=0)
            self.grid_canvas.pack(fill='both', expand=True, pady=10)

            # Store grid data
            self.grid_cells = {}  # (row, col) -> cell_id
            self.selected_channel = None
            self.selected_cell_id = None
            self.hovered_cell_id = None
            self.hovered_channel = None
            self.all_channels = []

            # Tooltip label
            self.tooltip_label = ttk.Label(
                channel_frame, text="", relief="solid", borderwidth=1, background="lightyellow")

            # Create initial empty grid
            self.create_grid()

            # Right side: Plot area (smaller, fixed width)
            right_frame = ttk.Frame(content_frame, width=500)
            right_frame.pack(side=tk.LEFT, fill='both')
            right_frame.pack_propagate(False)  # Maintain fixed width

            plot_frame = ttk.LabelFrame(
                right_frame, text="Signal", padding="10")
            plot_frame.pack(fill='both', expand=True)

            self.fig = Figure(figsize=(6, 5), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Voltage (V)')
            self.ax.set_title('Select a file and channel to view')
            self.ax.grid(True, alpha=0.3)

            self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
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

        def create_grid(self):
            """Create a 64x64 grid of cells"""
            grid_size = 64

            # Clear existing grid
            self.grid_canvas.delete("all")
            self.grid_cells.clear()

            # Update canvas to get current size
            self.grid_canvas.update()
            canvas_width = self.grid_canvas.winfo_width()
            canvas_height = self.grid_canvas.winfo_height()

            # Calculate cell size to fit canvas (use smaller dimension)
            cell_size = min(canvas_width, canvas_height) / grid_size

            # Calculate offset to center the grid
            grid_pixel_size = grid_size * cell_size
            x_offset = (canvas_width - grid_pixel_size) / 2
            y_offset = (canvas_height - grid_pixel_size) / 2

            # Create 64x64 grid (centered in canvas)
            for row in range(grid_size):
                for col in range(grid_size):
                    x1 = x_offset + col * cell_size
                    y1 = y_offset + row * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size

                    # Create cell (default white/inactive)
                    cell_id = self.grid_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='white',
                        outline='darkgray',
                        width=0.5,
                        tags=('cell', f'r{row}c{col}')
                    )

                    self.grid_cells[(row, col)] = cell_id

            # Bind events
            self.grid_canvas.bind('<Button-1>', self.on_grid_click)
            self.grid_canvas.bind('<Motion>', self.on_grid_hover)
            self.grid_canvas.bind('<Leave>', self.hide_tooltip)
            self.grid_canvas.bind(
                '<Configure>', lambda e: self.create_grid())  # Redraw on resize

        def update_grid_for_channels(self):
            """Update grid to show only active channels"""
            # Reset all cells to white (active)
            for (row, col), cell_id in self.grid_cells.items():
                self.grid_canvas.itemconfig(cell_id, fill='white')

            # Highlight active channels in black
            for row, col in self.all_channels:
                if (row, col) in self.grid_cells:
                    cell_id = self.grid_cells[(row, col)]
                    self.grid_canvas.itemconfig(cell_id, fill='black')

        def on_grid_click(self, event):
            """Handle grid cell click"""
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)

            items = canvas.find_overlapping(x, y, x, y)
            if items:
                tags = canvas.gettags(items[0])
                for tag in tags:
                    if tag.startswith('r') and 'c' in tag:
                        # Parse row and col from tag
                        parts = tag[1:].split('c')
                        if len(parts) == 2:
                            row = int(parts[0])
                            col = int(parts[1])

                            # Check if this is an active channel
                            if (row, col) in self.all_channels:
                                # Deselect previous
                                if self.selected_cell_id:
                                    self.grid_canvas.itemconfig(
                                        self.selected_cell_id, fill='white')

                                # Select new
                                self.selected_channel = (row, col)
                                self.selected_cell_id = self.grid_cells[(
                                    row, col)]
                                self.grid_canvas.itemconfig(
                                    self.selected_cell_id, fill='green')

                                # Auto-plot
                                self.plot_signal()
                        break

        def on_grid_hover(self, event):
            """Show tooltip and highlight on hover"""
            canvas = event.widget
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)

            items = canvas.find_overlapping(x, y, x, y)
            if items:
                tags = canvas.gettags(items[0])
                for tag in tags:
                    if tag.startswith('r') and 'c' in tag:
                        # Parse row and col from tag
                        parts = tag[1:].split('c')
                        if len(parts) == 2:
                            row = int(parts[0])
                            col = int(parts[1])

                            # Update hover highlight
                            if (row, col) != self.hovered_channel:
                                # Unhighlight previous hover
                                if self.hovered_cell_id and self.hovered_channel != self.selected_channel:
                                    prev_row, prev_col = self.hovered_channel
                                    if self.hovered_channel in self.all_channels:
                                        self.grid_canvas.itemconfig(
                                            self.hovered_cell_id, fill='black')
                                    else:
                                        self.grid_canvas.itemconfig(
                                            self.hovered_cell_id, fill='white')

                                # Highlight current hover (only if not selected)
                                if (row, col) != self.selected_channel:
                                    cell_id = self.grid_cells[(row, col)]
                                    if (row, col) in self.all_channels:
                                        self.grid_canvas.itemconfig(
                                            cell_id, fill='lightblue')
                                    else:
                                        self.grid_canvas.itemconfig(
                                            cell_id, fill='gray')
                                    self.hovered_cell_id = cell_id
                                    self.hovered_channel = (row, col)

                            # Show tooltip
                            self.show_tooltip(event, row, col)
                        break
            else:
                self.clear_hover()
                self.hide_tooltip()

        def show_tooltip(self, event, row, col):
            """Display tooltip with channel coordinates"""
            self.tooltip_label.config(text=f"({row + 1}, {col + 1})")
            # Position tooltip near mouse cursor (offset slightly to avoid blocking)
            # Get canvas position relative to its parent
            canvas_x = self.grid_canvas.winfo_x()
            canvas_y = self.grid_canvas.winfo_y()
            x = canvas_x + event.x + 10
            y = canvas_y + event.y - 20
            self.tooltip_label.place(x=x, y=y)
            self.tooltip_label.lift()

        def hide_tooltip(self, event=None):
            """Hide tooltip"""
            self.tooltip_label.place_forget()

        def clear_hover(self):
            """Clear hover highlight"""
            if self.hovered_cell_id and self.hovered_channel != self.selected_channel:
                if self.hovered_channel in self.all_channels:
                    self.grid_canvas.itemconfig(
                        self.hovered_cell_id, fill='black')
                else:
                    self.grid_canvas.itemconfig(
                        self.hovered_cell_id, fill='white')
            self.hovered_cell_id = None
            self.hovered_channel = None

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
                self.update_grid_for_channels()

                # Select first channel by default
                if self.all_channels:
                    self.selected_channel = self.all_channels[0]
                    self.selected_cell_id = self.grid_cells.get(
                        self.all_channels[0])
                    if self.selected_cell_id:
                        self.grid_canvas.itemconfig(
                            self.selected_cell_id, fill='green')

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
