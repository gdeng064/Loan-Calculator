import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import csv, math
import matplotlib.pyplot as plt

class LoanCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Loan Payoff Calculator")

        # Create input fields in the same row
        self.create_input_fields_in_row()

        # Create buttons (Calculate, Clear, Export, and Graph)
        self.create_buttons()

        # Apply Treeview style for column separators
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Helvetica', 10))  # Adjust row height and font
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])  # Remove borders

        # Add a treeview with columns
        self.result_tree = ttk.Treeview(master, columns=("Date", "Opening Balance", "Payment", "Interest", "Principal", "Closing Balance"), show='headings', style="Treeview")
        self.result_tree.heading("Date", text="Date")
        self.result_tree.heading("Opening Balance", text="Opening Balance")
        self.result_tree.heading("Payment", text="Payment")
        self.result_tree.heading("Interest", text="Interest")
        self.result_tree.heading("Principal", text="Principal")
        self.result_tree.heading("Closing Balance", text="Closing Balance")

        # Configure column width and alignment (center align headers and numbers)
        self.result_tree.column("Date", anchor="center", width=100)
        self.result_tree.column("Opening Balance", anchor="center", width=100)  # Right-aligned
        self.result_tree.column("Payment", anchor="center", width=100)  # Right-aligned
        self.result_tree.column("Interest", anchor="center", width=100)  # Right-aligned
        self.result_tree.column("Principal", anchor="center", width=100)  # Right-aligned
        self.result_tree.column("Closing Balance", anchor="center", width=150)  # Right-aligned

        # Apply alternating row colors
        self.result_tree.tag_configure('evenrow', background='#F5F5F5')  # Light gray
        self.result_tree.tag_configure('oddrow', background='#FFFFFF')   # White
        self.result_tree.tag_configure('totals', background='#44e35c', font=('Helvetica', 12, 'bold'))

        self.result_tree.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Add scrollbars
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.result_tree.yview)
        self.scrollbar.grid(row=7, column=2, sticky='ns')
        self.result_tree.configure(yscrollcommand=self.scrollbar.set)

        # Configure grid weights for resizing
        master.grid_rowconfigure(7, weight=1)
        master.grid_columnconfigure(1, weight=1)

        # Pre-fill current month and year
        now = datetime.now()
        self.entries[3].insert(0, str(now.month))  # Pre-fill start month
        self.entries[4].insert(0, str(now.year))   # Pre-fill start year

    def create_input_fields_in_row(self):
        labels = [
            ("Loan Balance ($):", "4504.07"), 
            ("Annual Interest Rate (%):", "6.99"), 
            ("Monthly Payment ($):", "392.29"), 
            ("Start Month (1-12):", ""),  # Default is current month
            ("Start Year:", "")  # Default is current year
        ]
        self.entries = []
        
        # Input fields all in one row
        row_frame = tk.Frame(self.master)
        row_frame.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky='w')

        # Create each label and entry field on the same row
        for i, (label_text, default_value) in enumerate(labels):
            label = tk.Label(row_frame, text=label_text)
            label.grid(row=0, column=2*i, padx=5, pady=5, sticky='w')
            
            entry = tk.Entry(row_frame, width=12)
            entry.grid(row=0, column=2*i+1, padx=5, pady=5, sticky='w')
            if default_value:  # Only set default values if provided
                entry.insert(0, default_value)
            self.entries.append(entry)

    def create_buttons(self):
        # Create a frame to hold the buttons and time label for better alignment
        button_frame = tk.Frame(self.master)
        button_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Create the calculate button inside the frame
        self.calculate_button = tk.Button(button_frame, text="Calculate Payoff Schedule", command=self.calculate_schedule, bg="#008000", fg="white", font=('Helvetica', 12, 'bold'), padx=10, pady=5)
        self.calculate_button.pack(side=tk.LEFT)

        # Label for displaying months and years, aligned next to the button inside the same frame
        self.time_label = tk.Label(button_frame, text="", bg="white", fg="black", font=('Helvetica', 12, 'bold'), padx=10, pady=5)
        self.time_label.pack(side=tk.LEFT, padx=10)

        # Add clear button
        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_inputs, bg="red", fg="white")
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Add export button
        self.export_button = tk.Button(button_frame, text="Export CSV", command=self.export_schedule_to_csv, bg="green", fg="white")
        self.export_button.pack(side=tk.LEFT, padx=10)

        # Add show graph button
        self.graph_button = tk.Button(button_frame, text="Show Graph", command=self.show_payoff_graph, bg="green", fg="white")
        self.graph_button.pack(side=tk.LEFT, padx=10)

    def calculate_schedule(self):
        # Input validation
        try:
            loan_balance = float(self.entries[0].get())
            annual_interest_rate = float(self.entries[1].get())
            monthly_payment = float(self.entries[2].get())
            start_month = int(self.entries[3].get())
            start_year = int(self.entries[4].get())

            if loan_balance <= 0 or annual_interest_rate < 0 or monthly_payment <= 0:
                raise ValueError
            if not (1 <= start_month <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers for loan balance, interest rate, and payment. Ensure month is between 1 and 12.")
            return

        # Calculate the loan payoff schedule
        schedule, months = self.loan_payoff_schedule(loan_balance, annual_interest_rate, monthly_payment, start_month, start_year)

        # Clear existing table
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # Add rows to the table with alternating colors
        for idx, row in enumerate(schedule[:-1]):  # Add rows except the totals row
            tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            self.result_tree.insert("", "end", values=row, tags=tags)

        # Insert the totals row with bold text and background color
        totals_row = schedule[-1]
        self.result_tree.insert("", "end", values=totals_row, tags=('totals',))

        # Update the time label with the total number of months and years
        years = months // 12
        remaining_months = months % 12
        self.time_label.config(text=f"Payoff Time: [ {math.ceil(years*365/7)} weeks | {months} months  |  {round(months/12, 2)} years]")

    def loan_payoff_schedule(self, loan_balance, annual_interest_rate, monthly_payment, start_month, start_year):
        monthly_interest_rate = round((annual_interest_rate / 100 / 365) * 30, 8) if annual_interest_rate > 0 else 0
        month = 0
        schedule_list = []
        
        total_interest = 0
        total_principal = 0
        total_payment = 0
        max_year = 9999  # Maximum allowed year in datetime

        while loan_balance > 0:
            current_month = (start_month + month - 1) % 12 + 1
            current_year = start_year + (start_month + month - 1) // 12

            if current_year > max_year:
                messagebox.showerror("Date Error", f"The calculated year {current_year} exceeds the maximum supported year ({max_year}). Calculation stopped.")
                break

            date = datetime(current_year, current_month, 1).strftime("%b %Y")

            if monthly_interest_rate > 0:
                interest = loan_balance * monthly_interest_rate
                principal = min(monthly_payment - interest, loan_balance)
            else:
                interest = 0
                principal = min(monthly_payment, loan_balance)

            payment = interest + principal

            total_interest += interest
            total_principal += principal
            total_payment += payment

            row = [
                date,
                f"${loan_balance:,.2f}",
                f"${payment:,.2f}",
                f"${interest:,.2f}",
                f"${principal:,.2f}",
                f"${max(loan_balance - principal, 0):,.2f}"
            ]
            schedule_list.append(row)

            loan_balance -= principal
            month += 1

        totals_row = [
            "Totals",
            "$0.00",  # No opening balance after the loan is paid off
            f"${total_principal:,.2f}",
            f"${total_interest:,.2f}",
            f"${total_payment:,.2f}",
            "$0.00"  # Closing balance should be 0
        ]
        schedule_list.append(totals_row)

        return schedule_list, month


    def clear_inputs(self):
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.time_label.config(text="")
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

    def export_schedule_to_csv(self, filename="loan_schedule.csv"):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Opening Balance", "Payment", "Interest", "Principal", "Closing Balance"])
            for row_id in self.result_tree.get_children():
                writer.writerow(self.result_tree.item(row_id)['values'])
        messagebox.showinfo("Export Successful", f"Schedule exported to {filename}")

    def show_payoff_graph(self):
        schedule = self.get_schedule()
        if not schedule:
            messagebox.showwarning("Graph Error", "No schedule available to display. Please calculate the schedule first.")
            return

        dates = [row[0] for row in schedule[:-1]]  # Exclude totals row
        balances = [float(row[5].replace('$', '').replace(',', '')) for row in schedule[:-1]]  # Closing balances
        payments = [float(row[2].replace('$', '').replace(',', '')) for row in schedule[:-1]]  # Monthly Payments
        interests = [float(row[3].replace('$', '').replace(',', '')) for row in schedule[:-1]]  # Interest
        principals = [float(row[4].replace('$', '').replace(',', '')) for row in schedule[:-1]]  # Principal

        plt.figure(figsize=(10, 6))  # Set the figure size

        # Plotting each line
        plt.plot(dates, balances, label='Closing Balance', color='blue', marker='o')  # Closing Balance
        plt.plot(dates, payments, label='Monthly Payment', color='green', linestyle='--', marker='o')  # Monthly Payments
        plt.plot(dates, interests, label='Interest', color='orange', linestyle='--', marker='o')  # Interest
        plt.plot(dates, principals, label='Principal', color='red', linestyle='--', marker='o')  # Principal

        plt.xlabel("Date")
        plt.ylabel("Amount ($)")
        plt.title("Loan Payment Breakdown Over Time")
        plt.xticks(rotation=85)
        
        # Add a grid
        plt.grid(False)  
        plt.legend()  # Add a legend to differentiate between the lines
        plt.tight_layout()
        plt.show()


    def get_schedule(self):
        return [self.result_tree.item(row)['values'] for row in self.result_tree.get_children()]

if __name__ == "__main__":
    root = tk.Tk()
    calculator = LoanCalculator(root)
    root.mainloop()
    # 14601.82 BMO LoC
