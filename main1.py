import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry  # type: ignore


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
            self.username = username
            self.password = password
            self.logged_in = True
            self.save_credentials()
            return True

        if username == self.username and password == self.password:
            self.logged_in = True
            return True

        return False


class Expense:
    def __init__(self, date, category, amount, is_repeated, payment_method):
        if isinstance(date, (datetime, )):
            self.date = date
        else:
            self.date = datetime.strptime(str(date).split()[0], '%Y-%m-%d')
        self.category = category
        self.amount = float(amount)
        self.is_repeated = bool(is_repeated)
        self.payment_method = payment_method


class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.budgets = {}
        self.load_expenses()
        self.load_budgets()

    def load_expenses(self):
        if not self.expenses:
            try:
                with open('expenses.csv', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            amt = float(row.get('Amount', 0) or 0)
                        except ValueError:
                            amt = 0.0
                        expense = Expense(
                            row.get('Date', ''),
                            row.get('Category', ''),
                            amt,
                            row.get('Repeated', 'False') == 'True',
                            row.get('Payment Method', '')
                        )
                        self.expenses.append(expense)
            except FileNotFoundError:
                pass

    def save_expenses(self):
        with open('expenses.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Category', 'Amount', 'Repeated', 'Payment Method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for expense in self.expenses:
                writer.writerow({
                    'Date': expense.date.strftime('%Y-%m-%d'),
                    'Category': expense.category,
                    'Amount': f"{expense.amount:.2f}",
                    'Repeated': 'True' if expense.is_repeated else 'False',
                    'Payment Method': expense.payment_method
                })

    def load_budgets(self):
        default_categories = ["Groceries", "Medical", "Entertainment", "Other"]

        try:
            with open('budgets.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                if not rows:
                    for c in default_categories:
                        self.budgets[c] = 0.0
                    self.save_budgets()
                    return

                for row in rows:
                    cat = row.get('Category', '').strip()
                    if not cat:
                        continue
                    try:
                        budget_val = float(row.get('Budget', 0) or 0)
                    except ValueError:
                        budget_val = 0.0
                    self.budgets[cat] = budget_val

        except FileNotFoundError:
            for c in default_categories:
                self.budgets[c] = 1000.0
            self.save_budgets()

    def save_budgets(self):
        with open('budgets.csv', 'w', newline='') as csvfile:
            fieldnames = ['Category', 'Budget']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for category, budget in self.budgets.items():
                writer.writerow({'Category': category, 'Budget': float(budget)})

    def set_budget(self, category, budget):
        try:
            budget_val = float(budget)
        except ValueError:
            budget_val = 0.0
        self.budgets[category] = budget_val
        self.save_budgets()

    def get_categories(self):
        return list(self.budgets.keys())

    def add_expense(self, date, category, amount, is_repeated, payment_method):
        expense = Expense(date, category, amount, is_repeated, payment_method)
        self.expenses.append(expense)
        self.save_expenses()

    def get_expenses_by_month(self, month):
        return [expense for expense in self.expenses if expense.date.strftime('%Y-%m') == month]


class ExpenseGUI:
    def __init__(self, root, user: User):
        self.root = root
        self.user = user
        self.root.title("Expense Tracker")
        self.tracker = ExpenseTracker()
        self.categories = []

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
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Login Failed", "Please provide both username and password.")
            return

        if self.user.login(username, password):
            self.show_options()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_options(self):
        self.username_label.grid_remove()
        self.username_entry.grid_remove()
        self.password_label.grid_remove()
        self.password_entry.grid_remove()
        self.login_button.grid_remove()

        self.categories = self.tracker.get_categories()

        # Top row buttons
        self.set_budget_button = ttk.Button(self.root, text="Set Budget", command=self.set_budget)
        self.set_budget_button.grid(row=0, column=0, padx=5, pady=5)

        self.view_expenses_button = ttk.Button(self.root, text="View Expenses", command=self.view_expenses)
        self.view_expenses_button.grid(row=0, column=1, padx=5, pady=5)

        self.view_monthly_expenses_button = ttk.Button(self.root, text="View Monthly Expenses", command=self.view_monthly_expenses)
        self.view_monthly_expenses_button.grid(row=0, column=2, padx=5, pady=5)

        self.view_budget_button = ttk.Button(self.root, text="View Budgets", command=self.view_budgets)
        self.view_budget_button.grid(row=0, column=3, padx=5, pady=5)

        # Category combobox
        self.category_label = ttk.Label(self.root, text="Category:")
        self.category_label.grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.categories_combobox = ttk.Combobox(self.root, textvariable=self.category_var, state="readonly")
        self.categories_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.update_category_combobox()

        # Amount entry
        self.amount_label = ttk.Label(self.root, text="Amount:")
        self.amount_label.grid(row=3, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        # Date entry
        self.date_label = ttk.Label(self.root, text="Date:")
        self.date_label.grid(row=4, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(self.root)
        self.date_entry.grid(row=4, column=1, padx=5, pady=5)

        # Repeated checkbox
        self.is_repeated_var = tk.BooleanVar()
        self.is_repeated_checkbutton = ttk.Checkbutton(self.root, text="Repeated", variable=self.is_repeated_var)
        self.is_repeated_checkbutton.grid(row=5, column=1, padx=5, pady=5, sticky="W")

        # Payment method combobox
        self.payment_method_label = ttk.Label(self.root, text="Payment Method:")
        self.payment_method_label.grid(row=6, column=0, padx=5, pady=5)
        self.payment_method_var = tk.StringVar()
        self.payment_method_combobox = ttk.Combobox(self.root, textvariable=self.payment_method_var, state="readonly")
        self.payment_method_combobox.grid(row=6, column=1, padx=5, pady=5)
        self.payment_method_combobox['values'] = ['Cash', 'Credit Card', 'Debit Card', 'Online Payment']

        # Add expense button
        self.add_expense_button = ttk.Button(self.root, text="Add Expense", command=self.add_expense)
        self.add_expense_button.grid(row=7, column=1, padx=5, pady=5)

    def update_category_combobox(self):
        self.categories = self.tracker.get_categories()
        self.categories_combobox['values'] = self.categories
        if self.categories:
            self.categories_combobox.current(0)

    def set_budget(self):
        self.budget_window = tk.Toplevel(self.root)
        self.budget_window.title("Set Budget")

        self.budget_entries = {}

        categories = list(self.tracker.budgets.keys())
        for i, category in enumerate(categories):
            ttk.Label(self.budget_window, text=category).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.budget_window)
            entry.insert(0, str(self.tracker.budgets.get(category, 0.0)))  
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.budget_entries[category] = entry

        ttk.Button(self.budget_window, text="Submit", command=self.submit_budget).grid(row=len(self.budget_entries), column=1, padx=5, pady=5)

    def submit_budget(self):
        updated = False
        for category, entry in self.budget_entries.items():
            budget_val = entry.get().strip()
            if budget_val:
                try:
                    self.tracker.set_budget(category, float(budget_val))
                    updated = True
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Budget for {category} must be a number.")
                    return

        if updated:
            messagebox.showinfo("Success", "Budgets updated successfully!")
            self.update_category_combobox()

        try:
            self.budget_window.destroy()
        except Exception:
            pass

    def view_budgets(self):
        budgets_window = tk.Toplevel(self.root)
        budgets_window.title("View Budgets")

        for i, (category, budget) in enumerate(self.tracker.budgets.items()):
            ttk.Label(budgets_window, text=f"{category}:").grid(row=i, column=0, padx=5, pady=5)
            ttk.Label(budgets_window, text=f"Rs.{budget:.2f}").grid(row=i, column=1, padx=5, pady=5)

    def view_expenses(self):
        expenses_window = tk.Toplevel(self.root)
        expenses_window.title("View Expenses")
        expenses_window.geometry("900x500")

        expenses = self.tracker.expenses

        text_widget = tk.Text(expenses_window, height=30, width=110)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        header = "{:<12}{:<20}{:<12}{:<10}{:<15}\n".format("Date", "Category", "Amount", "Repeat", "Payment Method")
        text_widget.insert(tk.END, header)
        text_widget.insert(tk.END, "-" * 80 + "\n")

        for expense in expenses:
            line = "{:<12}{:<20}{:<12.2f}{:<10}{:<15}\n".format(
                expense.date.strftime('%Y-%m-%d'),
                (expense.category[:18] + '..') if len(expense.category) > 20 else expense.category,
                expense.amount,
                "Yes" if expense.is_repeated else "No",
                expense.payment_method
            )
            text_widget.insert(tk.END, line)

        text_widget.config(state=tk.DISABLED)

    def view_monthly_expenses(self):
        monthly_expenses = {}
        for expense in self.tracker.expenses:
            expense_month = expense.date.strftime('%Y-%m')
            monthly_expenses[expense_month] = monthly_expenses.get(expense_month, 0.0) + expense.amount

        if not monthly_expenses:
            messagebox.showinfo("No Data", "No expense data to plot.")
            return

        try:
            sorted_items = sorted(monthly_expenses.items(), key=lambda kv: datetime.strptime(kv[0], '%Y-%m'))
        except Exception:
            sorted_items = sorted(monthly_expenses.items())

        months, totals = zip(*sorted_items)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(months, totals)
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Expenses')
        ax.set_title('Monthly Expenses')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plot_window = tk.Toplevel(self.root)
        plot_window.title("Monthly Expenses")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_expense(self):
        selected_category = self.categories_combobox.get()
        if not selected_category:
            messagebox.showerror("Error", "Please select a category first.")
            return

        amt_text = self.amount_entry.get().strip()
        if not amt_text:
            messagebox.showerror("Error", "Please enter an amount.")
            return
        try:
            amount = float(amt_text)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        date = self.date_entry.get_date().strftime('%Y-%m-%d')
        is_repeated = self.is_repeated_var.get()
        payment_method = self.payment_method_combobox.get() or "Unknown"

        if selected_category in self.tracker.budgets:
            budget = self.tracker.budgets[selected_category]
            if amount > budget:
                messagebox.showwarning("Budget Warning", f"The amount exceeds the budget for {selected_category} (${budget:.2f}).")

        self.tracker.add_expense(date, selected_category, amount, is_repeated, payment_method)

        self.clear_entry_fields()

        messagebox.showinfo("Expense Added", "Expense has been successfully added.")

    def clear_entry_fields(self):
        try:
            self.amount_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.date_entry.set_date(datetime.today())
        except Exception:
            pass
        try:
            self.is_repeated_var.set(False)
        except Exception:
            pass
        try:
            self.payment_method_combobox.set('')
        except Exception:
            pass

def main():
    user = User()
    root = tk.Tk()
    app = ExpenseGUI(root, user)
    root.mainloop()

if __name__ == "__main__":
    main()
