import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket
import ssl
import time

HOST = '192.168.92.200'
PORT = 9999
CERT_FILE = 'server.crt'

class ClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Seat-Smart")
        master.resizable(False, False)  # Prevent window resizing

        # Setting up colors
        self.primary_color = '#4b0082'  # Indigo
        self.secondary_color = '#ff7f0e'  # Orange
        self.accent_color = '#66c2a5'  # Light green

        # Setting up fonts
        self.header_font = ('Helvetica', 24, 'bold')
        self.label_font = ('Helvetica', 14)
        self.button_font = ('Helvetica', 14, 'bold')

        # Change default background color
        master.configure(background=self.primary_color)

        # Creating widgets
        self.create_widgets()

        # Initialize client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = ssl.wrap_socket(self.client, cert_reqs=ssl.CERT_REQUIRED, ca_certs=CERT_FILE)
        self.client.connect((HOST, PORT))

        # Automatically refresh available classes
        self.view_classes()

        # Update time
        self.update_time()

        # Initialize active classes list
        self.active_classes = {}

    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self.master, background=self.primary_color)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        # Time Label
        self.time_label = tk.Label(header_frame, text='', font=self.header_font, background=self.primary_color, fg='white')
        self.time_label.pack(side=tk.LEFT, padx=(0, 20))

        # Header Label
        self.label = tk.Label(header_frame, text="Seat-Smart", font=self.header_font, background=self.primary_color, fg='white')
        self.label.pack(side=tk.LEFT)

        # Refresh Button
        self.view_button = tk.Button(header_frame, text="Refresh", font=self.button_font, command=self.view_classes, bg=self.accent_color, fg='white')
        self.view_button.pack(side=tk.RIGHT, padx=(20, 0))

        # Treeview Frame
        tree_frame = tk.Frame(self.master, background=self.primary_color)
        tree_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Treeview for displaying class information
        self.treeview = ttk.Treeview(tree_frame, height=10)
        self.treeview.pack(fill=tk.X)

        # Columns for the treeview
        columns = ("Class", "Teacher", "Timing", "Available Seats")
        self.treeview["columns"] = columns
        self.treeview["show"] = "headings"
        for col in columns:
            self.treeview.heading(col, text=col)

        # Frame for class selection and seats selection
        selection_frame = tk.Frame(self.master, background=self.primary_color)
        selection_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        # Label and Dropdown for selecting class
        select_class_label = tk.Label(selection_frame, text="Select Class:", font=self.label_font, background=self.primary_color, fg='white')
        select_class_label.pack(side=tk.LEFT, padx=(0, 10))
        self.class_var = tk.StringVar(self.master)
        self.class_var.set("Select Class")
        self.class_dropdown = tk.OptionMenu(selection_frame, self.class_var, "Select Class")  # Default value set
        self.class_dropdown.pack(side=tk.LEFT)

        # Label and Dropdown for selecting number of seats
        seats_label = tk.Label(selection_frame, text="No. of Seats:", font=self.label_font, background=self.primary_color, fg='white')
        seats_label.pack(side=tk.LEFT, padx=(10, 0))
        self.seats_var = tk.StringVar(self.master)
        self.seats_var.set("Select Seats")
        self.seats_dropdown = tk.OptionMenu(selection_frame, self.seats_var, "Select Seats")  # Default value set
        self.seats_dropdown.pack(side=tk.LEFT)

        # Button frame
        button_frame = tk.Frame(self.master, background=self.primary_color)
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))

        # Book Class Button
        self.book_button = tk.Button(button_frame, text="Book Class", font=self.button_font, command=self.book_class, bg=self.secondary_color, fg='white')
        self.book_button.pack(side=tk.LEFT, padx=10)

        # Cancel Booking Button
        self.cancel_button = tk.Button(button_frame, text="Cancel Booking", font=self.button_font, command=self.cancel_booking, bg='red', fg='white')
        self.cancel_button.pack(side=tk.LEFT, padx=10)

        # Active Classes Frame
        active_classes_frame = tk.Frame(self.master, background=self.primary_color)
        active_classes_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Active Classes Label
        active_classes_label = tk.Label(active_classes_frame, text="Active Classes:", font=self.label_font, background=self.primary_color, fg='white')
        active_classes_label.pack(side=tk.LEFT)

        # Active Classes Listbox
        self.active_classes_listbox = tk.Listbox(active_classes_frame, width=60, height=5, font=self.label_font)
        self.active_classes_listbox.pack(fill=tk.X)

    def view_classes(self):
        self.treeview.delete(*self.treeview.get_children())
        try:
            self.client.send('get_classes'.encode('utf-8'))
            classes_info = eval(self.client.recv(1024).decode('utf-8'))
            for class_name, details in classes_info.items():
                available_seats = details['seats']
                if available_seats > 0:
                    self.treeview.insert("", "end", values=(class_name, details['teacher'], details['timing'], available_seats), tags='available')
                    self.treeview.item(self.treeview.selection(), tags='available')

            # Populate dropdowns with available classes and number of seats
            class_names = list(classes_info.keys())
            self.class_var.set("Select Class")
            self.class_dropdown['menu'].delete(0, 'end')
            for class_name in class_names:
                self.class_dropdown['menu'].add_command(label=class_name, command=tk._setit(self.class_var, class_name))
            
            max_seats = 3
            seats_list = [str(i) for i in range(1, max_seats + 1)]
            self.seats_var.set("Select Seats")
            self.seats_dropdown['menu'].delete(0, 'end')
            for seats in seats_list:
                self.seats_dropdown['menu'].add_command(label=seats, command=tk._setit(self.seats_var, seats))

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def book_class(self):
        class_name = self.class_var.get()
        num_seats = self.seats_var.get()
        if class_name == "Select Class" or num_seats == "Select Seats":
            messagebox.showwarning("Warning", "Please select class and number of seats.")
            return
        try:
            self.client.send(f'book_class {class_name} {num_seats}'.encode('utf-8'))
            response = self.client.recv(1024).decode('utf-8')
            messagebox.showinfo("Booking Status", response)

            # Update active classes list
            if class_name in self.active_classes:
                self.active_classes[class_name] += int(num_seats)
            else:
                self.active_classes[class_name] = int(num_seats)

            self.update_active_classes_list()

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def cancel_booking(self):
        class_name = self.class_var.get()
        num_seats = self.seats_var.get()
        if class_name == "Select Class" or num_seats == "Select Seats":
            messagebox.showwarning("Warning", "Please select class and number of seats.")
            return
        try:
            self.client.send(f'cancel_booking {class_name} {num_seats}'.encode('utf-8'))
            response = self.client.recv(1024).decode('utf-8')
            messagebox.showinfo("Cancellation Status", response)

            # Update active classes list
            if class_name in self.active_classes:
                self.active_classes[class_name] -= int(num_seats)
                if self.active_classes[class_name] <= 0:
                    del self.active_classes[class_name]

            self.update_active_classes_list()

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.master.after(1000, self.update_time)

    def update_active_classes_list(self):
        self.active_classes_listbox.delete(0, tk.END)
        for i, (class_name, seats_booked) in enumerate(self.active_classes.items(), start=1):
            self.active_classes_listbox.insert(tk.END, f"{i}.   Class: {class_name}   Seats Booked: {seats_booked}")

def main():
    root = tk.Tk()
    root.geometry("800x600")  # Set window width and height
    client_gui = ClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
