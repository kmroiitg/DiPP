import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.fft import fft, fftfreq
from scipy.signal import savgol_filter
import numpy as np
import os
import sys
import json
import webbrowser


class THzAnalysisGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DiPP 7.0")

                # Add a top-level menu bar
        menu_bar = tk.Menu(master)
        master.config(menu=menu_bar)

        # Add Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How To Manual", command=self.show_manual)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        # Add Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_checkbutton(label="Dark Mode", command=self.toggle_dark_mode)
        settings_menu.add_command(label="Advanced", command=self.open_advanced_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)


        # Create a frame for plots to keep the GUI layout fixed
        self.plot_frame = tk.Frame(master)
        self.plot_frame.grid(row=0, column=9, rowspan=11, columnspan=4, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(9, weight=1)  # Adjust grid position as needed

        # GUI elements
        self.label_ref = tk.Label(master, text="Reference File:")
        self.label_sample = tk.Label(master, text="Sample File:")
        self.label_title = tk.Label(master, text="Title:")
        self.label_save_path = tk.Label(master, text="Save Path:")

        self.entry_ref = tk.Entry(master)
        self.entry_sample = tk.Entry(master)
        self.entry_title = tk.Entry(master)
        self.entry_save_path = tk.Entry(master)

        self.label_freq = tk.Label(master, text="Frequency Range (THz):")
        self.label_time_ref = tk.Label(master, text="Reference Time Range (ps):")
        self.label_time_sample = tk.Label(master, text="Sample Time Range (ps):")
        self.label_increment = tk.Label(master, text="Increment Step (ps):")  # New Label for Increment Value
        self.label_w_p = tk.Label(master, text="Savgol-Filter Parameters (w/p):")

        self.label_time_step = tk.Label(master, text="Time Step (ps):")   #time step displayer
        self.entry_time_step = tk.Entry(master, width=8, state='readonly')
        self.label_time_step.grid(row=4, column=6)
        self.entry_time_step.grid(row=4, column=7)

        self.label_padding = tk.Label(master, text="FFT Padding:")
        self.padding_var = tk.StringVar()
        self.padding_var.set("No Zero Pad")  # default option
        self.dropdown_padding = tk.OptionMenu(master, self.padding_var, "No Zero Pad", "1 GHz Zero Pad")

        self.label_padding.grid(row=5, column=7)
        self.dropdown_padding.grid(row=5, column=8)



        self.entry_freq1 = tk.Entry(master)
        self.entry_freq1.insert(0, "0.2")
        self.entry_freq2 = tk.Entry(master)
        self.entry_freq2.insert(0, "2")

        self.entry_time_ref_start = tk.Entry(master, width=8)
        self.entry_time_ref_start.insert(0, "0")  # Time Start is Fixed
        self.entry_time_ref_end = tk.Entry(master, width=8)
        self.entry_time_ref_end.insert(0, "699")

        self.entry_time_sample_start = tk.Entry(master, width=8)
        self.entry_time_sample_start.insert(0, "0")  # Time Start is Fixed
        self.entry_time_sample_end = tk.Entry(master, width=8)
        self.entry_time_sample_end.insert(0, "699")

        # Inside __init__ function, after defining entry_time_ref_start and entry_time_ref_end
        self.entry_time_ref_start.bind("<KeyRelease>", lambda event: self.auto_fill_sample_time())
        self.entry_time_ref_end.bind("<KeyRelease>", lambda event: self.auto_fill_sample_time())

        self.entry_increment = tk.Entry(master, width=8)  # New Entry for Increment Step
        self.entry_increment.insert(0, "0.1")  # Default step is 10 ps
        self.entry_w = tk.Entry(master)
        self.entry_p = tk.Entry(master)

        self.entry_w = tk.Entry(master)
        self.entry_w.insert(0, "3")
        self.entry_p = tk.Entry(master)
        self.entry_p.insert(0, "2")

        self.button_inc_ref = tk.Button(master, text="+", command=lambda: self.adjust_time(self.entry_time_ref_end, True))
        self.button_dec_ref = tk.Button(master, text="-", command=lambda: self.adjust_time(self.entry_time_ref_end, False))
        self.button_inc_sample = tk.Button(master, text="+", command=lambda: self.adjust_time(self.entry_time_sample_end, True))
        self.button_dec_sample = tk.Button(master, text="-", command=lambda: self.adjust_time(self.entry_time_sample_end, False))

        self.button_browse_ref = tk.Button(master, text="Browse", command=self.browse_ref)
        self.button_browse_sample = tk.Button(master, text="Browse", command=self.browse_sample)
        self.button_browse_save_path = tk.Button(master, text="Browse", command=self.browse_save_path)
        self.button_run = tk.Button(master, text="Run Analysis", command=self.run_analysis)
        self.button_overlay = tk.Button(master, text="Overlay Transmission Graphs", command=self.overlay_transmission_graphs)
        self.button_reset = tk.Button(master, text="Reset Graphs", command=self.reset_graphs)

        # Layout
        self.label_ref.grid(row=0, column=0)
        self.label_sample.grid(row=1, column=0)
        self.label_title.grid(row=2, column=0)
        self.label_save_path.grid(row=3, column=0)

        self.entry_ref.grid(row=0, column=1)
        self.entry_sample.grid(row=1, column=1)
        self.entry_title.grid(row=2, column=1)
        self.entry_save_path.grid(row=3, column=1)

        self.button_browse_ref.grid(row=0, column=2)
        self.button_browse_sample.grid(row=1, column=2)
        self.button_browse_save_path.grid(row=3, column=2)

        self.label_freq.grid(row=4, column=0, columnspan=2)
        self.label_time_ref.grid(row=5, column=0, columnspan=2)
        self.label_time_sample.grid(row=6, column=0, columnspan=2)
        self.label_w_p.grid(row=7, column=0, columnspan=2)
        #self.label_increment.grid(row=5, column=4)  # Label for Increment Step

        self.entry_freq1.grid(row=4, column=2,columnspan=2)
        self.entry_freq2.grid(row=4, column=3,columnspan=2)

        self.entry_time_ref_start.grid(row=5, column=2)
        self.entry_time_ref_end.grid(row=5, column=3)
        self.button_dec_ref.grid(row=5, column=4)  # Decrease Time End
        self.button_inc_ref.grid(row=5, column=5)  # Increase Time End

        self.entry_time_sample_start.grid(row=6, column=2)
        self.entry_time_sample_end.grid(row=6, column=3)
        self.button_dec_sample.grid(row=6, column=4)  # Decrease Time End
        self.button_inc_sample.grid(row=6, column=5)  # Increase Time End

        # Buttons for adjusting both reference & sample time end values simultaneously
        self.button_inc_both = tk.Button(master, text="++", command=lambda: self.adjust_time(None, True, both=True))
        self.button_dec_both = tk.Button(master, text="--", command=lambda: self.adjust_time(None, False, both=True))

        # Position the new ++ and -- buttons
        self.button_inc_both.grid(row=6, column=6)  # Increase Both Time Ends
        self.button_dec_both.grid(row=6, column=7)  # Decrease Both Time Ends

        self.entry_w.grid(row=7, column=2,columnspan=2)
        self.entry_p.grid(row=7, column=3,columnspan=2)

        self.entry_increment.grid(row=5, column=6)  # Entry Field for Increment Step

        self.button_run.grid(row=9, column=0, columnspan=4)
        self.button_overlay.grid(row=10, column=0, columnspan=2)
        self.button_reset.grid(row=10, column=2, columnspan=2)

        self.button_save_data = tk.Button(master, text="Save Data", command=self.save_data)
        self.button_save_data.grid(row=9, column=3, columnspan=2)

        self.overlay_transmission_data = []  # Store data for overlaying transmission graphs
        self.overlay_transmission_fit_data = [] # Store data for overlaying transmission fit graphs
        self.dark_mode = False
        self.data_begin = 6

        self.dark_mode = False  # Dark mode flag
        self.data_begin = 6     # Default header skip lines
        self.load_settings()
        if self.dark_mode:
            self.toggle_dark_mode()
        # Apply settings to entry fields if loaded
        self.entry_time_ref_start.delete(0, tk.END)
        self.entry_time_ref_start.insert(0, getattr(self, "time_ref_start_val", "0"))
        self.entry_time_ref_end.delete(0, tk.END)
        self.entry_time_ref_end.insert(0, getattr(self, "time_ref_end_val", "699"))
        self.entry_time_sample_start.delete(0, tk.END)
        self.entry_time_sample_start.insert(0, getattr(self, "time_sample_start_val", "0"))
        self.entry_time_sample_end.delete(0, tk.END)
        self.entry_time_sample_end.insert(0, getattr(self, "time_sample_end_val", "699"))
        self.entry_freq1.delete(0, tk.END)
        self.entry_freq1.insert(0, getattr(self, "freq1_val", "0.2"))
        self.entry_freq2.delete(0, tk.END)
        self.entry_freq2.insert(0, getattr(self, "freq2_val", "2"))
        self.entry_w.delete(0, tk.END)
        self.entry_w.insert(0, getattr(self, "w_val", "3"))
        self.entry_p.delete(0, tk.END)
        self.entry_p.insert(0, getattr(self, "p_val", "2"))



    def browse_ref(self):
        file_path = filedialog.askopenfilename()
        self.entry_ref.delete(0, tk.END)
        self.entry_ref.insert(0, file_path)
        # Load Reference File Efficiently (Skipping Header Lines)
        data_begin = 6
        self.ref = open(self.entry_ref.get())
        self.time_ref_full, self.voltage_ref_full = np.loadtxt(self.entry_ref.get(), skiprows=self.data_begin-1, unpack=True)

    def browse_sample(self):
        file_path = filedialog.askopenfilename()
        self.entry_sample.delete(0, tk.END)
        self.entry_sample.insert(0, file_path)
        # Load Sample File Efficiently (Skipping Header Lines)
        data_begin = 6
        self.sample = open(self.entry_sample.get())
        self.time_sample_full, self.voltage_sample_full = np.loadtxt(self.entry_sample.get(), skiprows=self.data_begin-1, unpack=True)

        T = np.abs(np.mean(np.diff(self.time_sample_full)))
        self.entry_time_step.configure(state='normal')
        self.entry_time_step.delete(0, tk.END)
        self.entry_time_step.insert(0, f"{T:.4f}")
        self.entry_time_step.configure(state='readonly')

        print(self.time_sample_full)

    def browse_save_path(self):
        folder_path = filedialog.askdirectory()
        self.entry_save_path.delete(0, tk.END)
        self.entry_save_path.insert(0, folder_path)


    def adjust_time(self, entry_field, increase=True, both=False):
        """Adjusts the Time End values for either a single entry or both sample & reference simultaneously."""
        try:
            step = float(self.entry_increment.get())  # Get the user-defined increment step
            
            if both:
                # Adjust BOTH sample and reference time_end
                current_ref = float(self.entry_time_ref_end.get())
                current_sample = float(self.entry_time_sample_end.get())

                if increase:
                    new_ref = current_ref + step
                    new_sample = current_sample + step
                else:
                    new_ref = max(float(self.entry_time_ref_start.get()), current_ref - step)
                    new_sample = max(float(self.entry_time_sample_start.get()), current_sample - step)

                # Update both fields
                self.entry_time_ref_end.delete(0, tk.END)
                self.entry_time_ref_end.insert(0, float(round(new_ref, 3)))

                self.entry_time_sample_end.delete(0, tk.END)
                self.entry_time_sample_end.insert(0, float(round(new_sample, 3)))

            else:
                # Adjust SINGLE time_end (Reference OR Sample)
                current_value = float(entry_field.get())

                if increase:
                    new_value = current_value + step
                else:
                    new_value = max(float(entry_field.master.grid_slaves(row=entry_field.grid_info()['row'], column=2)[0].get()), current_value - step)

                # Update the specified field
                entry_field.delete(0, tk.END)
                entry_field.insert(0, float(round(new_value, 3)))

            # Auto-update the graph after every increment/decrement
            self.run_analysis()

        except ValueError:
            messagebox.showerror("Error", "Invalid increment value. Enter a valid number.")

    # Define the auto_fill_sample_time function
    def auto_fill_sample_time(self):
        """Auto-fills the sample time range based on the reference time range"""
        try:
            ref_start = float(self.entry_time_ref_start.get())
            ref_end = float(self.entry_time_ref_end.get())

            self.entry_time_sample_start.delete(0, tk.END)
            self.entry_time_sample_start.insert(0, ref_start)

            self.entry_time_sample_end.delete(0, tk.END)
            self.entry_time_sample_end.insert(0, ref_end)
        
        except ValueError:
            # Ignore if input is invalid (e.g., empty fields or non-numeric input)
            pass


    def run_analysis(self):
        try:
            # Get parameters from the GUI entries
            self.freq1 = float(self.entry_freq1.get())
            self.freq2 = float(self.entry_freq2.get())
            self.ref_start = float(self.entry_time_ref_start.get())
            self.ref_end = float(self.entry_time_ref_end.get())
            self.sample_start = float(self.entry_time_sample_start.get())
            self.sample_end = float(self.entry_time_sample_end.get())
            self.w = int(self.entry_w.get())
            self.p = int(self.entry_p.get())

            # **Use np.searchsorted() for Faster Index Lookup**
            ref_start_idx = np.searchsorted(self.time_ref_full, self.ref_start, side="left")
            ref_end_idx = np.searchsorted(self.time_ref_full, self.ref_end, side="right")

            sample_start_idx = np.searchsorted(self.time_sample_full, self.sample_start, side="left")
            sample_end_idx = np.searchsorted(self.time_sample_full, self.sample_end, side="right")

            # **Slice Data Using Found Indices (Faster than Boolean Masking)**
            self.time_ref = self.time_ref_full[ref_start_idx:ref_end_idx]
            self.voltage_ref = self.voltage_ref_full[ref_start_idx:ref_end_idx]

            self.time_sample = self.time_sample_full[sample_start_idx:sample_end_idx]
            self.voltage_sample = self.voltage_sample_full[sample_start_idx:sample_end_idx]

            # Time step in seconds (from ps)
            T_ps = np.abs(np.mean(np.diff(self.time_sample_full)))
            T = T_ps * 1e-12  # convert to seconds

            # User selection
            padding_mode = self.padding_var.get()

            if padding_mode == "1 GHz Zero Pad":
                target_resolution = 1e9  # 1 GHz
                required_total_points = int(np.ceil(1 / (target_resolution * T)))
                current_points_ref = len(self.voltage_ref)
                current_points_sam = len(self.voltage_sample)
                zeros_to_pad_ref = max(0, required_total_points - current_points_ref)
                zeros_to_pad_sam = max(0, required_total_points - current_points_sam)

                zero_pad_ref = np.zeros(zeros_to_pad_ref)
                zero_pad_sample = np.zeros(zeros_to_pad_sam)
                self.voltage_ref_padded = np.concatenate((self.voltage_ref, zero_pad_ref))
                self.voltage_sample_padded = np.concatenate((self.voltage_sample, zero_pad_sample))
            else:
                # No padding
                self.voltage_ref_padded = self.voltage_ref
                self.voltage_sample_padded = self.voltage_sample


            T   = np.abs(np.mean(np.diff(self.time_sample_full)))
            N = len(self.voltage_sample_padded)  # Number of sample points
            # Compute frequency array
            self.xf = fftfreq(N, T)[:N // 2]

            # Use np.searchsorted() for faster index lookup
            index1 = np.searchsorted(self.xf, self.freq1, side="left")
            index2 = np.searchsorted(self.xf, self.freq2, side="right")

            # Slice the frequency array
            self.xf_sliced = self.xf[index1:index2]

            y1 = self.voltage_ref_padded
            y2 = self.voltage_sample_padded

            yf1 = np.fft.rfft(y1)
            yf2 = np.fft.rfft(y2)

            self.trans = np.divide(np.abs(yf2[index1:index2]), np.abs(yf1[index1:index2]), where=np.abs(yf1[index1:index2]) != 0)

            self.trans_fit = savgol_filter(self.trans, self.w, polyorder=self.p, deriv=0)

            self.fft_phase_ref = np.angle(yf1[index1:index2])
            self.fft_phase_sam = np.angle(yf2[index1:index2])

            # Store data for overlaying transmission graphs
            self.overlay_transmission_data.append((self.xf_sliced, self.trans, self.entry_title.get()))
            self.overlay_transmission_fit_data.append((self.xf_sliced, self.trans_fit, self.entry_title.get() + str(self.w) + '/' + str(self.p)))

            self.display_plots()

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_plots(self):
        Title = self.entry_title.get()
        save_path = self.entry_save_path.get()

            # Clear previous plots
        for widget in self.plot_frame.winfo_children():
         widget.destroy()

        plt.style.use("dark_background" if self.dark_mode else "default")
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        canvas_widget.bind("<Configure>", lambda event: canvas.draw())    

        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack()

        ax[0].plot(self.time_ref, self.voltage_ref)
        ax[0].plot(self.time_sample, self.voltage_sample)
        ax[0].legend(['Reference [' + str(self.ref_start) + '-' + str(self.ref_end) + ']', 'Sample [' + str(self.sample_start) + '-' + str(self.sample_end) + ']'], loc='upper right')
        ax[0].set_xlabel('Time (ps)')
        ax[0].set_ylabel('Amplitude')
        ax[0].set_xlim(self.ref_start,self.ref_end)
        ax[0].axhline(y=0, linestyle='--', color='darkgray', linewidth=1)

        ax[1].plot(self.xf_sliced, self.trans, color='darkgray', linewidth=1, label='Exp')
        ax[1].plot(self.xf_sliced, self.trans_fit, label='w/p=' + str(self.w) + '/' + str(self.p))
        ax[1].set_xlabel('Frequency (THz)')
        ax[1].legend()
        ax[1].set_ylabel('Transmission')
        ax[1].set_xlim(self.freq1, self.freq2)
        ax[1].set_ylim(0, 1.0)
        plt.suptitle(Title)
        plt.tight_layout()

        canvas.draw()
        Title1 = 'td_trans_' + Title + '.png'
        s_path1 = os.path.join(save_path, Title1)
        canvas.print_figure(s_path1, dpi=600)
        
    def save_data(self):
        Title = self.entry_title.get()
        save_path = self.entry_save_path.get()

        t_data = np.array([self.xf_sliced, self.trans]).T
        t_fitdata = np.array([self.xf_sliced, self.trans_fit]).T
        refphase_data = np.array([self.xf_sliced, self.fft_phase_ref]).T
        samphase_data = np.array([self.xf_sliced, self.fft_phase_sam]).T

        def save_with_prompt(save_path, filename, data):
            full_path = os.path.join(save_path, filename)
            if os.path.exists(full_path):
                overwrite = messagebox.askyesno("File Exists", f"The file '{filename}' already exists.\nDo you want to overwrite it?")
                if not overwrite:
                    messagebox.showinfo("Save Aborted", "Please change the title and try again.")
                    return False
            np.savetxt(full_path, data, delimiter='\t', newline='\n')
            return True

        proceed = True
        proceed &= save_with_prompt(save_path, f"t_{Title}.txt", t_data)
        proceed &= save_with_prompt(save_path, f"t_fit_{Title}.txt", t_fitdata)
        proceed &= save_with_prompt(save_path, f"refphase_{Title}.txt", refphase_data)
        proceed &= save_with_prompt(save_path, f"samphase_{Title}.txt", samphase_data)

        if proceed:
            messagebox.showinfo("Success", "Data saved successfully.")



    
    
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#2e2e2e" if self.dark_mode else "SystemButtonFace"
        fg = "white" if self.dark_mode else "black"

        # Apply to main window and plot frame
        self.master.configure(bg=bg)
        self.plot_frame.configure(bg=bg)

        # Apply to all child widgets
        widgets = self.master.winfo_children() + self.plot_frame.winfo_children()
        for widget in widgets:
            if isinstance(widget, (tk.Label, tk.Button, tk.Entry, tk.Frame, tk.OptionMenu)):
                try:
                    widget.configure(bg=bg, fg=fg)
                    if isinstance(widget, tk.Entry):
                        widget.configure(insertbackground=fg)
                        if widget.cget("state") == "readonly":
                            widget.configure(readonlybackground=bg, fg=fg)
                except:
                    pass

        # Redraw if a plot exists
        for widget in self.plot_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                fig = widget.figure
                fig.patch.set_facecolor(bg)
                for ax in fig.axes:
                    ax.set_facecolor(bg)
                    ax.tick_params(colors=fg)
                    ax.title.set_color(fg)
                    ax.xaxis.label.set_color(fg)
                    ax.yaxis.label.set_color(fg)
                    for spine in ax.spines.values():
                        spine.set_color(fg)
                widget.draw()


    
    def open_advanced_settings(self):
        adv_window = tk.Toplevel(self.master)
        adv_window.title("Advanced Settings")
        adv_window.geometry("350x400")

        # Scrollable canvas inside frame
        canvas = tk.Canvas(adv_window)
        scrollbar = tk.Scrollbar(adv_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- All widgets below added to scrollable_frame ---
        tk.Label(scrollable_frame, text="Header Lines to Skip (data_begin):").pack(pady=5)
        data_begin_entry = tk.Entry(scrollable_frame)
        data_begin_entry.insert(0, str(self.data_begin))
        data_begin_entry.pack()

        tk.Label(scrollable_frame, text="Time Ref Start:").pack()
        time_ref_start_entry = tk.Entry(scrollable_frame)
        time_ref_start_entry.insert(0, self.entry_time_ref_start.get())
        time_ref_start_entry.pack()

        tk.Label(scrollable_frame, text="Time Ref End:").pack()
        time_ref_end_entry = tk.Entry(scrollable_frame)
        time_ref_end_entry.insert(0, self.entry_time_ref_end.get())
        time_ref_end_entry.pack()

        tk.Label(scrollable_frame, text="Time Sample Start:").pack()
        time_sample_start_entry = tk.Entry(scrollable_frame)
        time_sample_start_entry.insert(0, self.entry_time_sample_start.get())
        time_sample_start_entry.pack()

        tk.Label(scrollable_frame, text="Time Sample End:").pack()
        time_sample_end_entry = tk.Entry(scrollable_frame)
        time_sample_end_entry.insert(0, self.entry_time_sample_end.get())
        time_sample_end_entry.pack()

        tk.Label(scrollable_frame, text="Frequency Start (THz):").pack()
        freq1_entry = tk.Entry(scrollable_frame)
        freq1_entry.insert(0, self.entry_freq1.get())
        freq1_entry.pack()

        tk.Label(scrollable_frame, text="Frequency End (THz):").pack()
        freq2_entry = tk.Entry(scrollable_frame)
        freq2_entry.insert(0, self.entry_freq2.get())
        freq2_entry.pack()

        tk.Label(scrollable_frame, text="Savgol Filter Window (w):").pack()
        w_entry = tk.Entry(scrollable_frame)
        w_entry.insert(0, self.entry_w.get())
        w_entry.pack()

        tk.Label(scrollable_frame, text="Savgol Filter Order (p):").pack()
        p_entry = tk.Entry(scrollable_frame)
        p_entry.insert(0, self.entry_p.get())
        p_entry.pack()

        def apply_changes():
            try:
                new_value = int(data_begin_entry.get())
                if new_value < 0:
                    raise ValueError
                self.data_begin = new_value

                self.entry_time_ref_start.delete(0, tk.END)
                self.entry_time_ref_start.insert(0, time_ref_start_entry.get())
                self.entry_time_ref_end.delete(0, tk.END)
                self.entry_time_ref_end.insert(0, time_ref_end_entry.get())
                self.entry_time_sample_start.delete(0, tk.END)
                self.entry_time_sample_start.insert(0, time_sample_start_entry.get())
                self.entry_time_sample_end.delete(0, tk.END)
                self.entry_time_sample_end.insert(0, time_sample_end_entry.get())
                self.entry_freq1.delete(0, tk.END)
                self.entry_freq1.insert(0, freq1_entry.get())
                self.entry_freq2.delete(0, tk.END)
                self.entry_freq2.insert(0, freq2_entry.get())
                self.entry_w.delete(0, tk.END)
                self.entry_w.insert(0, w_entry.get())
                self.entry_p.delete(0, tk.END)
                self.entry_p.insert(0, p_entry.get())

                messagebox.showinfo("Success", f"'data_begin' and analysis settings updated.")
                adv_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid non-negative integer.")

        tk.Button(scrollable_frame, text="Apply", command=apply_changes).pack(pady=10)



    
    def load_settings(self):
        settings_path = "settings.json"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    self.data_begin = settings.get("data_begin", 6)
                    self.dark_mode = settings.get("dark_mode", False)
                    self.time_ref_start_val = settings.get("time_ref_start", "0")
                    self.time_ref_end_val = settings.get("time_ref_end", "699")
                    self.time_sample_start_val = settings.get("time_sample_start", "0")
                    self.time_sample_end_val = settings.get("time_sample_end", "699")
                    self.freq1_val = settings.get("freq1", "0.2")
                    self.freq2_val = settings.get("freq2", "2")
                    self.w_val = settings.get("w", "3")
                    self.p_val = settings.get("p", "2")
            except Exception as e:
                messagebox.showwarning("Settings", f"Failed to load settings: {e}")

    def save_settings(self):
        settings = {
            "data_begin": self.data_begin,
            "time_ref_start": self.entry_time_ref_start.get(),
            "time_ref_end": self.entry_time_ref_end.get(),
            "time_sample_start": self.entry_time_sample_start.get(),
            "time_sample_end": self.entry_time_sample_end.get(),
            "freq1": self.entry_freq1.get(),
            "freq2": self.entry_freq2.get(),
            "w": self.entry_w.get(),
            "p": self.entry_p.get(),
            "dark_mode": self.dark_mode
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            messagebox.showwarning("Settings", f"Failed to save settings: {e}")


    def overlay_transmission_graphs(self):
        if not self.overlay_transmission_data:
            if not self.overlay_transmission_fit_data:
                messagebox.showerror("Error", "No transmission data to overlay.")
                return

        # Create a new window for overlay plots
        overlay_window = tk.Toplevel(self.master)
        overlay_window.title("Overlayed Transmission Graphs")

        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=overlay_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        canvas_widget.bind("<Configure>", lambda event: canvas.draw())

        toolbar = NavigationToolbar2Tk(canvas, overlay_window, pack_toolbar=False)
        toolbar.update()
        toolbar.pack()

        # Plot the transmission data
        for xf_sliced, trans, title in self.overlay_transmission_data:
            ax.plot(xf_sliced, trans, label=title)

        ax.set_xlabel('Frequency (THz)')
        ax.set_ylabel('Transmission')
        ax.set_xlim(float(self.entry_freq1.get()), float(self.entry_freq2.get()))
        ax.set_ylim(0, 1.0)
        ax.legend()
        plt.suptitle("Overlayed Transmission Graphs")
        plt.tight_layout()

        # Create a new window for overlay fit plots
        overlay_window_fit = tk.Toplevel(self.master)
        overlay_window.title("Overlayed Transmission Fit Graphs")

        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=overlay_window_fit)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        canvas_widget.bind("<Configure>", lambda event: canvas.draw())

        toolbar = NavigationToolbar2Tk(canvas, overlay_window_fit, pack_toolbar=False)
        toolbar.update()
        toolbar.pack()

        # Plot the transmission data
        for xf_sliced, trans_fit, title in self.overlay_transmission_fit_data:
            ax.plot(xf_sliced, trans_fit, label=title)

        ax.set_xlabel('Frequency (THz)')
        ax.set_ylabel('Transmission (Fit)')
        ax.set_xlim(float(self.entry_freq1.get()), float(self.entry_freq2.get()))
        ax.set_ylim(0, 1.1)
        ax.legend()
        plt.suptitle("Overlayed Transmission Fit Graphs")
        plt.tight_layout()

        # Draw the canvas
        canvas.draw()


    def reset_graphs(self):
        self.overlay_transmission_data.clear()
        self.overlay_transmission_fit_data.clear()
        messagebox.showinfo("Reset", "All overlayed graphs have been cleared.")


    def on_closing(self):
        self.save_settings()
        """Handle cleanup and ensure proper program termination."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.destroy()  # Destroys the Tkinter root window
            sys.exit()  # Ensures the program exits completely

    def show_manual(self):
        manual_window = tk.Toplevel(self.master)
        manual_window.title("How To Manual")

        text_widget = tk.Text(manual_window, wrap='word', width=100, height=30)
        scrollbar = tk.Scrollbar(manual_window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        howto_text = """
        DiPP v6.0 - How To Manual

        1. Load Reference and Sample Files:
        - Click "Browse" next to each entry.
        - Files must be tab-separated with headers skipped automatically. 
        - Go to settings -> advanced -> headers to set the header rows to be skipped.
        
        2. Set Title and Save Path:
        - Title: Used in saved file names.
        - Save Path: Choose a folder where all outputs go.

        3. Time and Frequency Ranges:
        - Set ranges in picoseconds (ps) and THz.
        - Use +/- buttons to adjust windowing range precisely.
        - +/- moves trims the time signal of each file
        - ++/-- trims the time signal of sample and reference simultaneously. Applicable in most cases.

        4. Smoothing Parameters:
        - w/p = Savgol filter window size and polynomial order.

        5. FFT Padding:
        - "No Zero Pad" = Original length
        - "1 GHz Zero Pad" = Extend with zeros for higher resolution (1 GHz frequency resolution)

        6. Run Analysis:
        - Click “Run Analysis” to generate plots and preview data.
        - Data is NOT saved to disk yet.

        7. Save Data:
        - Click “Save Data” to write transmission & phase data to `.txt`.
        - Prevents accidental overwriting and speeds up execution.

        8. Overlay Graphs:
        - Compare multiple runs using “Overlay Transmission Graphs”.

        9. Reset:
        - Clears all overlayed graphs.

        Built using Python Tkinter & ChatGPT 

        Developed by """
        text_widget.insert(tk.END, howto_text)

        # Add a hyperlink at the end
        link_text = "km.ro"
        text_widget.insert(tk.END, link_text, "link")
        text_widget.tag_config("link", foreground="blue", underline=1)
        text_widget.tag_bind("link", "<Button-1>", lambda e: webbrowser.open_new("https://www.researchgate.net/profile/Rohith-K-M"))

        text_widget.config(state='disabled')






if __name__ == "__main__":
    root = tk.Tk()
    app = THzAnalysisGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Bind the close event
    root.mainloop()
