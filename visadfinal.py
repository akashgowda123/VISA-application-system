import json
import os
from datetime import datetime

# File to store visa application data
DATA_FILE = "visa_applications.json"
USER_DATA_FILE = "user_data.json"

# Load existing applications from the JSON file
def load_applications():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save applications to the JSON file
def save_applications(applications):
    with open(DATA_FILE, "w") as file:
        json.dump(applications, file, indent=4)

# Load user data from the JSON file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user data to the JSON file
def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Generate a unique application ID
def generate_application_id():
    applications = load_applications()
    return f"APP{len(applications) + 1:04d}"

# Check if password is unique across all users
def is_password_unique(password):
    user_data = load_user_data()
    for user in user_data.values():
        if user["password"] == password:
            return False
    return True

# Check if passport number is unique across all applications
def is_passport_unique(passport_number):
    applications = load_applications()
    for app in applications.values():
        if app["passport_number"] == passport_number:
            return False
    return True

# Check if application details already exist
def application_exists(name, passport_number, nationality, university, visa_type):
    applications = load_applications()
    for app in applications.values():
        if (app["name"] == name and 
            app["passport_number"] == passport_number and 
            app["nationality"] == nationality and 
            app["university"] == university and 
            app["visa_type"] == visa_type):
            return True
    return False

# Login functionality
def login(username, password, user_type):
    user_data = load_user_data()
    if username in user_data:
        if user_data[username]["password"] == password and user_data[username]["user_type"] == user_type:
            return True, username, user_type
    return False, None, None

# Register functionality
def register(username, password, user_type):
    user_data = load_user_data()
    if username in user_data:
        return False, "Username already exists."
    
    if not is_password_unique(password):
        return False, "Password must be unique. Please choose a different password."
    
    user_data[username] = {"password": password, "user_type": user_type}
    save_user_data(user_data)
    return True, "Registration successful! Please login."

# Create a new visa application
def create_visa_application(name, passport_number, nationality, university, visa_type):
    if not all([name, passport_number, nationality, university, visa_type]):
        return False, "All fields are required!"
    elif len(passport_number) != 10 or not passport_number.isdigit():
        return False, "Passport number must be exactly 10 digits!"
    elif name == passport_number:
        return False, "Name and Passport Number cannot be the same!"
    elif not is_passport_unique(passport_number):
        return False, "Passport number already exists in our system!"
    elif application_exists(name, passport_number, nationality, university, visa_type):
        return False, "An application with these exact details already exists!"

    application_id = generate_application_id()
    applications = load_applications()
    applications[application_id] = {
        "name": name,
        "passport_number": passport_number,
        "nationality": nationality,
        "university": university,
        "visa_type": visa_type,
        "interview_date": None,
        "interview_location": None,
        "interview_status": "Not Assigned",
        "visa_status": "Pending",
        "visa_expiry_date": None,
        "Renew status": "not renewed",
        "details_updated": False
    }
    save_applications(applications)
    return True, f"Application created successfully! Application ID: {application_id}"

# View details of a visa application
def view_application(application_id):
    applications = load_applications()
    if application_id in applications:
        return True, applications[application_id]
    return False, "Application not found!"

# Assign an interview to an application
def assign_interview(application_id, interview_date, interview_location):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["visa_status"] in ["On Hold", "Suspended"]:
        return False, f"Cannot assign interview. Visa application is {application['visa_status']}."
    elif not all([application["name"], application["passport_number"], application["nationality"], application["university"]]):
        return False, "Cannot assign interview. Missing required details."
    elif not interview_location.strip():
        return False, "Interview location is required!"

    application["interview_date"] = interview_date.strftime("%Y-%m-%d")
    application["interview_location"] = interview_location
    application["interview_status"] = "Assigned"
    save_applications(applications)
    return True, "Interview assigned successfully!"

# Update interview status
def update_interview_status(application_id, new_status):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["interview_status"] == "Assigned":
        application["interview_status"] = new_status
        save_applications(applications)
        return True, "Interview status updated successfully!"
    return False, "No interview assigned to this application."

# Approve or reject a visa application
def approve_reject_visa(application_id, decision, expiry_date):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["visa_status"] in ["On Hold", "Suspended"]:
        return False, f"Cannot process. Visa application is {application['visa_status']}."
    elif application["visa_status"] in ["Pending", "Rejected"]:
        if decision == "Approve":
            application["visa_status"] = "Approved"
            application["visa_expiry_date"] = expiry_date.strftime("%Y-%m-%d")
            save_applications(applications)
            return True, "Visa approved successfully!"
        elif decision == "Reject":
            application["visa_status"] = "Rejected"
            save_applications(applications)
            return True, "Visa rejected."
    return False, "Visa is already approved."

# Renew a visa application
def renew_application(application_id, new_expiry_date):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["visa_status"] in ["On Hold", "Suspended"]:
        return False, f"Cannot renew. Visa application is {application['visa_status']}."
    elif application["visa_expiry_date"]:
        expiry_date = datetime.strptime(application["visa_expiry_date"], "%Y-%m-%d")
        if expiry_date >= datetime.now():
            return False, "Visa is not expired yet. Cannot renew!"
        else:
            application["visa_expiry_date"] = new_expiry_date.strftime("%Y-%m-%d")
            application["Renew status"] = "Renewed"
            save_applications(applications)
            return True, "Visa renewed successfully!"
    return False, "No expiry date found for this application."

