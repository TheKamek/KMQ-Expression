import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
from datetime import datetime
import hashlib
import random
import csv

current_profile_path = None


def generate_sigil(data):
    
    profile_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    
    random.seed(profile_hash)
    
    
    char_list = r"/&%\"*+ç=)(\<>!@"
    
    
    sigil = ""
    for _ in range(5):
        for _ in range(10):
            sigil += random.choice(char_list)
        sigil += "\n"
    
    return sigil.strip()

def delete_profile():
    global current_profile_path
    if current_profile_path:
        result = messagebox.askyesno("Delete Profile", "Are you sure you want to delete this profile?")
        if result:
            try:
                os.remove(current_profile_path)
                messagebox.showinfo("Success", "Profile deleted successfully")
                current_profile_path = None
                create_new_profile()  
                update_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete the profile. Error: {str(e)}")
    else:
        messagebox.showwarning("No Profile Selected", "Please load a profile before deleting.")

def export_to_csv():
    try:
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                 filetypes=[("CSV files", "*.csv")])
        if not file_path:  
            return

        
        profile_files = [f for f in os.listdir(current_dir) if f.endswith("_profile.json")]

        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            
            header = ["First Name", "Last Name", "Gender", "Profession", "Personality Type", 
                      "Additional Notes", "Timestamp", "Sigil"]
            header.extend(traits)  
            csvwriter.writerow(header)

            
            for profile_file in profile_files:
                with open(os.path.join(current_dir, profile_file), 'r') as f:
                    data = json.load(f)
                
                row = [
                    data.get('first_name', ''),
                    data.get('last_name', ''),
                    data.get('gender', ''),
                    data.get('profession', ''),
                    data.get('personality_type', ''),
                    data.get('additional_notes', ''),
                    data.get('timestamp', ''),
                    data.get('sigil', '').replace('\n', '|')  
                ]
                
                
                for trait in traits:
                    row.append(data.get('traits', {}).get(trait, ''))
                
                csvwriter.writerow(row)

        messagebox.showinfo("Success", f"Profiles exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not export profiles. Error: {str(e)}")

def generate_profile():
    data = {
        "first_name": first_name_entry.get(),
        "last_name": last_name_entry.get(),
        "gender": gender_var.get(),
        "profession": profession_entry.get(),
        "traits": {trait: scales[trait].get() for trait in traits},
        "additional_notes": notes_text.get("1.0", tk.END).strip(),
        "timestamp": datetime.now().isoformat()
    }
    
    sorted_traits = sorted(data["traits"].items(), key=lambda x: x[1], reverse=True)
    data["personality_type"] = sorted_traits[0][0][0] + sorted_traits[1][0][0]
    
    
    data["sigil"] = generate_sigil(data)
    
    save_profile(data)
    display_sigil(data["sigil"])

def save_profile(data):
    global current_profile_path
    if current_profile_path:
        full_path = current_profile_path
    else:
        filename = f"{data['first_name']}_{data['last_name']}_profile.json"
        counter = 1
        while os.path.exists(os.path.join(current_dir, filename)):
            filename = f"{data['first_name']}_{data['last_name']}_profile_{counter}.json"
            counter += 1
        full_path = os.path.join(current_dir, filename)
    
    try:
        with open(full_path, "w") as f:
            json.dump(data, f, indent=2)
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            result_label.config(text=f"Profile saved as {os.path.basename(full_path)}\nFile size: {file_size} bytes\nLocation: {current_dir}")
            result_label.configure(style="Success.TLabel")
            update_file_list()
        else:
            result_label.config(text=f"File created but not found: {full_path}")
            result_label.configure(style="Error.TLabel")
    except Exception as e:
        result_label.config(text=f"Error saving file: {str(e)}\nAttempted path: {full_path}")
        result_label.configure(style="Error.TLabel")

def update_profile():
    global current_profile_path
    if current_profile_path:
        generate_profile()
    else:
        messagebox.showwarning("No Profile Selected", "Please load a profile before updating.")

def update_file_list():
    file_listbox.delete(0, tk.END)
    for file in os.listdir(current_dir):
        if file.endswith("_profile.json"):
            file_listbox.insert(tk.END, file)
            
def load_profile(event):
    global current_profile_path
    try:
        selection = file_listbox.curselection()
        if selection:
            selected_file = file_listbox.get(selection)
            current_profile_path = os.path.join(current_dir, selected_file)
            with open(current_profile_path, 'r') as f:
                data = json.load(f)

            first_name_entry.delete(0, tk.END)
            first_name_entry.insert(0, data.get('first_name', ''))

            last_name_entry.delete(0, tk.END)
            last_name_entry.insert(0, data.get('last_name', ''))

            profession_entry.delete(0, tk.END)
            profession_entry.insert(0, data.get('profession', ''))

            gender_var.set(data.get('gender', 'undefined'))

            for trait, scale in scales.items():
                scale.set(data['traits'].get(trait, 50))

            notes_text.delete('1.0', tk.END)
            notes_text.insert('1.0', data.get('additional_notes', ''))

            display_sigil(data.get('sigil', ''))

            result_label.config(text="Profile loaded successfully")
            result_label.configure(style="Success.TLabel")
    
    except Exception as e:
        messagebox.showerror("Error", f"Could not load the profile. Error: {e}")
        result_label.config(text=f"Error loading profile: {str(e)}")
        result_label.configure(style="Error.TLabel")

