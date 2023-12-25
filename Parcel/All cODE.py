import json
from typing import List
from tabulate import tabulate
from datetime import datetime

# File names for data
CUSTOMERS_FILE = 'customers.json'
PARCELS_FILE = 'parcels.json'
BILLS_FILE = 'bills.json'

# User management functions
def reset_system(system):
    confirmation = input("Are you sure you want to reset all parcels and bills? (yes/no): ")

    if confirmation.lower() == 'yes':
        # Clear parcels and bills data
        system["parcels"] = []
        system["bills"] = []

        # Reset current parcel and consignment numbers to default
        system["current_consignment_number"] = 10000000
        system["current_parcel_number"] = 10000000

        # Reset current bill number to default
        system["current_bill_id"] = 10000000

        # Save changes to files
        save_parcels_to_file(system)
        save_bills_to_file(system)

        print("Parcels, bills, and counters reset successfully!")
    else:
        print("Reset operation canceled.")
def initialize_system():
    return {
        "users": [],
        "current_user": None,
        "customers": [],  # Add customers key
        "current_customer_id": 1,  # Add current_customer_id key
        "parcels": [],  # Add parcels key
        "current_consignment_number": 10000000,  # Initialize consignment number to 10000000
        "current_parcel_number": 10000000,  # Initialize parcel number to 10000000
        "bills": [], "current_bill_id": 1,
    }

def login(system, username, password):
    for user in system["users"]:
        if user["username"] == username and user["password"] == password:
            system["current_user"] = user
            return True
    return False

def add_user(system, username, password, role="operator"):
    system["users"].append({"username": username, "password": password, "role": role})

def assign_admin_role(system, index):
    if 0 <= index < len(system["users"]):
        user = system["users"][index]
        if user["role"] != "administrator":
            user["role"] = "administrator"
            print("Administrator role assigned successfully!")
        else:
            print("User already has administrator role.")
    else:
        print("Invalid user index!")

def remove_admin_role(system, index):
    if 0 <= index < len(system["users"]):
        user = system["users"][index]
        if user["role"] == "administrator":
            user["role"] = "operator"
            print("Administrator role removed successfully!")
        else:
            print("User does not have administrator role.")
    else:
        print("Invalid user index!")

def delete_user(system, index):
    if 0 <= index < len(system["users"]):
        del system["users"][index]
        print("User deleted successfully!")
    else:
        print("Invalid user index!")

def get_users_by_role(system, role):
    filtered_users = [user for user in system["users"] if user["role"] == role]
    return filtered_users

def save_users_to_file(system):
    data = system["users"]
    with open('users.json', 'w') as file:
        json.dump(data, file)

def load_users_from_file(system):
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)
            system["users"] = data
    except FileNotFoundError:
        pass

# Pricing functions

table_price = [
    ['Zone A', 'RM8.00', 'RM16.00', 'RM18.00'],
    ['Zone B', 'RM9.00', 'RM18.00', 'RM20.00'],
    ['Zone C', 'RM10.00', 'RM20.00', 'RM22.00'],
    ['Zone D', 'RM11.00', 'RM22.00', 'RM24.00'],
    ['Zone E', 'RM12.00', 'RM24.00', 'RM26.00']
]

def modify_price(destination, new_above_3kg_price):
    for row in table_price:
        if row[0] == destination:
            row[-1] = new_above_3kg_price

def delete_price(destination):
    for row in table_price:
        if row[0] == destination:
            row[-1] = ''

def check_price(destination, weight):
    for row in table_price:
        if row[0] == destination:
            if weight < 1:
                return row[1]
            elif 1 <= weight <= 3:
                return row[2]
            else:
                return row[3]
    return None

def save_pricing_to_file():
    data = table_price
    with open('pricing.json', 'w') as file:
        json.dump(data, file)

def load_pricing_from_file():
    try:
        with open('pricing.json', 'r') as file:
            data = json.load(file)
            table_price.clear()
            table_price.extend(data)
    except FileNotFoundError:
        pass

# Customer management functions

def initialize_customers():
    return {"customers": [], "current_customer_id": 1}

