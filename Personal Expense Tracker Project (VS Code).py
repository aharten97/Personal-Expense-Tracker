###Personal Expense Tracker Project

## 1. ADD AN EXPENSE


#create an empty list

v_total_expenses = []

#promt the user for expense details

v_date = str(input("Please enter the date of the expense (YY-MM-DD): "))
v_category = input("Please enter the category of the expense (Food, Travel, Clothing, Etc.): ")
v_amount = float(input("Please enter the amount of the expense: "))
v_description = input("Please enter a brief description of the expense: ")

#store an expense in a list as a dictionary

v_expense = {
    "date" : v_date,
    "category" : v_category,
    "amount" : v_amount,
    "description" : v_description
}

## 2. VIEW LIST OF EXPENSES

#store multiple expenses by appending a dictionary to the list

v_total_expenses.append(v_expense)

#create a loop to view list of expenses

print("\nTotal Expenses:")
for v_expense in v_total_expenses:
  print(v_expense)

## 3. SET AND TRACK THE BUDGET

#prompt user to set a budget

v_monthly_budget = float(input("Please enter your monthly budget: "))

#track spending with budget

  #add up total expenses using for loop

v_total_spent = 0
for v_expense in v_total_expenses:
  v_total_spent += v_expense["amount"]

  #compare total amount spent to monthly budget using if/else statement

print("\nTotal Amount Spent So Far: " + str(v_total_spent))
if v_total_spent > v_monthly_budget :
  print("You have exceeded your budget!")
else :
  print("You have $" + str(round(v_monthly_budget - v_total_spent, 2)) + " left for the month.")

## 4. SAVE AND LOAD EXPENSES

import csv

#save expenses to a file
with open("expenses.csv", "w", newline="") as v_file :
  writer = csv.writer(v_file)
  #create a header row
  writer.writerow(["date", "category", "amount", "description"])
  #create a for loop to load back into the list of expenses
  for v_expense in v_total_expenses:
    writer.writerow([v_expense["date"], v_expense["category"], v_expense["amount"], v_expense["description"]])

## 5. CREATE AN INTERACTIVE MENU

import csv

#global list to hold expenses

v_total_expenses = []

#create a function to add an expense

def add_expense() :
  v_date = str(input("Please enter the date of the expense (YY-MM-DD): "))
  v_category = input("Please enter the category of the expense (Food, Travel, Clothing, Etc.): ")
  v_amount = float(input("Please enter the amount of the expense: "))
  v_description = input("Please enter a brief description of the expense: ")

  #store in dictionary

  v_expense = {
    "date" : v_date,
    "category" : v_category,
    "amount" : v_amount,
    "description" : v_description
  }

  #add the dictionary to the list
  v_total_expenses.append(v_expense)

#create a function to view list of expenses

def view_expenses() :
  if not v_total_expenses : #check if list is empty
    print("No expenses have been recorded yet. \n")
  else :
    print("\nTotal Expenses:")
    for i in v_total_expenses : #loop through each expense
      print(i) #print each expense in dictionary
    print()

#create a function to track the budget

def track_budget() :
  v_monthly_budget = float(input("Please enter your monthly budget: "))

  #sum "amount" values to calculate total spent so far
  v_total_spent = sum(i["amount"] for i in v_total_expenses)

  print("\nTotal Amount Spent So Far: " + str(round(v_total_spent, 2)))

  #compare total spend to monthly budget
  if v_total_spent > v_monthly_budget :
    print("You have exceeded your budget!")
  else :
    print("You have $" + str(round(v_monthly_budget - v_total_spent, 2)) + " left for the month.\n")

#create a function to save expenses to CSV

def save_expenses() :
  with open("expenses.csv", "w", newline="") as v_file :
    writer = csv.writer(v_file)

    #create header row once at the top of the file
    writer.writerow(["date", "category", "amount", "description"])

    #write each expense in as a row in the CSV
    for i in v_total_expenses :
      writer.writerow([i["date"], i["category"], i["amount"], i["description"]])
  print("Expenses saved to file.\n")

#create a main menu loop

while True :
  print("Menu:")
  print("1. Add expense")
  print("2. View expenses")
  print("3. Track budget")
  print("4. Save expenses")
  print("5. Exit")

  #ask the user to choose an option
  v_choice = input("Please enter a number (1-5) to choose an option: ")

  #use if, elif, and else to match user choice to function
  if v_choice == "1" :
    add_expense()
  elif v_choice == "2" :
    view_expenses()
  elif v_choice == "3" :
    track_budget()
  elif v_choice == "4" :
    save_expenses()
  elif v_choice == "5" :
    save_expenses() #save expenses before exiting
    print("Goodbye!")
    break
  else :
    print("Invalid choice. Please enter a number between 1 and 5.\n")