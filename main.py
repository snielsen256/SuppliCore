"""
SuppliCore - Nutrition and Supplement Database Manager
Stephen Nielsen
10/6/2023


# install mysql connector
$> pip install mysql-connector-python
$> pip install mysql-connector-python --upgrade


"""
from db_interface import *
import datetime

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
        "DOB": datetime.datetime(2000, 1, 1).strftime(date_format), 
        "weight_kg": 1000.0,
        "Medical_conditions_id": 1
        }
    
    #create(cnx, "Medical_conditions", test_condition)
    create(cnx, "Patients", test_patient)

def main():
    # Load config (login information)
    config = load_config()
    print("Config loaded")

    # start database
    cnx = start_database(config)
    print("Database started")
    
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
                pass
                #delete(cnx, test_tablename, get_table_items_interface(cnx, test_tablename))
            case 6:# if generate report
                #print(get_table_items_interface(cnx, "Patients"))
                patient_MRN = get_table_items_interface(cnx, "Patients")
                print(patient_MRN)
                #report = generate_report(cnx, patient_MRN)
                #print(report)
            case _:# else
                print("Invalid input.")
                continue


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
            "DOB": "",
            "age": 0.0,
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

    # import patient data, convert to dictionary
    patient_data = read(cnx, "Patients", where=f"MRN = {patient_MRN}").to_dict()
    for key in patient_data:
        patient_data[key] = patient_data[key][0]

    # calculate Holliday-Segar formula
    hs = 0.0
    weight = report["header"]["weight_kg"]

    if weight <= 10.0:
        hs = weight * 100.0
    elif weight <= 20.0:
        hs = 1000 + (50 * (weight - 10))
    else:
        hs = 1500 + (20 * (weight - 20))

    report["calculations"]["Holliday-Segar"]["maintenance"] = hs
    report["calculations"]["Holliday-Segar"]["sick_day"] = hs * 1.5

    # calculate WHO REE formula
    sex = report["header"]["sex"]
    age = report["header"]["age"]
    wr = 0.0

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
        print(f"Unknown sex '{sex}'")
    
    report["calculations"]["WHO_REE"] = wr

    # return
    return report



if __name__ == '__main__':
    main()