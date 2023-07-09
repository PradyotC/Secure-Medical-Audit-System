from MedicalDataSystem import MedicalData
import json

class AuditServer:
    def __init__(self, file_path, blockchain_file_path):
        self.md = MedicalData(file_path, blockchain_file_path)

    #this methods receives json from the client converts it into dictionary and calls the appropriate method
    def receive_data(self,data:dict)->bytes:
        if data["function"] == "create_record":
            return json.dumps(self.md.create_record(data["user_type"], data["user_id"], data["patient_id"], data["record_id"], data["record_data"])).encode()
        elif data["function"] == "delete_record":
            return json.dumps(self.md.delete_record(data["user_type"], data["user_id"], data["patient_id"], data["record_id"])).encode()
        elif data["function"] == "update_record":
            return json.dumps(self.md.update_record(data["user_type"], data["user_id"], data["patient_id"], data["record_id"], data["record_data"])).encode()
        elif data["function"] == "get_records":
            return json.dumps(self.md.get_records(data["user_type"], data["user_id"], data["patient_id"])).encode()
        elif data["function"] == "print_record":
            return json.dumps(self.md.print_record(data["user_type"], data["user_id"], data["patient_id"], data["record_id"])).encode()
        elif data["function"] == "copy_record":
            return json.dumps(self.md.copy_record(data["user_type"], data["user_id"], data["patient_id"], data["record_id"], data["new_patient_id"], data["new_record_id"])).encode()
        elif data["function"] == "query_user_logs":
            return json.dumps(self.md.query_user_logs(data["user_type"], data["user_id"], data["patient_id"])).encode()
        else:
            return json.dumps(("Error", "Invalid function")).encode()
