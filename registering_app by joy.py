import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Function to create Excel sheet
def create_excel():
    crop_name = crop_entry.get()
    try:
        field_area = float(field_area_entry.get())
        motor_capacity = float(motor_capacity_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for field area and motor capacity")
        return

    # Create data dictionary
    data = {
        "Crop Name": [crop_name],
        "Field Area (acres)": [field_area],
        "Motor Pump Capacity (L/min)": [motor_capacity]
    }

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Set the file name to "my_field.xlsx"
    file_name = "my_field.xlsx"

    # Save to Excel file
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Field Data', startrow=1, index=False)
        workbook = writer.book
        worksheet = writer.sheets['Field Data']

        # Format the heading
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'valign': 'center',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        worksheet.merge_range('A1:D1', f"Field Data", header_format)

    # Success message
    messagebox.showinfo("Success", f"Excel sheet created: {file_name}")

# GUI Setup
root = tk.Tk()
root.title("Field Data Application")
root.geometry("600x600")
root.configure(bg="#E0E0E0")  # Light gray background

# Frame for main content
main_frame = tk.Frame(root, bg="#E0E0E0", bd=5, relief=tk.GROOVE)
main_frame.pack(pady=20, padx=10)

# Adjusted font sizes
heading_font = ("Helvetica", 36)  # Heading font
label_font = ("Helvetica", 18)     # Label font
button_font = ("Helvetica", 18)    # Button font

# Heading
heading = tk.Label(main_frame, text="Field Data Entry", font=heading_font, fg="#4B0082", bg="#E0E0E0")
heading.pack(pady=10)

# Function to create a 3D button effect
def create_3d_button(text, command):
    button_frame = tk.Frame(main_frame, bg="#E0E0E0")  # Background frame for the button
    button_frame.pack(pady=10)  # Padding for the button frame

    button = tk.Button(
        button_frame,
        text=text,
        command=command,
        font=button_font,
        bg="#4CAF50", 
        fg="white",
        relief=tk.RAISED,
        bd=5,
        activebackground="#45A049",
        activeforeground="white"
    )
    button.pack(padx=5, pady=5)  # Padding for the button
    return button

# Crop Name
crop_label = tk.Label(main_frame, text="Crop Name:", font=label_font, bg="#E0E0E0")
crop_label.pack(pady=5)
crop_entry = tk.Entry(main_frame, width=30, font=label_font)
crop_entry.pack(pady=5)

# Field Area
field_area_label = tk.Label(main_frame, text="Field Area (acres):", font=label_font, bg="#E0E0E0")
field_area_label.pack(pady=5)
field_area_entry = tk.Entry(main_frame, width=30, font=label_font)
field_area_entry.pack(pady=5)

# Motor Capacity
motor_capacity_label = tk.Label(main_frame, text="Motor Pump Capacity (L/min):", font=label_font, bg="#E0E0E0")
motor_capacity_label.pack(pady=5)
motor_capacity_entry = tk.Entry(main_frame, width=30, font=label_font)
motor_capacity_entry.pack(pady=5)

# Submit Button
submit_button = create_3d_button("Create Excel", create_excel)

# Run the GUI loop
root.mainloop()
