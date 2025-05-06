import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry # type: ignore

class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.logged_in = False
        self.load_credentials()

    def load_credentials(self):
        try:
            with open('credentials.txt', 'r') as file:
                data = file.readlines()
                if data:
                    self.username, self.password = data[0].strip().split(',')
        except FileNotFoundError:
            pass

    def save_credentials(self):
        with open('credentials.txt', 'w') as file:
            file.write(f"{self.username},{self.password}")

    def login(self, username, password):
        if self.username is None or self.password is None:
            print("Welcome, user!")
            self.username = username
            self.password = password
            self.logged_in = True
            self.save_credentials()
            return True
        elif username == self.username and password == self.password:
            print("Login successful!")
            self.logged_in = True
            return True
        else:
            print("Invalid username or password.")
            return False

class Expense:
    def __init__(self, date, category, amount, is_repeated, payment_method):
        self.date = datetime.strptime(date.split()[0], '%Y-%m-%d')
        self.category = category
        self.amount = amount
        self.is_repeated = is_repeated
        self.payment_method = payment_method

class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.budgets = {}
        self.load_expenses()  # Load expenses only once during initialization
        self.load_budgets()

    def load_expenses(self):
        if not self.expenses:  # Check if expenses have already been loaded
            try:
                with open('expenses.csv', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        expense = Expense(row['Date'], row['Category'], float(row['Amount']), row['Repeated'] == 'True', row['Payment Method'])
                        self.expenses.append(expense)
            except FileNotFoundError:
                pass

    def save_expenses(self):
        with open('expenses.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Category', 'Amount', 'Repeated', 'Payment Method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for expense in self.expenses:
                writer.writerow({'Date': expense.date.strftime('%Y-%m-%d'), 'Category': expense.category, 'Amount': expense.amount,
                                 'Repeated': 'True' if expense.is_repeated else 'False',
                                 'Payment Method': expense.payment_method})

    def load_budgets(self):
        try:
            with open('budgets.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.budgets[row['Category']] = float(row['Budget'])
        except FileNotFoundError:
            pass

    def save_budgets(self):
        with open('budgets.csv', 'w', newline='') as csvfile:
            fieldnames = ['Category', 'Budget']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for category, budget in self.budgets.items():
                writer.writerow({'Category': category, 'Budget': budget})

    def set_budget(self, category, budget):
        self.budgets[category] = budget
        self.save_budgets()

    def get_categories(self):
        return list(self.budgets.keys())
    
    def add_expense(self, date, category, amount, is_repeated, payment_method):
        expense = Expense(date, category, amount, is_repeated, payment_method)
        self.expenses.append(expense)
        self.save_expenses()

    def get_expenses_by_month(self, month):
        return [expense for expense in self.expenses if expense.date.strftime('%Y-%m').startswith(month)]

class ExpenseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.tracker = ExpenseTracker()
        self.categories = self.tracker.get_categories()

        self.username_label = ttk.Label(root, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(root, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, padx=5, pady=5)
        
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if user.login(username, password):
            self.show_options()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_options(self):
        self.username_label.grid_remove()
        self.username_entry.grid_remove()
        self.password_label.grid_remove()
        self.password_entry.grid_remove()
        self.login_button.grid_remove()

        self.set_budget_button = ttk.Button(self.root, text="Set Budget", command=self.set_budget)
        self.set_budget_button.grid(row=0, column=0, padx=5, pady=5)

        self.view_expenses_button = ttk.Button(self.root, text="View Expenses", command=self.view_expenses)
        self.view_expenses_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.view_monthly_expenses_button = ttk.Button(self.root, text="View Monthly Expenses", command=self.view_monthly_expenses)
        self.view_monthly_expenses_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Combobox for categories
        self.category_label = ttk.Label(self.root, text="Category:")
        self.category_label.grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.categories_combobox = ttk.Combobox(self.root, textvariable=self.category_var, state="readonly")
        self.categories_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.categories_combobox['values'] = self.categories
    
        self.view_budget_button = ttk.Button(self.root, text="View Budgets", command=self.view_budgets)
        self.view_budget_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Entry fields for expense details
        self.amount_label = ttk.Label(self.root, text="Amount:")
        self.amount_label.grid(row=3, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)
        
        self.date_label = ttk.Label(self.root, text="Date:")
        self.date_label.grid(row=4, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(self.root)
        self.date_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Checkbutton for is_repeated
        self.is_repeated_var = tk.BooleanVar()
        self.is_repeated_checkbutton = ttk.Checkbutton(self.root, text="Repeated", variable=self.is_repeated_var)
        self.is_repeated_checkbutton.grid(row=5, column=1, padx=5, pady=5, sticky="W")

        # Combobox for payment_method
        self.payment_method_label = ttk.Label(self.root, text="Payment Method:")
        self.payment_method_label.grid(row=6, column=0, padx=5, pady=5)
        self.payment_method_var = tk.StringVar()
        self.payment_method_combobox = ttk.Combobox(self.root, textvariable=self.payment_method_var, state="readonly")
        self.payment_method_combobox.grid(row=6, column=1, padx=5, pady=5)
        self.payment_method_combobox['values'] = ['Cash', 'Credit Card', 'Debit Card', 'Online Payment']
        
        # Button to add expense
        self.add_expense_button = ttk.Button(self.root, text="Add Expense", command=self.add_expense)
        self.add_expense_button.grid(row=7, column=1, padx=5, pady=5)

    def set_budget(self):
        self.budget_window = tk.Toplevel(self.root)
        self.budget_window.title("Set Budget")

        self.budget_entries = {}  # Dictionary to store budget entry widgets for each category

        for i, category in enumerate(["Groceries", "Medical", "Entertainment", "Other"]):  # You can modify this list to include more categories
            ttk.Label(self.budget_window, text=category).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.budget_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.budget_entries[category] = entry

        ttk.Button(self.budget_window, text="Submit", command=self.submit_budget).grid(row=len(self.budget_entries), column=1, padx=5, pady=5)

    def submit_budget(self):
        budgets = {}
        for category, entry in self.budget_entries.items():
            budget = entry.get()
            if budget:  # Check if a value is entered
                budgets[category] = float(budget)
        print("Budgets:", budgets)
        # Here you can save the budgets to a file or perform other actions

    def view_budgets(self):
        budgets_window = tk.Toplevel(self.root)
        budgets_window.title("View Budgets")

        # Display budgets for each category
        for i, (category, budget) in enumerate(self.tracker.budgets.items()):
            ttk.Label(budgets_window, text=f"{category}:").grid(row=i, column=0, padx=5, pady=5)
            ttk.Label(budgets_window, text=f"${budget}").grid(row=i, column=1, padx=5, pady=5)

    def view_expenses(self):
        # Create a new window for displaying expenses
        expenses_window = tk.Toplevel(self.root)
        expenses_window.title("View Expenses")
        expenses_window.geometry("800x600")  # Set the dimensions to 800x600 pixels

        # Retrieve the list of expenses from the ExpenseTracker
        expenses = self.tracker.expenses

        # Create a text widget to display the expenses
        text_widget = tk.Text(expenses_window, height=40, width=100)
        text_widget.pack(padx=10, pady=10)

        # Format and display the expenses in the text widget
        text_widget.insert(tk.END, "{:<15}{:<15}{:<15}{:<15}{:<15}\n".format("Date", "Category", "Amount", "Repeated", "Payment Method"))
        for expense in expenses:
            text_widget.insert(tk.END, "{:<15}{:<15}{:<15.2f}{:<15}{:<15}\n".format(expense.date.strftime('%Y-%m-%d'), expense.category, expense.amount, expense.is_repeated, expense.payment_method))

        # Make the text widget read-only
        text_widget.config(state=tk.DISABLED)

    def view_monthly_expenses(self):
        # Calculate monthly expenses
        monthly_expenses = {}
        for expense in self.tracker.expenses:
            # Extract the year and month from the expense's date
            expense_month = expense.date.strftime('%Y-%m')
            if expense_month in monthly_expenses:
                monthly_expenses[expense_month] += expense.amount
            else:
                monthly_expenses[expense_month] = expense.amount

        print("Monthly Expenses:", monthly_expenses)

        # Plot monthly expenses
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(monthly_expenses.keys(), monthly_expenses.values(), color='blue')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Expenses')
        ax.set_title('Monthly Expenses')
        plt.xticks(rotation=45, ha='right')

        # Create a new window to display the plot
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Monthly Expenses")

        # Create a Tkinter canvas widget for the plot
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Display the plot
        plt.tight_layout()

    def add_expense(self):
        # Check if a category is selected
        selected_category = self.categories_combobox.get()
        if not selected_category:
            messagebox.showerror("Error", "Please select a category first.")
            return

        # Get expense details
        amount = float(self.amount_entry.get())
        date = self.date_entry.get_date().strftime('%Y-%m-%d')
        is_repeated = self.is_repeated_var.get()
        payment_method = self.payment_method_combobox.get()

        # Check if the expense exceeds the budget
        if selected_category in self.tracker.budgets:
            budget = self.tracker.budgets[selected_category]
            if amount > budget:
                messagebox.showwarning("Warning", f"The amount exceeds the budget for {selected_category}.")

        # Create an Expense object
        expense = Expense(date, selected_category, amount, is_repeated, payment_method)

        # Save the expense to file
        self.tracker.add_expense(date, selected_category, amount, is_repeated, payment_method)

        # Clear entry fields after adding expense
        self.clear_entry_fields()

        messagebox.showinfo("Expense Added", "Expense has been successfully added.")

def main():
    global user
    user = User()
    root = tk.Tk()
    app = ExpenseGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