def create_new_profile():
    global current_profile_path
    current_profile_path = None
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    profession_entry.delete(0, tk.END)
    gender_var.set('undefined')
    for scale in scales.values():
        scale.set(50)
    notes_text.delete('1.0', tk.END)
    result_label.config(text="")
    display_sigil('')

def display_sigil(sigil):
    sigil_text.config(state=tk.NORMAL)
    sigil_text.delete('1.0', tk.END)
    sigil_text.insert(tk.END, sigil)
    sigil_text.config(state=tk.DISABLED)

def copy_sigil():
    sigil = sigil_text.get('1.0', tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(sigil)
    messagebox.showinfo("Copied", "Sigil copied to clipboard!")

root = tk.Tk()
root.title("Personality Profile Generator")

root.attributes('-fullscreen', True)

style = ttk.Style()
style.configure("Success.TLabel", foreground="green")
style.configure("Error.TLabel", foreground="red")

current_dir = os.getcwd()

left_frame = ttk.Frame(root, padding="10")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = ttk.Frame(root, padding="10")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

close_button = ttk.Button(root, text="X", command=root.quit)
close_button.place(relx=1.0, y=0, anchor="ne")


ttk.Label(left_frame, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
first_name_entry = ttk.Entry(left_frame)
first_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
last_name_entry = ttk.Entry(left_frame)
last_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Profession:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
profession_entry = ttk.Entry(left_frame)
profession_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Gender:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
gender_var = tk.StringVar(value="undefined")
gender_frame = ttk.Frame(left_frame)
gender_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

genders = ["male", "female", "non-binary", "undefined"]
for i, gender in enumerate(genders):
    ttk.Radiobutton(gender_frame, text=gender, variable=gender_var, value=gender).grid(row=0, column=i, padx=5)

traits = [
    "Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism",
    "Self-Discipline", "Assertiveness", "Empathy", "Creativity", "Curiosity",
    "Resilience", "Adaptability", "Emotional Intelligence", "Leadership",
    "Risk-Taking", "Perfectionism", "Optimism", "Patience", "Honesty", "Ambition"
]
scales = {}

for i, trait in enumerate(traits):
    row = i // 2 + 4
    col = (i % 2) * 3
    ttk.Label(left_frame, text=f"{trait}:").grid(row=row, column=col, padx=10, pady=5, sticky="e")
    scale = ttk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
    scale.set(50)
    scale.grid(row=row, column=col+1, padx=10, pady=5, sticky="w")
    scales[trait] = scale

ttk.Label(left_frame, text="Additional Notes:").grid(row=len(traits)//2+5, column=0, padx=10, pady=5, sticky="ne")
notes_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=40, height=5)
notes_text.grid(row=len(traits)//2+5, column=1, columnspan=5, padx=10, pady=5, sticky="w")
ttk.Label(left_frame, text="Personality Sigil:").grid(row=len(traits)//2+8, column=0, padx=10, pady=5, sticky="ne")
sigil_text = tk.Text(left_frame, wrap=tk.NONE, width=25, height=5, font=("Courier", 12))
sigil_text.grid(row=len(traits)//2+8, column=1, columnspan=5, padx=10, pady=5, sticky="w")
sigil_text.config(state=tk.DISABLED)

button_frame = ttk.Frame(left_frame)
button_frame.grid(row=len(traits)//2+6, column=0, columnspan=6, pady=10)

submit_button = ttk.Button(button_frame, text="Save New Profile", command=generate_profile)
submit_button.grid(row=0, column=0, padx=5)

update_button = ttk.Button(button_frame, text="Update Profile", command=update_profile)
update_button.grid(row=0, column=1, padx=5)

new_profile_button = ttk.Button(button_frame, text="New Profile", command=create_new_profile)
new_profile_button.grid(row=0, column=2, padx=5)

delete_button = ttk.Button(button_frame, text="Delete Profile", command=delete_profile)
delete_button.grid(row=0, column=3, padx=5)

export_button = ttk.Button(button_frame, text="Export to CSV", command=export_to_csv)
export_button.grid(row=0, column=4, padx=5)


result_label = ttk.Label(left_frame, text="")
result_label.grid(row=len(traits)//2+7, column=0, columnspan=6, pady=5)


ttk.Label(right_frame, text="Saved Profiles:").pack(pady=10)

file_listbox = tk.Listbox(right_frame, width=50)
file_listbox.pack(expand=True, fill='both')
file_listbox.bind('<Double-1>', load_profile)

update_file_list()


left_frame.grid_columnconfigure(1, weight=1)
left_frame.grid_columnconfigure(4, weight=1)


root.mainloop()