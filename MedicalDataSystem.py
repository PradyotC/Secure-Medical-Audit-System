import json
from BlockChain import BlockChainFile

class MedicalData:
    def __init__(self, file_path, blockchain_file_path):
        self.file_path = file_path
        self.blockchain_file_path = blockchain_file_path
        self.data = self.read_data()
        self.bcf = BlockChainFile(self.blockchain_file_path)
        self.bc = self.bcf.blockchain
    
    def read_data(self):
        try:
            with open(self.file_path) as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def write_data(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    def create_record(self, user_type, user_id, patient_id, record_id, record_data)->tuple:
        data = self.data
        if user_type == 'auditor' or user_id == patient_id:
            if patient_id in data:
                data[patient_id][record_id] = record_data
            else:
                data[patient_id] = {record_id: record_data}
            self.write_data(data)
            self.bc.log_operation(user_id, patient_id, "create")
            self.bcf.store_blockchain()
            return ("Success", "Record created successfully")
        else:
            return ("Error", "User not allowed to create record")
    
    def delete_record(self, user_type, user_id, patient_id, record_id)->tuple:
        data = self.data
        if user_type == 'auditor' or user_id == patient_id:
            if patient_id in data and record_id in data[patient_id]:
                del data[patient_id][record_id]
                if not data[patient_id]:
                    del data[patient_id]
                self.write_data(data)
                self.bc.log_operation(user_id, patient_id, "delete")
                self.bcf.store_blockchain()
                return ("Success", "Record deleted successfully")
            else:
                return ("Error", "Records not found\n\nOR\n\nUser not allowed to delete record")
        else:
            return ("Error", "User not allowed to delete record")
    
    def update_record(self, user_type, user_id, patient_id, record_id, record_data)->tuple:
        data = self.data
        if user_type == 'auditor' or user_id == patient_id:
            if patient_id in data and record_id in data[patient_id]:
                data[patient_id][record_id] = record_data
                self.write_data(data)
                self.bc.log_operation(user_id, patient_id, "update")
                self.bcf.store_blockchain()
                return ("Success", "Record updated successfully")
            else:
                return ("Error", "Records not found\n\nOR\n\nUser not allowed to update record")
        else:
            return ("Error", "User not allowed to update record")
    
    def get_records(self, user_type, user_id, patient_id)->tuple:
        data = self.data
        if user_type == 'auditor' or user_id == patient_id:
            if patient_id in data:
                self.bc.log_operation(user_id, patient_id, "query_records")
                self.bcf.store_blockchain()
                # print(data[patient_id])
                # return data[patient_id]
                return ("Success", "Records found", data[patient_id])
            else:
                # print("No records found for patient ID: {}".format(patient_id))
                # return {}
                return ("Error", "No records found for patient ID: {}".format(patient_id))
        else:
            return ("Error", "User not allowed to query records")
    
    def print_record(self, user_type, user_id, patient_id, record_id)->tuple:
        data = self.data
        if user_type == 'auditor' or user_id == patient_id:
            if patient_id in data and record_id in data[patient_id]:
                self.bc.log_operation(user_id, patient_id, "print_record")
                self.bcf.store_blockchain()
                # print(data[patient_id][record_id])
                return ("Success", "Record found", data[patient_id][record_id])
            else:
                return ("Error", "No records found for patient ID: {}\n\nOR\n\nUser not allowed to print record".format(patient_id))
        else:
            return ("Error", "User not allowed to print record")
    
    def copy_record(self, user_type, user_id, patient_id, record_id, new_patient_id, new_record_id)->tuple:
        data = self.data
        if user_type == 'auditor':
            if patient_id in data and record_id in data[patient_id]:
                record_data = data[patient_id][record_id]
                if new_patient_id in data:
                    data[new_patient_id][new_record_id] = record_data
                else:
                    data[new_patient_id] = {new_record_id: record_data}
                self.write_data(data)
                self.bc.log_operation(user_id, patient_id, "copy_record")
                self.bc.log_operation(user_id, new_patient_id, "create_copy_record")
                self.bcf.store_blockchain()
                return ("Success", "Record copied successfully")
            else:
                return ("Error", "Record not found")
        else:
            return ("Error", "User not allowed to copy record")

    def query_user_logs(self, user_type, user_id, patient_id)->tuple:
        if not (user_id == patient_id or user_type == 'auditor'):
            return ("Error", "User not allowed to query logs")
        if patient_id not in self.data:
            return ("Error", "No records found for patient ID: {}".format(patient_id))
        self.bc.log_operation(user_id, patient_id, "query_logs")
        self.bcf.store_blockchain()
        if user_type == 'auditor':
            returncode,message,logs = self.bc.query_user_logs(user_id, patient_id,usertype='auditor')
        else:
            returncode,message,logs = self.bc.query_user_logs(user_id, patient_id)
        return (returncode,message,logs)

    def check_integrity(self)->tuple:
        check_blockchain = BlockChainFile(self.blockchain_file_path).load_blockchain()
        boolean = True
        for i in range(len(check_blockchain.chain)):
            boolean = boolean and check_blockchain.check_integrity(i)
        return boolean 