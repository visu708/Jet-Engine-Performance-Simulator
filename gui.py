# ui/gui.py

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Assuming these imports are already available in your project structure
from Engines.turbojet import Turbojet
from Engines.turbofan import Turbofan
from Engines.turboprop import Turboprop
from Engines.turboshaft import Turboshaft
from Engines.ramjet import Ramjet
from Engines.scramjet import Scramjet
from Components.compressor import AxialCompressor, CentrifugalCompressor
from Physics.performance import standard_atmosphere

class EngineSimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Engine Simulator")
        self.geometry("850x900")
        self.configure(bg="#2c3e50")

        # Use a professional ttk theme
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#34495e', foreground='white')
        self.style.configure('TLabel', background='#34495e', foreground='white', font=('Helvetica', 10))
        self.style.configure('TLabelframe', background='#34495e', foreground='white')
        self.style.configure('TLabelframe.Label', background='#34495e', foreground='white', font=('Helvetica', 10, 'bold'))
        self.style.configure('TButton', background='#16a085', foreground='white', font=('Helvetica', 10, 'bold'))
        self.style.map('TButton',
            background=[('active', '#1abc9c')]
        )
        self.style.configure('TEntry', fieldbackground='#ecf0f1', foreground='#34495e')

        self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.heading_font = font.Font(family="Helvetica", size=12, weight="bold")

        self.engine_types = {
            "Turbojet": Turbojet, "Turbofan": Turbofan, "Turboprop": Turboprop,
            "Turboshaft": Turboshaft, "Ramjet": Ramjet, "Scramjet": Scramjet
        }
        self.active_inputs = {}
        self.create_widgets()

    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self, padding="15", style="TFrame")
        header_frame.pack(fill="x", pady=(10, 0), padx=20)
        ttk.Label(header_frame, text="🚀 Jet Engine Performance Simulator 🚀", font=self.title_font, background='#34495e', foreground='#ecf0f1').pack()
        ttk.Label(header_frame, text="An Aerospace Engineering Project", background='#34495e', foreground='#bdc3c7').pack()

        # Selection and Input Frame
        input_container_frame = ttk.Frame(self, padding="15", style="TFrame")
        input_container_frame.pack(pady=10, padx=20, fill="x")

        # Engine Selection
        select_frame = ttk.Frame(input_container_frame, style="TFrame")
        select_frame.pack(pady=10)
        ttk.Label(select_frame, text="Select Engine Type:", font=self.heading_font).pack(side="left")
        self.engine_var = tk.StringVar(self)
        self.engine_var.set("Turbojet")
        engine_menu = ttk.OptionMenu(select_frame, self.engine_var, "Turbojet", *self.engine_types.keys(), command=self.on_engine_select)
        engine_menu.pack(side="left", padx=10)

        self.input_frame = ttk.Frame(input_container_frame, padding="10", style="TFrame")
        self.input_frame.pack(pady=10, padx=10, fill="x")
        self.on_engine_select("Turbojet")
        
        # Run Button
        run_button = ttk.Button(self, text="Run Simulation", command=self.run_simulation, style='TButton')
        run_button.pack(pady=10)

        # Results Notebook (Tabs)
        self.results_notebook = ttk.Notebook(self)
        self.results_notebook.pack(pady=10, padx=20, fill="both", expand=True)

        self.results_text_frame = ttk.Frame(self.results_notebook, style="TFrame")
        self.results_notebook.add(self.results_text_frame, text="Output Metrics")
        self.create_text_results_widget(self.results_text_frame)

        self.results_graph_frame = ttk.Frame(self.results_notebook, style="TFrame")
        self.results_notebook.add(self.results_graph_frame, text="Performance Graphs")

    def create_text_results_widget(self, parent_frame):
        ttk.Label(parent_frame, text="Simulation Results:", font=self.heading_font, background='#34495e', foreground='#ecf0f1').pack(pady=5)
        self.results_text = tk.Text(parent_frame, height=15, width=60, state="disabled", font=("Courier", 10), background='#2c3e50', foreground='white', borderwidth=0, highlightthickness=0)
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)

    def on_engine_select(self, engine_name):
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.active_inputs.clear()

        self.add_input_field("Altitude [m]:", "altitude", "11000")
        self.add_input_field("Mach Number:", "mach", "0.8")
        self.add_input_field("Air Mass Flow [kg/s]:", "mdot_air", "100")

        if engine_name in ["Turbojet", "Turbofan", "Turboprop", "Turboshaft"]:
            self.add_input_field("Tt4 [K]:", "tt4_target", "1500")
            self.add_compressor_inputs()

        if engine_name == "Turbofan":
            self.add_input_field("Bypass Ratio (BPR):", "bpr", "5.0")
            self.add_input_field("Fan PR:", "fan_pr", "1.4")
            self.add_input_field("Fan Eta:", "fan_eta", "0.93")
            
        if engine_name in ["Ramjet", "Scramjet"]:
            self.add_input_field("Tt4 [K]:", "tt4_target", "2000")

    def add_input_field(self, label, key, default=""):
        row = len(self.active_inputs)
        ttk.Label(self.input_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(self.input_frame)
        entry.insert(0, default)
        entry.grid(row=row, column=1, padx=5, pady=2)
        self.active_inputs[key] = entry

    def add_compressor_inputs(self):
        comp_frame = ttk.LabelFrame(self.input_frame, text="Compressor", padding=5)
        comp_frame.grid(row=len(self.active_inputs), column=0, columnspan=2, sticky="ew", pady=5)
        
        self.comp_type = tk.StringVar(self)
        self.comp_type.set("Axial")
        ttk.Radiobutton(comp_frame, text="Axial", variable=self.comp_type, value="Axial", command=self.update_comp_fields, style='TRadiobutton').pack(side="left")
        ttk.Radiobutton(comp_frame, text="Centrifugal", variable=self.comp_type, value="Centrifugal", command=self.update_comp_fields, style='TRadiobutton').pack(side="left")
        
        self.comp_fields_frame = ttk.Frame(comp_frame)
        self.comp_fields_frame.pack(side="top", pady=5)
        self.update_comp_fields()

    def update_comp_fields(self):
        # Clear previous fields from the dictionary
        self.active_inputs.pop('comp_pr', None)
        self.active_inputs.pop('comp_eta', None)
        self.active_inputs.pop('comp_stages', None)
        
        # Destroy all widgets in the comp_fields_frame
        for widget in self.comp_fields_frame.winfo_children():
            widget.destroy()
            
        comp_type = self.comp_type.get()
        if comp_type == "Axial":
            fields = [("Stages:", "comp_stages", "8"), ("PR/stage:", "comp_pr", "1.25"), ("Eta/stage:", "comp_eta", "0.90")]
        else: # Centrifugal
            fields = [("PR:", "comp_pr", "5.0"), ("Eta:", "comp_eta", "0.82")]

        for label_text, key, default in fields:
            ttk.Label(self.comp_fields_frame, text=label_text).pack(side="left", padx=5)
            entry = ttk.Entry(self.comp_fields_frame, width=10)
            entry.insert(0, default)
            entry.pack(side="left", padx=5)
            self.active_inputs[key] = entry
            
    def run_simulation(self):
        try:
            inputs = {key: float(entry.get()) for key, entry in self.active_inputs.items()}
            T0, p0, _ = standard_atmosphere(inputs['altitude'])
            flight_inputs = {'altitude': inputs['altitude'], 'M0': inputs['mach'], 'p0': p0, 'T0': T0}

            engine_name = self.engine_var.get()
            components = {}
            if "comp_pr" in inputs:
                if self.comp_type.get() == "Axial":
                    components['compressor'] = AxialCompressor(n_stages=int(inputs['comp_stages']), pr_stage=inputs['comp_pr'], eta_stage=inputs['comp_eta'])
                else:
                    components['compressor'] = CentrifugalCompressor(pr_stage=inputs['comp_pr'], eta=inputs['comp_eta'])
            
            if engine_name == "Turbofan":
                components['fan'] = AxialCompressor(n_stages=1, pr_stage=inputs['fan_pr'], eta_stage=inputs['fan_eta'])
                
            engine_class = self.engine_types[engine_name]
            if engine_name == "Turbofan":
                engine = engine_class(bypass_ratio=inputs['bpr'], **components)
            else:
                engine = engine_class(**components)
                
            results = engine.simulate(flight=flight_inputs, mdot_air=inputs['mdot_air'], Tt4_target=inputs['tt4_target'])

            self.update_text_results(engine_name, results)
            self.generate_graphs(engine, inputs)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical values.")
        except Exception as e:
            messagebox.showerror("Simulation Error", f"An error occurred: {e}")

    def update_text_results(self, engine_name, results):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        output = (
            f"Engine: {engine_name}\n"
            f"Net Thrust: {results.get('F_net_N', 'N/A'):.2f} N\n"
            f"TSFC: {results.get('TSFC', 'N/A'):.6f} kg/(N·s)\n"
            f"Overall Efficiency: {results.get('eta_overall', 'N/A'):.2%}\n"
            f"Air Mass Flow: {results.get('mdot_air', 'N/A'):.2f} kg/s\n"
            f"Fuel Mass Flow: {results.get('mdot_fuel', 'N/A'):.6f} kg/s\n"
        )
        self.results_text.insert(tk.END, output)
        self.results_text.config(state="disabled")

    def generate_graphs(self, engine, initial_inputs):
        for widget in self.results_graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), facecolor='#34495e')
        fig.suptitle('Engine Performance Graphs', fontsize=16, color='white')

        # Graph 1: Performance vs. Mach Number
        mach_numbers = np.linspace(0.1, 2.5, 20)
        thrusts = []
        tsfcs = []

        for M in mach_numbers:
            flight = {'altitude': initial_inputs['altitude'], 'M0': M, 'p0': standard_atmosphere(initial_inputs['altitude'])[1], 'T0': standard_atmosphere(initial_inputs['altitude'])[0]}
            try:
                result = engine.simulate(flight=flight, mdot_air=initial_inputs['mdot_air'], Tt4_target=initial_inputs['tt4_target'])
                thrusts.append(result['F_net_N'])
                tsfcs.append(result['TSFC'])
            except:
                thrusts.append(np.nan)
                tsfcs.append(np.nan)

        ax1.plot(mach_numbers, thrusts, label='Net Thrust (N)', color='#3498db')
        ax1.plot(mach_numbers, tsfcs, label='TSFC (kg/N·s)', color='#e74c3c')
        ax1.set_xlabel("Mach Number", color='white')
        ax1.set_ylabel("Performance", color='white')
        ax1.set_title("Performance vs. Mach Number", color='white')
        ax1.legend()
        ax1.tick_params(axis='x', colors='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.set_facecolor('#2c3e50')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['left'].set_color('white')

        # Graph 2: Performance vs. Altitude
        altitudes = np.linspace(0, 20000, 20)
        thrusts_alt = []
        tsfcs_alt = []

        for alt in altitudes:
            T0, p0, _ = standard_atmosphere(alt)
            flight = {'altitude': alt, 'M0': initial_inputs['mach'], 'p0': p0, 'T0': T0}
            try:
                result = engine.simulate(flight=flight, mdot_air=initial_inputs['mdot_air'], Tt4_target=initial_inputs['tt4_target'])
                thrusts_alt.append(result['F_net_N'])
                tsfcs_alt.append(result['TSFC'])
            except:
                thrusts_alt.append(np.nan)
                tsfcs_alt.append(np.nan)

        ax2.plot(altitudes, thrusts_alt, label='Net Thrust (N)', color='#3498db')
        ax2.plot(altitudes, tsfcs_alt, label='TSFC (kg/N·s)', color='#e74c3c')
        ax2.set_xlabel("Altitude (m)", color='white')
        ax2.set_ylabel("Performance", color='white')
        ax2.set_title("Performance vs. Altitude", color='white')
        ax2.legend()
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')
        ax2.set_facecolor('#2c3e50')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')

        # Embedding the plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.results_graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        
if __name__ == "__main__":
    app = EngineSimulatorGUI()
    app.mainloop()