def add_customer(system, name, address, telephone):
    # Find the highest customer ID
    highest_customer_id = max(customer["id"] for customer in system["customers"]) if system["customers"] else 0
    # Assign the next available customer ID
    customer_id = highest_customer_id + 1
    customer = {"id": customer_id, "name": name, "address": address, "telephone": telephone}
    system["customers"].append(customer)

    return customer_id

def modify_customer(system, customer_id, address, telephone):
    for customer in system["customers"]:
        if customer["id"] == customer_id:
            customer["address"] = address
            customer["telephone"] = telephone
            print("Customer details modified successfully!")
            return
    print("Customer not found.")

def view_customers(system):
    if not system["customers"]:
        print("No customers available.")
    else:
        headers = ["Customer ID", "Name", "Address", "Telephone"]
        customer_data = [[customer["id"], customer["name"], customer["address"], customer["telephone"]] for customer in system["customers"]]
        print(tabulate(customer_data, headers=headers, tablefmt="grid"))

def load_customers_from_file(system):
    try:
        with open(CUSTOMERS_FILE, 'r') as file:
            data = json.load(file)
            system["customers"] = data["customers"]
            system["current_customer_id"] = data["current_customer_id"]
    except FileNotFoundError:
        pass

def save_customers_to_file(system):
    data = {"customers": system["customers"], "current_customer_id": system["current_customer_id"]}
    with open(CUSTOMERS_FILE, 'w') as file:
        json.dump(data, file)
def delete_customer(system, customer_id):
    for i, customer in enumerate(system["customers"]):
        if customer["id"] == customer_id:
            # Delete customer
            del system["customers"][i]
            print("Customer deleted successfully!")
            # Save changes to the file
            save_customers_to_file(system)
            return

    print("Customer not found.")
# Parcel handling functions

def initialize_parcels():
    return {"parcels": [], "current_consignment_number": 10000000, "current_parcel_number": 10000000}

