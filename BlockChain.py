import hashlib
import datetime
import os

class Block:
    def __init__(self, userID, patientID, action, previous_hash):
        self.timestamp = datetime.datetime.utcnow()
        self.patientID = patientID
        self.userID = userID
        self.action = action
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_contents = str(self.timestamp) + str(self.patientID) + str(self.userID) + str(self.action) + str(self.previous_hash)
        return hashlib.sha256(block_contents.encode()).hexdigest()

class Blockchain:
    def __init__(self,opr=None):
        if opr == "load":
            self.chain = []
        else:
            self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(None, None, None,"0")

    def query_user_logs(self, userID, patientID, usertype="patient"):
        logs = []
        returncode = ""
        message = ""
        if (userID == patientID or usertype=="auditor"):
            for block in self.chain:
                if block.patientID == patientID: #auditor can query any userID
                    logs.append(tuple([block.timestamp.strftime("%Y-%m-%d %H:%M:%S"), block.userID, block.patientID, block.action]))
            if len(logs) == 0:
                returncode = "Error"
                message = "No logs found for user {}".format(patientID)
            else:
                returncode = "Success"
                message = "Logs found for user {}".format(patientID)
        else:
            returncode = "Error"
            message = "User {} not allowed to query logs for user {}".format(userID, patientID)
        return returncode,message,logs

    def log_operation(self, userID, patientID, action):
        previous_block = self.chain[-1]
        new_block = Block(userID, patientID, action, previous_block.hash)
        self.chain.append(new_block)

    def check_integrity(self, block_index):
        block = self.chain[block_index]
        if block.hash != block.calculate_hash():
            return False
        if block_index > 0 and block.previous_hash != self.chain[block_index - 1].hash:
            return False
        return True

class BlockChainFile:
    def __init__(self, filename):
        self.filename = filename
        self.blockchain = self.load_blockchain()

    def store_blockchain(self):
        with open(self.filename, 'w') as f:
            for block in self.blockchain.chain:
                f.write("Timestamp | {}\n".format(block.timestamp))
                f.write("Patient ID | {}\n".format(block.patientID))
                f.write("User ID | {}\n".format(block.userID))
                f.write("Action | {}\n".format(block.action))
                f.write("Previous Hash | {}\n".format(block.previous_hash))
                f.write("Hash | {}\n".format(block.hash))
                f.write("\n")

    def load_blockchain(self)->Blockchain:
        if not os.path.exists(self.filename):
            return Blockchain()
        else:
            blockchain = Blockchain(opr="load")
            with open(self.filename, 'r') as f:
                lines = f.readlines()
                for i in range(0, len(lines), 7):
                    timestampstr = lines[i].strip().split(" | ")[1]
                    timestamp = datetime.datetime.strptime(timestampstr, "%Y-%m-%d %H:%M:%S.%f")
                    patientID = lines[i+1].strip().split(" | ")[1]
                    userID = lines[i+2].strip().split(" | ")[1]
                    action = lines[i+3].strip().split(" | ")[1]
                    previous_hash = lines[i+4].strip().split(" | ")[1]
                    hash = lines[i+5].strip().split(" | ")[1]
                    block = Block(userID, patientID, action, previous_hash)
                    block.timestamp = timestamp
                    block.hash = hash
                    blockchain.chain.append(block)
            return blockchain