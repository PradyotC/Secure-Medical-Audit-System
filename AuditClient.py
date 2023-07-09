import json

class AuditClient:
    def __init__(self,usertype:str,username:str):
        self.usertype = usertype
        self.username = username
        self.breakflag = False

    def printresponse(self,data:list):
        if self.breakflag:
            return
        if data[0] == "Error":
            print("\nError: "+data[1])
        else:
            print("\nSuccess: "+data[1])
            if len(data)==3:
                print("\nData:")
                if type(data[2]) == list:
                    print("Logs\n")
                    print("Datatime\t\tUser ID\t\tPatient ID\t\tAction")
                    print("----------------------------------------------------------------------")
                    for i in data[2]:
                        print(i[0],"\t",i[1],"\t\t",i[2],"\t\t\t",i[3])
                elif type(data[2]) == dict:
                    for i in data[2]:
                        print(i,":",data[2][i])
                else:
                    print(data[2])
    
    def ask(self)->bytes:
        if self.breakflag:
            return json.dumps({"function":"invalid"}).encode()
        if self.usertype == "auditor":
            print("\nChoose an option:\n")
            print("1. Create a record")
            print("2. Delete a record")
            print("3. Update a record")
            print("4. Get all records")
            print("5. Print a record")
            print("6. Copy a record")
            print("7. Query user logs")
            choice = int(input("\nEnter your choice: "))
            if choice == 1:
                patient_id = input("Enter patient ID: ")
                record_id = input("Enter record ID: ")
                print("Enter record data: ")
                temperature = float(input("Enter temperature: "))
                blood_pressure = input("Enter blood_pressure: ")
                record_data = {"temperature":temperature,"blood_pressure":blood_pressure}
                return json.dumps({"function":"create_record","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id,"record_id":record_id,"record_data":record_data}).encode()
            elif choice == 2:
                patient_id = input("Enter patient ID: ")
                record_id = input("Enter record ID: ")
                return json.dumps({"function":"delete_record","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id,"record_id":record_id}).encode()
            elif choice == 3:
                patient_id = input("Enter patient ID: ")
                record_id = input("Enter record ID: ")
                print("Enter record data: ")
                temperature = float(input("Enter temperature: "))
                blood_pressure = input("Enter blood_pressure: ")
                record_data = {"temperature":temperature,"blood_pressure":blood_pressure}
                return json.dumps({"function":"update_record","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id,"record_id":record_id,"record_data":record_data}).encode()
            elif choice == 4:
                patient_id = input("Enter patient ID: ")
                return json.dumps({"function":"get_records","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id}).encode()
            elif choice == 5:
                patient_id = input("Enter patient ID: ")
                record_id = input("Enter record ID: ")
                return json.dumps({"function":"print_record","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id,"record_id":record_id}).encode()
            elif choice == 6:
                patient_id = input("Enter patient ID: ")
                record_id = input("Enter record ID: ")
                new_patient_id = input("Enter new patient ID: ")
                new_record_id = input("Enter new record ID: ")
                return json.dumps({"function":"copy_record","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id,"record_id":record_id,"new_patient_id":new_patient_id,"new_record_id":new_record_id}).encode()
            elif choice == 7:
                patient_id = input("Enter patient ID: ")
                return json.dumps({"function":"query_user_logs","user_type":self.usertype,"user_id":self.username,"patient_id":patient_id}).encode()
            else:
                return json.dumps({"function":"invalid"}).encode()
        else:
            print("\nChoose an option:\n")
            print("1. Create a record")
            print("2. Delete a record")
            print("3. Update a record")
            print("4. Get all records")
            print("5. Print a record")
            print("6. Query user logs")
            choice = int(input("\nEnter your choice: "))
            if choice == 1:
                record_id = input("Enter record ID: ")
                print("\nEnter record data: ")
                temperature = float(input("Enter temperature: "))
                blood_pressure = input("Enter blood_pressure: ")
                record_data = {"temperature":temperature,"blood_pressure":blood_pressure}
                return json.dumps({"function":"create_record","user_type":self.usertype,"user_id":self.username,"patient_id":self.username,"record_id":record_id,"record_data":record_data}).encode()
            elif choice == 2:
                record_id = input("Enter record ID: ")
                return json.dumps({"function":"delete_record","user_type":self.usertype,"user_id":self.username,"patient_id":self.username,"record_id":record_id}).encode()
            elif choice == 3:
                record_id = input("Enter record ID: ")
                print("\nEnter record data: ")
                temperature = float(input("Enter temperature: "))
                blood_pressure = input("Enter blood_pressure: ")
                record_data = {"temperature":temperature,"blood_pressure":blood_pressure}
                return json.dumps({"function":"update_record","user_type":self.usertype,"user_id":self.username,"patient_id":self.username,"record_id":record_id,"record_data":record_data}).encode()
            elif choice == 4:
                return json.dumps({"function":"get_records","user_type":self.usertype,"user_id":self.username,"patient_id":self.username}).encode()
            elif choice == 5:
                record_id = input("Enter record ID: ")
                return json.dumps({"function":"print_record","user_type":self.usertype,"user_id":self.username,"patient_id":self.username,"record_id":record_id}).encode()
            elif choice == 6:
                return json.dumps({"function":"query_user_logs","user_type":self.usertype,"user_id":self.username,"patient_id":self.username}).encode()
            else:
                return json.dumps({"function":"invalid"}).encode()
