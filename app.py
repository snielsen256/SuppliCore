"""
SuppliCore - Nutrition and Supplement Database Manager
Stephen Nielsen
10/6/2023


# install mysql connector
$> pip install mysql-connector-python
$> pip install mysql-connector-python --upgrade


"""
from db_interface import *
#from GUI import MultiPageApp # imported in main
import datetime as dt
from datetime import datetime

date_format = "%Y-%m-%d"

def test_fill(cnx):
    """
    fills the database with test data. For testing purposes only.
    """
    
    test_tablename = "Supplements"
    test_dict = {"name":"triopenin", "kcal":100.0, "displacement":50.0, "notes":"Not for human consumption"}
    test_dict_2 = {"name":"canopenin", "kcal":1000.0, "displacement":5.0, "notes":"Totally safe for human consumption bro"}
    test_tablename_2 = "Patients"

    test_condition = {"name": "big sad"}

    test_patient = {
        "MRN": 123456, 
        "f_name": "John", 
        "l_name": "Doe", 
        "sex": "M",
        "DOB": dt.datetime(2000, 1, 1).strftime(date_format), 
        "weight_kg": 1000.0,
        "Medical_conditions_id": 1
        }
    
    create(cnx, "Medical_conditions", test_condition)
    cnx.commit()
    create(cnx, "Patients", test_patient)
    cnx.commit()

def main():
    from GUI import MultiPageApp

    # Load config (login information)
    config = load_config()
    print("Config loaded")

    # start database
    cnx = start_database(config)
    print("Database started")
    #test_fill(cnx)
    
    # open GUI
    app = MultiPageApp(cnx)
    app.mainloop()

    
    """
    # Text navigation made redundant by GUI

    # user choice
    in_main_loop = True
    while in_main_loop:
        
        # user input
        print("--------------------")
        print("What would you like to do?")
        user_input = input("1) Exit 2) Create 3) Read 4) Update 5) Delete 6) Generate report: ")
        print()
        try:
            user_input = int(user_input)
        except:
            print("Invalid input.")
            continue
        
        # choice
        match user_input:
            case 1:#if exit
                print("Exiting")
                in_main_loop = False
                break
            case 2:# if create
                test_fill(cnx)
            case 3:# if read
                returned = read(cnx, get_table_names_interface(cnx, config))
                if returned.empty:
                    print("Table is empty")
                else:
                    print(returned)
            case 4:# if update
                pass
                #update(cnx, test_tablename, get_table_items_interface(cnx, test_tablename), test_dict_2)
            case 5:# if delete
                tablename = get_table_names_interface(cnx, config)
                item_id = get_table_items_interface(cnx, tablename)
                if item_id == 0:
                    continue
                delete(cnx, tablename, item_id)
            case 6:# if generate report
                patient_MRN = get_table_items_interface(cnx, "Patients")
                report = generate_report(cnx, patient_MRN)
                print(report)
                user_input = input("Would you like to save this report? (y/n): ")
                if user_input[:1].lower() == "y":
                    save_report_JSON(report)
                else:
                    print("Not saved.")
            case _:# else
                print("Invalid input.")
                continue
        """

    # close database
    close_database(cnx)
    print("Database closed")

    # end program
    print("TERMINATED")
    
