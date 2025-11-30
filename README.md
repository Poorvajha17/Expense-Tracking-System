# Expense Tracking System

A simple and intuitive desktop application built using **Python** and **Tkinter GUI** for tracking daily expenses, managing budgets, and visualizing spending patterns. The system supports user login, multiple expense categories, and persistent storage for long-term financial tracking.

## Overview

The Expense Tracking System helps users record, monitor, and analyze their expenses efficiently. With a clean Tkinter interface, users can log expenses across various categories, set monthly budgets, and visualize spending trends. All data is saved in CSV files, ensuring persistence across sessions.

## Features

**Login System**  
- Secure user login using credentials stored in a text file  
- Personalized expense tracking for each user  

**Expense Tracking**  
- Add expenses with:  
  - Category  
  - Amount  
  - Date (via calendar widget)  
  - Payment method  
  - Repeatability option  
- View all expenses with month-wise filtering  

**Monthly Expense Visualization**  
- Beautiful bar charts generated using **matplotlib**  
- Clear view of spending patterns per month  

**Persistent Storage**  
- All expenses and budgets saved in CSV files  
- Data preserved even after closing the app  

**Budget Management**  
- Set monthly budget limits for each category  
- Compare actual spending vs. budgeted amounts  

## Requirements

- Python 3.x  
- Tkinter (included with Python)  
- matplotlib  
- tkcalendar  
- csv (built-in module)  

### Install required libraries:
```bash
pip install matplotlib tkcalendar
```

## Installation
- Clone the Repository
```bash
git clone https://github.com/Poorvajha17/Expense-Tracking-System.git
```

- Install Dependencies
- Run the Application
```bash
python main1.py
```