def add_parcel(system, customer_id, destination, weight, sender_name, sender_address, sender_telephone):
    consignment_number = generate_unique_consignment_number(system)
    parcel_number = generate_unique_parcel_number(system)
    price = check_price(destination, weight)
    if price is not None:
        parcel = {
            "consignment_number": consignment_number,
            "parcel_number": parcel_number,
            "customer_id": customer_id,
            "destination": destination,
            "weight": weight,
            "sender_name": sender_name,
            "sender_address": sender_address,
            "sender_telephone": sender_telephone,
            "price": price,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        system["parcels"].append(parcel)

        # Generate bill for the consignment
        generate_bill(system, consignment_number)

        return consignment_number, parcel_number
    else:
        print("Invalid destination or weight for pricing. Cannot add parcel.")
        return None

def view_parcels(system):
    if not system["parcels"]:
        print("No parcels available.")
    else:
        headers = ["Consignment Number", "Parcel Number", "Customer ID", "Destination", "Weight", "Sender Name", "Sender Address", "Sender Telephone", "Price", "Date"]
        parcel_data = [[
            parcel["consignment_number"],
            parcel["parcel_number"],
            parcel["customer_id"],
            parcel["destination"],
            parcel["weight"],
            parcel["sender_name"],
            parcel["sender_address"],
            parcel["sender_telephone"],
            parcel["price"],
            parcel["date"]
        ] for parcel in system["parcels"]]
        print(tabulate(parcel_data, headers=headers, tablefmt="grid"))

def load_parcels_from_file(system):
    try:
        with open(PARCELS_FILE, 'r') as file:
            data = json.load(file)
            system["parcels"] = data["parcels"]
            system["current_consignment_number"] = data["current_consignment_number"]
            system["current_parcel_number"] = data["current_parcel_number"]
    except FileNotFoundError:
        pass

def save_parcels_to_file(system):
    data = {
        "parcels": system["parcels"],
        "current_consignment_number": system["current_consignment_number"],
        "current_parcel_number": system["current_parcel_number"]
    }
    with open(PARCELS_FILE, 'w') as file:
        json.dump(data, file)

# Function to generate a bill for a consignment
def generate_unique_parcel_number(system):
    system["current_parcel_number"] = 10000000  # Set the initial value
    while True:
        parcel_number = system["current_parcel_number"]
        system["current_parcel_number"] += 1
        new_parcel_number = f'P{parcel_number}'

        # Check if the generated parcel number is already in use
        if not any(parcel["parcel_number"] == new_parcel_number for parcel in system["parcels"]):
            return new_parcel_number

def create_consignment(system):
    view_customers(system)

    try:
        customer_id = int(input("Enter the customer ID for consignment: "))
        customer = next((c for c in system["customers"] if c["id"] == customer_id), None)

        if customer:
            destination = input("Enter destination: ")
            weight = float(input("Enter weight of the parcel: "))
            sender_name = input("Enter sender's name: ")
            sender_address = input("Enter sender's address: ")
            sender_telephone = input("Enter sender's telephone: ")

            consignment_number, parcel_number = add_parcel(system, customer_id, destination, weight, sender_name, sender_address, sender_telephone)

            if consignment_number:
                print(f"Consignment created successfully! Number: {consignment_number}, Parcel Number: {parcel_number}")
            else:
                print("Failed to create consignment.")
        else:
            print("Customer not found.")
    except ValueError:
        print("Invalid input. Please enter a valid customer ID.")

def generate_unique_consignment_number(system):
    system["current_consignment_number"] = 10000000  # Set the initial value
    while True:
        consignment_number = system["current_consignment_number"]
        system["current_consignment_number"] += 1
        new_consignment_number = f'{consignment_number}'  # Use f-string for correct formatting

        # Check if the generated consignment number is already in use
        if not any(consignment["consignment_number"] == new_consignment_number for consignment in system["parcels"]):
            return new_consignment_number

def delete_parcel_within_consignment(system, consignment_number):
    view_bill(system, consignment_number)
    parcel_number_to_delete = input("Enter the parcel number to delete within this consignment: ")

    for i, parcel in enumerate(system["parcels"]):
        if parcel["consignment_number"] == consignment_number and parcel["parcel_number"] == parcel_number_to_delete:
            del system["parcels"][i]
            print(f"Parcel {parcel_number_to_delete} deleted successfully from the consignment {consignment_number}!")
            save_parcels_to_file(system)
            return

    print(f"Parcel {parcel_number_to_delete} not found in the consignment {consignment_number}.")

def delete_parcel_from_bill(system, consignment_number, parcel_number):
    for i, parcel in enumerate(system["parcels"]):
        if parcel["consignment_number"] == consignment_number and parcel["parcel_number"] == parcel_number:
            del system["parcels"][i]
            print("Parcel deleted successfully from the bill!")
            return
    print("Parcel not found in the bill.")

def generate_bill(system, consignment_number):
    bill = {
        "consignment_number": consignment_number,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "customer_name": None,
        "customer_address": None,
        "customer_telephone": None,
        "items": []
    }

    total_amount = 0

    for parcel in system["parcels"]:
        if parcel["consignment_number"] == consignment_number:
            # Assign customer details once (assuming all parcels in a consignment belong to the same customer)
            if bill["customer_name"] is None:
                customer = next((c for c in system["customers"] if c["id"] == parcel["customer_id"]), None)
                if customer:
                    bill["customer_name"] = customer["name"]
                    bill["customer_address"] = customer["address"]
                    bill["customer_telephone"] = customer["telephone"]

            item = {
                "parcel_number": parcel["parcel_number"],
                "receiver_name": parcel["sender_name"],  # Assuming sender_name is the receiver's name
                "receiver_address": parcel["sender_address"],  # Assuming sender_address is the receiver's address
                "receiver_telephone": parcel["sender_telephone"],  # Assuming sender_telephone is the receiver's telephone
                "destination": parcel["destination"],
                "weight": parcel["weight"],
                "price": float(parcel["price"].replace('RM', ''))
            }

            bill["items"].append(item)
            total_amount += item["price"]

    # Calculate 8% service tax
    service_tax = total_amount * 0.08
    total_amount_with_tax = total_amount + service_tax

    # Update bill with total amount, service tax, and total amount with tax
    bill["total_amount"] = total_amount
    bill["service_tax"] = service_tax
    bill["total_amount_with_tax"] = total_amount_with_tax

    system["bills"].append(bill)
    print("Bill generated successfully!")

def print_pricing_table():
    headers = ["Destination", "Below 1kg", "1-3kg", "Above 3kg"]
    print(tabulate(table_price, headers=headers, tablefmt="grid"))

# Bill management functions
def view_bill(system, consignment_number):
    total_amount = 0
    headers = ["Parcel Number", "Receiver Name", "Receiver Address", "Receiver Telephone", "Destination", "Weight", "Price"]
    bill_data = []
    for parcel in system["parcels"]:
        if parcel["consignment_number"] == consignment_number:
            bill_data.append([
                parcel["parcel_number"],
                parcel["sender_name"],  # Display sender_name as receiver_name
                parcel["sender_address"],  # Display sender_address as receiver_address
                parcel["sender_telephone"],  # Display sender_telephone as receiver_telephone
                parcel["destination"],
                parcel["weight"],
                parcel["price"]
            ])
            # Convert the price to float before adding
            total_amount += float(parcel["price"].replace('RM', ''))

    # Display total amount, service tax, and total amount with tax
    print(tabulate(bill_data, headers=headers, tablefmt="grid"))
    print(f"Total Amount: RM{total_amount:.2f}")
    print(f"Service Tax (8%): RM{total_amount * 0.08:.2f}")
    print(f"Total Amount with Tax: RM{(total_amount + total_amount * 0.08):.2f}")

def view_bills_by_customer(system, customer_id):
    total_amount = 0
    headers = ["Consignment Number", "Parcel Number", "Receiver Name", "Receiver Address", "Receiver Telephone", "Destination", "Weight (KG)", "Price (RM)"]
    bill_data = []
    for parcel in system["parcels"]:
        if parcel["customer_id"] == customer_id:
            price = float(parcel["price"].replace('RM', ''))  # Convert the price to float
            bill_data.append([
                parcel["consignment_number"],
                parcel["parcel_number"],
                parcel["sender_name"],  # Display sender_name as receiver_name
                parcel["sender_address"],  # Display sender_address as receiver_address
                parcel["sender_telephone"],  # Display sender_telephone as receiver_telephone
                parcel["destination"],
                parcel["weight"],
                price  # Use the converted price in calculations
            ])
            total_amount += price

    # Calculate 8% service tax
    service_tax = total_amount * 0.08
    total_amount_with_tax = total_amount + service_tax

    print(tabulate(bill_data, headers=headers, tablefmt="grid"))
    print(f"Total Amount: RM{total_amount:.2f}")
    print(f"Service Tax (8%): RM{service_tax:.2f}")
    print(f"Total Amount with Tax: RM{total_amount_with_tax:.2f}")
def view_bills_by_date(system, start_date, end_date):
    total_amount = 0
    headers = ["Consignment Number", "Parcel Number", "Destination", "Weight", "Price"]
    bill_data = []
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    for parcel in system["parcels"]:
        parcel_date = datetime.strptime(parcel["date"], "%Y-%m-%d")
        if start_datetime <= parcel_date <= end_datetime:
            bill_data.append([
                parcel["consignment_number"],
                parcel["parcel_number"],
                parcel["destination"],
                parcel["weight"],
                parcel["price"]
            ])
            total_amount += parcel["price"]
    print(tabulate(bill_data, headers=headers, tablefmt="grid"))
    print(f"Total Amount: {total_amount}")

def load_bills_from_file(system):
    try:
        with open(BILLS_FILE, 'r') as file:
            data = json.load(file)
            system["bills"] = data["bills"]
    except FileNotFoundError:
        pass

def save_bills_to_file(system):
    data = {"bills": system["bills"]}
    with open(BILLS_FILE, 'w') as file:
        json.dump(data, file)

# Main program
system = initialize_system()
load_users_from_file(system)
load_customers_from_file(system)
load_parcels_from_file(system)
load_bills_from_file(system)
load_pricing_from_file()

while True:
    username = input("Enter your username (or type 'exit' to quit): ")
    if username.lower() == 'exit':
        # Save customers before exiting
        save_customers_to_file(system)
        break

    password = input("Enter your password: ")

    if login(system, username, password):
        if system["current_user"]["role"] == 'administrator':
            print("Welcome, Administrator:", system["current_user"]["username"])
        else:
            print("Welcome, Operator:", system["current_user"]["username"])

        while True:
            if system["current_user"]["role"] == 'operator':
                print("What would you like to do?")
                print("1. Add customer details")
                print("2. Modify customer address and telephone number")
                print("3. View list of customers")
                print("4. Check price of a parcel")
                print("5. Generate list of parcels received")
                print("6. View bill from a consignment number")
                print("7. View bills by customer")
                print("8. View bills by date range")
                print("9. Delete a parcel")
                print("10. Create Consignment")
                print("11. Logout")

                operator_choice = input("Enter the option number: ")

                if operator_choice == '1':
                    name = input("Enter customer name: ")
                    address = input("Enter customer address: ")
                    telephone = input("Enter customer telephone: ")
                    add_customer(system, name, address, telephone)

                elif operator_choice == '2':
                    view_customers(system)
                    customer_id = int(input("Enter the customer ID to modify: "))
                    if customer_id not in (customer["id"] for customer in system["customers"]):
                        print("Customer not found.")
                    else:
                        address = input("Enter new address: ")
                        telephone = input("Enter new telephone number: ")
                        modify_customer(system, customer_id, address, telephone)

                elif operator_choice == '3':
                    view_customers(system)

                elif operator_choice == '4':
                    destination = input("Enter destination: ")
                    weight = float(input("Enter weight of the parcel: "))
                    price = check_price(destination, weight)
                    if price is not None:
                        print(f"The price for the parcel is: {price}")
                    else:
                        print("Invalid destination or weight for pricing. Cannot calculate price.")

                elif operator_choice == '5':
                    view_parcels(system)

                elif operator_choice == '6':
                    consignment_number = int(input("Enter consignment number: "))
                    #checks wheter or not the consignment number that inputted by the user exists within the system or not
                    if consignment_number in (parcel["consignment_number"] for parcel in system["parcels"]):
                        view_bill(system, consignment_number)
                    else:
                        print("Consignment number not found.")

                elif operator_choice == '7':
                    customer_id = int(input("Enter customer ID: "))
                    #checks whether or not the customers id that inputted by the user exists within the system or not
                    if customer_id not in (customer["id"] for customer in system["customers"]):
                        print("Customer not found.")
                    else:
                        view_bills_by_customer(system, customer_id)

                elif operator_choice == '8':
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    #states that the date is invalid since the start date is greater than the end date
                    if start_date > end_date:
                        print("Invalid date range.")
                    #checks whether or not the date that inputted by the user exists within the system +or not
                    elif start_date and end_date not in (parcel["date"] for parcel in system["parcels"]):
                        print("No bills found within the date range.")
                    else:
                        view_bills_by_date(system, start_date, end_date)

                elif operator_choice == '9':
                    consignment_number = int(input("Enter consignment number: "))
                    if consignment_number in (parcel["consignment_number"] for parcel in system["parcels"]):
                        delete_parcel_within_consignment(system, consignment_number)
                    else:
                        print("Consignment number not found.")

                elif operator_choice == '10':
                    create_consignment(system)
                    save_parcels_to_file(system)
                    save_bills_to_file(system)

                elif operator_choice == '11':
                    # Save data before logging out
                    save_customers_to_file(system)
                    save_parcels_to_file(system)
                    save_bills_to_file(system)
                    break

                else:
                    print("Invalid choice")

            elif system["current_user"]["role"] == 'administrator':
                print("What would you like to do?")
                print("1. Add user")
                print("2. Assign administrator role")
                print("3. Remove administrator role")
                print("4. Delete user")
                print("5. List of users")
                print("6. Show Pricing Table")
                print("7. Modify Pricing")
                print("8. Delete Pricing")
                print("9. Check Pricing")
                print("10. Reset Parcels And Bills")
                print("11. Delete Customer")
                print("12. Logout")
                option = input("Enter the option number: ")

                if option == '1':
                    new_username = input("Enter the username for the new user: ")
                    new_password = input("Enter the password for the new user: ")
                    new_role = input("Enter the role for the new user (default: operator): ")
                    add_user(system, new_username, new_password, new_role)
                    print("User added successfully!")
                    save_users_to_file(system)

                elif option == '2':
                    users = get_users_by_role(system, 'operator')
                    if len(users) == 0:
                        print("No operators available to assign as administrators.")
                    else:
                        print("Choose a user to assign as an administrator:")
                        for i, user in enumerate(users):
                            print(f"{i + 1}. {user['username']} (Role: {user['role']})")
                        user_index = int(input("Enter the user number: ")) - 1
                        assign_admin_role(system, user_index)
                        save_users_to_file(system)

                elif option == '3':
                    users = get_users_by_role(system, 'administrator')
                    if len(users) == 0:
                        print("No administrators available to remove the role.")
                    else:
                        print("Choose a user to remove administrator role:")
                        for i, user in enumerate(users):
                            print(f"{i + 1}. {user['username']} (Role: {user['role']})")
                        user_index = int(input("Enter the user number: ")) - 1
                        remove_admin_role(system, user_index)
                        save_users_to_file(system)

                elif option == '4':
                    if len(system["users"]) == 0:
                        print("No users available to delete.")
                    else:
                        print("Choose a user to delete:")
                        for i, user in enumerate(system["users"]):
                            print(f"{i + 1}. {user['username']}")
                        user_index = int(input("Enter the user number: ")) - 1
                        delete_user(system, user_index)
                        save_users_to_file(system)

                elif option == '5':
                    filter_option = input("Filter users by role (admin/operator/all): ")
                    if filter_option.lower() == 'admin':
                        users = get_users_by_role(system, 'administrator')
                        print("List of administrators:")
                        for i, user in enumerate(users):
                            print(f"{i + 1}. {user['username']} (Role: {user['role']})")
                    elif filter_option.lower() == 'operator':
                        users = get_users_by_role(system, 'operator')
                        print("List of operators:")
                        for i, user in enumerate(users):
                            print(f"{i + 1}. {user['username']} (Role: {user['role']})")
                    elif filter_option.lower() == 'all':
                        if len(system["users"]) == 0:
                            print("No users available.")
                        else:
                            print("List of all users:")
                            for i, user in enumerate(system["users"]):
                                print(f"{i + 1}. {user['username']} (Role: {user['role']})")
                    else:
                        print("Invalid filter option!")

                elif option == '6':
                    print("Current Pricing Table:")
                    headers = ['Destination', 'Weight below 1kg', 'Weight in between 1kg to 3kg', 'Weight above 3kg']
                    print(tabulate(table_price, headers=headers, tablefmt="grid"))

                elif option == '7':
                    modify_destination = input("\nEnter the destination to modify the price for parcels above 3kg: ")
                    new_price = input(f"Enter the new price for {modify_destination} (above 3kg): ")
                    modify_price(modify_destination, new_price)
                    save_pricing_to_file()

                elif option == '8':
                    price_to_remove = input("\nEnter the destination to delete the price for parcels above 3kg: ")
                    delete_price(price_to_remove)
                    save_pricing_to_file()

                elif option == '9':
                    destination_to_check = input("\nEnter the destination to check the price: ")
                    weight_to_check = float(input("Enter the weight of the parcel: "))
                    price = check_price(destination_to_check, weight_to_check)
                    if price:
                        print(
                            f"The price for the parcel to {destination_to_check} weighing {weight_to_check}kg is: {price}")
                    else:
                        print("Invalid destination or weight for pricing.")

                elif option == '10':
                    reset_system(system)

                elif option == '11':
                    view_customers(system)
                    try:
                        customer_id_to_delete = int(input("Enter the customer ID to delete: "))
                        delete_customer(system, customer_id_to_delete)
                    except ValueError:
                        print("Invalid input. Please enter a valid customer ID.")

                elif option == '12':
                    print("Logging out...")
                    break

                else:
                    print("Invalid option!")
        else:
                print("Invalid username or password. Please try again.")

