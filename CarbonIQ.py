import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# --- Functions ---
def calculate():
    try:
        hours = float(hours_entry.get())
        dataset_factor = float(dataset_var.get())
    except:
        messagebox.showerror("Error", "Enter valid numeric values")
        return
    
    hardware = hardware_var.get()
    region_factor = float(region_var.get())

    power_dict = {"CPU":120, "GPU":300, "TPU":250}
    power = power_dict[hardware]

    selected_models = [m for m, var in model_vars.items() if var.get()==1]
    if not selected_models:
        messagebox.showwarning("Warning", "Select at least one model")
        return

    results.clear()
    result_text.delete("1.0", tk.END)
    
    # Animated chart
    max_steps = 20
    temp_energies = {m:0 for m in selected_models}
    temp_co2s = {m:0 for m in selected_models}

    for step in range(1,max_steps+1):
        fig.clf()
        ax = fig.add_subplot(111)
        for model in selected_models:
            factor = model_factors.get(model,1)
            energy = (power * hours * dataset_factor * factor)/1000
            co2 = energy * region_factor
            results[model] = {"energy":energy, "co2":co2}

            temp_energies[model] = energy * step/max_steps
            temp_co2s[model] = co2 * step/max_steps

        model_names = list(selected_models)
        energies = [temp_energies[m] for m in model_names]
        co2s = [temp_co2s[m] for m in model_names]
        x = range(len(model_names))
        ax.bar([i-0.15 for i in x], energies, width=0.3, label="Energy (kWh)", color="#29b6f6")
        ax.bar([i+0.15 for i in x], co2s, width=0.3, label="CO₂ (kg)", color="#ff7043")
        ax.set_xticks(x)
        ax.set_xticklabels(model_names)
        ax.set_ylabel("Value")
        ax.set_title("ML Models Energy & CO₂")
        ax.legend()
        canvas.draw()
        root.update()
        time.sleep(0.03)

    # Display results
    result_text.delete("1.0", tk.END)
    for model in selected_models:
        result_text.insert(tk.END,f"{model} → ⚡ Energy: {results[model]['energy']:.2f} kWh, 🌫️ CO₂: {results[model]['co2']:.2f} kg\n")

def export_pdf():
    if not results:
        messagebox.showwarning("Warning", "Calculate first!")
        return
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"AI Carbon Impact Report", ln=1, align="C")
    pdf.set_font("Arial","",12)
    pdf.ln(10)
    pdf.cell(0,10,f"Hardware: {hardware_var.get()}", ln=1)
    pdf.cell(0,10,f"Training Hours: {hours_entry.get()}", ln=1)
    pdf.cell(0,10,f"Region Factor: {region_var.get()}", ln=1)
    pdf.cell(0,10,f"Dataset Factor: {dataset_var.get()}", ln=1)
    pdf.ln(5)
    for model in results:
        pdf.cell(0,10,f"{model} → Energy: {results[model]['energy']:.2f} kWh, CO₂: {results[model]['co2']:.2f} kg", ln=1)
    chart_path = "side_chart.png"
    fig.savefig(chart_path)
    pdf.image(chart_path, x=30, w=150)
    pdf.output("AI_Carbon_Impact_Report.pdf")
    messagebox.showinfo("PDF Saved", "Report saved as AI_Carbon_Impact_Report.pdf")

# --- GUI Setup ---
root = tk.Tk()
root.title("AI Carbon Impact Calculator")
root.geometry("900x600")
root.configure(bg="#f0f4f8")

results = {}
model_factors = {"Small":1, "Medium":1.5, "Large":2, "Custom":1.2}

# Main frames: left=inputs/results, right=chart
left_frame = tk.Frame(root, bg="#e8f0fe", padx=10, pady=10)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(root, bg="#f0f4f8", padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

# --- Left Frame: Inputs ---
tk.Label(left_frame, text="🌍 AI Carbon Impact Calculator", font=("Arial",16,"bold"), bg="#e8f0fe").pack(pady=5)

# Hardware
tk.Label(left_frame,text="Hardware:", bg="#e8f0fe").pack(anchor="w")
hardware_var = tk.StringVar(value="GPU")
ttk.Combobox(left_frame,textvariable=hardware_var, values=["CPU","GPU","TPU"], state="readonly").pack(fill="x", pady=2)

# Training Hours
tk.Label(left_frame,text="Training Hours:", bg="#e8f0fe").pack(anchor="w")
hours_entry = tk.Entry(left_frame)
hours_entry.pack(fill="x", pady=2)

# Region Factor
tk.Label(left_frame,text="Region CO₂ Factor:", bg="#e8f0fe").pack(anchor="w")
region_var = tk.StringVar(value="0.7")
ttk.Combobox(left_frame,textvariable=region_var, values=["0.7","0.4","0.2"], state="readonly").pack(fill="x", pady=2)

# Dataset Factor
tk.Label(left_frame,text="Dataset Factor:", bg="#e8f0fe").pack(anchor="w")
dataset_var = tk.StringVar(value="1")
ttk.Combobox(left_frame,textvariable=dataset_var, values=["0.5","1","1.5","2"], state="readonly").pack(fill="x", pady=2)

# Models selection
tk.Label(left_frame,text="Select ML Models:", bg="#e8f0fe").pack(anchor="w")
model_vars = {}
for model in ["Small","Medium","Large","Custom"]:
    var = tk.IntVar()
    tk.Checkbutton(left_frame, text=model, variable=var, bg="#e8f0fe").pack(anchor="w")
    model_vars[model] = var

# Buttons
tk.Button(left_frame,text="Calculate Impact", command=calculate, bg="#4caf50", fg="white").pack(pady=5,fill="x")
tk.Button(left_frame,text="Export PDF Report", command=export_pdf, bg="#1b5e20", fg="white").pack(pady=5,fill="x")

# Result display
result_text = tk.Text(left_frame,height=12)
result_text.pack(fill="x", pady=5)

# --- Right Frame: Chart ---
fig = plt.Figure(figsize=(5,5))
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

root.mainloop()