# Suspend a visa
def suspend_visa(application_id):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["visa_status"] == "Approved":
        application["visa_status"] = "Suspended"
        save_applications(applications)
        return True, "Visa suspended successfully!"
    return False, "Visa is not approved or is already suspended."

# Unsuspend a visa
def unsuspend_visa(application_id):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["visa_status"] == "Suspended":
        application["visa_status"] = "Approved"
        save_applications(applications)
        return True, "Visa unsuspended successfully!"
    return False, "Visa is not suspended."

# Update user details
def update_user_details(application_id, name, passport_number, nationality, university):
    applications = load_applications()
    if application_id not in applications:
        return False, "Application not found!"

    application = applications[application_id]
    if application["details_updated"]:
        return False, "Details can only be updated once."
    else:
        # Check if new passport number is unique
        if passport_number != application["passport_number"] and not is_passport_unique(passport_number):
            return False, "Passport number already exists in our system!"
        
        application["name"] = name
        application["passport_number"] = passport_number
        application["nationality"] = nationality
        application["university"] = university
        application["details_updated"] = True
        save_applications(applications)
        return True, "Details updated successfully!"

# Command-line interface
def main():
    while True:
        print("\n--- International Student Visa Facilitator ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_type = input("Enter user type (User/Admin): ")
            success, message = register(username, password, user_type)
            print(message)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_type = input("Enter user type (User/Admin): ")
            success, logged_in_user, logged_in_user_type = login(username, password, user_type)
            if success:
                print(f"Logged in as {logged_in_user} ({logged_in_user_type})")
                if logged_in_user_type == "User":
                    user_menu(logged_in_user)
                elif logged_in_user_type == "Admin":
                    admin_menu()
            else:
                print("Invalid username or password.")

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

# User menu
def user_menu(username):
    while True:
        print("\n--- User Menu ---")
        print("1. Create Visa Application")
        print("2. View Application")
        print("3. Update User Details")
        print("4. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Enter name: ")
            passport_number = input("Enter passport number (10 digits): ")
            nationality = input("Enter nationality: ")
            university = input("Enter university: ")
            visa_type = input("Enter visa type (Student/Work): ")
            success, message = create_visa_application(name, passport_number, nationality, university, visa_type)
            print(message)

        elif choice == "2":
            application_id = input("Enter application ID: ")
            success, result = view_application(application_id)
            if success:
                for key, value in result.items():
                    print(f"{key.capitalize()}: {value}")
            else:
                print(result)

        elif choice == "3":
            application_id = input("Enter application ID: ")
            name = input("Enter name: ")
            passport_number = input("Enter passport number (10 digits): ")
            nationality = input("Enter nationality: ")
            university = input("Enter university: ")
            success, message = update_user_details(application_id, name, passport_number, nationality, university)
            print(message)

        elif choice == "4":
            print("Logging out...")
            break

        else:
            print("Invalid choice. Please try again.")

# Admin menu
def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Create Visa Application")
        print("2. View Application")
        print("3. Assign Interview")
        print("4. Update Interview Status")
        print("5. Approve/Reject Visa")
        print("6. Renew Visa")
        print("7. Suspend Visa")
        print("8. Unsuspend Visa")
        print("9. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Enter name: ")
            passport_number = input("Enter passport number (10 digits): ")
            nationality = input("Enter nationality: ")
            university = input("Enter university: ")
            visa_type = input("Enter visa type (Student/Work): ")
            success, message = create_visa_application(name, passport_number, nationality, university, visa_type)
            print(message)

        elif choice == "2":
            application_id = input("Enter application ID: ")
            success, result = view_application(application_id)
            if success:
                for key, value in result.items():
                    print(f"{key.capitalize()}: {value}")
            else:
                print(result)

        elif choice == "3":
            application_id = input("Enter application ID: ")
            interview_date = input("Enter interview date (YYYY-MM-DD): ")
            interview_location = input("Enter interview location: ")
            try:
                interview_date = datetime.strptime(interview_date, "%Y-%m-%d")
                success, message = assign_interview(application_id, interview_date, interview_location)
                print(message)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "4":
            application_id = input("Enter application ID: ")
            new_status = input("Enter new status (Completed/Pending): ")
            success, message = update_interview_status(application_id, new_status)
            print(message)

        elif choice == "5":
            application_id = input("Enter application ID: ")
            decision = input("Enter decision (Approve/Reject): ")
            expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
            try:
                expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                success, message = approve_reject_visa(application_id, decision, expiry_date)
                print(message)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "6":
            application_id = input("Enter application ID: ")
            new_expiry_date = input("Enter new expiry date (YYYY-MM-DD): ")
            try:
                new_expiry_date = datetime.strptime(new_expiry_date, "%Y-%m-%d")
                success, message = renew_application(application_id, new_expiry_date)
                print(message)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "7":
            application_id = input("Enter application ID: ")
            success, message = suspend_visa(application_id)
            print(message)

        elif choice == "8":
            application_id = input("Enter application ID: ")
            success, message = unsuspend_visa(application_id)
            print(message)

        elif choice == "9":
            print("Logging out...")
            break

        else:
            print("Invalid choice. Please try again.")

# Run the program
if __name__ == "__main__":
    main()