def generate_report(cnx, patient_MRN: int):
    """
    creates a report
    * Parameters:
           * cnx - the connection to the database
           * patient_MRN: int - The MRN, used to identify the patient
    * Returns: 
           * report: dict
    """
    report = {
        "header": {
            "name": "",
            "sex": "",
            "MRN": "",
            "DOB": "",
            "age": 0.0,
            "age_unit": "",
            "weight_kg": 0.0,
            "current_date": "",
            "feeding_schedule": "",
            "method_of_delivery": "",
            "home_recipe": "",
            "fluids": "",
            "solids": ""
        },
        "food_and_supplements": {
            "": 0.0,
            "total_formula_only": 0.0,
            "total_food_and_formula": 0.0,
        },
        "calculations": {
            "Holliday-Segar": {
                "maintenance": 0.0,
                "sick_day": 0.0
            },
            "WHO_REE": 0.0
        }
    }

    # Import patient data, convert to dictionary
    patient_data = read(cnx, "Patients", where=f"MRN = {patient_MRN}").to_dict()
    for key in patient_data:
        patient_data[key] = patient_data[key][0]

    # Fill report with known data
    for key in ["MRN", "DOB", "sex", "weight_kg"]:
        report["header"][key] = patient_data[key]
    report["header"]["DOB"] = dt.datetime.strftime(report["header"]["DOB"], date_format)
    report["header"]["name"] = f"{patient_data['l_name']}, {patient_data['f_name']}"

    # Current date and age
    report["header"]["current_date"] = datetime.now().strftime(date_format)
    curr_date = dt.datetime.strptime(report["header"]["current_date"], date_format)
    DOB = dt.datetime.strptime(report["header"]["DOB"], date_format)
    age_dict = calculate_age(DOB, curr_date)
    report["header"]["age_unit"] = age_dict["age_unit"]
    report["header"]["age"] = age_dict["age"]

    # Holliday-Segar Formula
    weight = report["header"]["weight_kg"]
    if weight <= 10.0:
        hs = weight * 100.0
    elif weight <= 20.0:
        hs = 1000 + (50 * (weight - 10))
    else:
        hs = 1500 + (20 * (weight - 20))
    report["calculations"]["Holliday-Segar"]["maintenance"] = hs
    report["calculations"]["Holliday-Segar"]["sick_day"] = hs * 1.5

    # WHO REE Formula
    sex = report["header"]["sex"]
    age = report["header"]["age"]
    if sex == "M":
        if age <= 3:
            wr = (weight * 60.9) - 54
        elif age <= 10:
            wr = (weight * 22.7) + 495
        else:
            wr = (weight * 17.5) + 651
    elif sex == "F":
        if age <= 3:
            wr = (weight * 60.1) - 51
        elif age <= 10:
            wr = (weight * 22.5) + 499
        else:
            wr = (weight * 12.2) + 746
    else:
        wr = 0.0  # Default value for unknown sex
    report["calculations"]["WHO_REE"] = wr

    return report

def save_report_JSON(report: dict):
    """
    Saves a report as a JSON file
    * Parameters:
           * report: dict - The report, as outputted by generate_report()
    * Returns: None 
    """
    from GUI import save_info_popup
    
    try:
        # if it comes from generate_report()
        filename = f"report_out/{report['header']['MRN']}-({report['header']['current_date']}).json"
    except:
        # if it comes from the GUI
        filename = f"report_out/{report['MRN']}-({report['current_date']}).json"
        print(report)


    with open(filename, "w") as file: 
        json.dump(report, file)

    save_info_popup(info_text=f"Saved as {filename}")
    print(f"Saved as {filename}")

def calculate_age(DOB: datetime, curr_date: datetime):
    """
    Calculates the the age and age units (years, months, days) based off the difference of two dates. Called by generate_report().
    * Parameters:
        * DOB: datetime
        * curr_date: datetime
    * Returns: 
           * dict
                * age: float
                * age_unit: string
    """
    years = curr_date.year - DOB.year

    # Adjust if the birth date has not occurred yet this year
    if (curr_date.month, curr_date.day) < (DOB.month, DOB.day):
        years -= 1

    # Calculate age in months if less than 1 year old
    if years < 1:
        months = (curr_date.year - DOB.year) * 12 + curr_date.month - DOB.month
        if curr_date.day < DOB.day:
            months -= 1  # Adjust if the day of the month hasn't occurred
        if months == 0:
            # Calculate days if less than 1 month old
            days = (curr_date - DOB).days
            return {"age": days, "age_unit": "days"}
        return {"age": months, "age_unit": "months"}

    # Default to returning age in years
    return {"age": years, "age_unit": "years"}

if __name__ == '__main__':
    main()