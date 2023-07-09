import socket
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import json
import hashlib
from AuditServer import AuditServer
import time
import threading
import cryptography.exceptions

prev_message = None

#Check if users.json exists and if it does, load it into a dictionary
try:
    with open("users.json", "r") as f:
        user_data = json.load(f)
except:
    user_data = {}

#save data to json file
def save_data():
    with open("users.json", "w+") as f:
        json.dump(user_data, f, indent=4)

#padding function
def pad_message(message):
    while len(message) % 16 != 0:
        message += b"\0"
    return message

# Encrypt and send some data to the client using AES-GCM
def send_encrypted_data(sock, key, data, cipher):
    if not sock: return
    nonce = secrets.token_bytes(12)
    cipher = AESGCM(key)
    encrypted_data = cipher.encrypt(nonce, data, None)
    encrypted_data = nonce + encrypted_data
    while True:
        sock.sendall(encrypted_data)
        ack = sock.recv(3)
        if ack == b"ok\0":
            break

def receive_and_decrypt(sock:socket.socket, cipher)->bytes:
    while True:
        try:
            encrypted_data = sock.recv(1024)
        except OSError:
            return b""
        if not encrypted_data:
            return b""
        nonce = encrypted_data[:12]
        try:
            decrypted_data = cipher.decrypt(nonce, encrypted_data[12:], None)
            sock.sendall(b"ok\0")
            return decrypted_data
        except cryptography.exceptions.InvalidTag:
            sock.sendall(b"err")

# SHA256 hash function
def sha(message): return hashlib.sha256(message).hexdigest()

shaPassStr,shaTypeStr = sha("password".encode()),sha("type".encode())
shapatient,shaauditor = sha("patient".encode()),sha("auditor".encode())

adts = AuditServer("medical_data.json", "blockchain.txt")

integrity_conn = False
conn2,pre_master_secret,cipher = None,None,None

def check_integrity_thread(stop_event):
    while not stop_event.is_set():
        if not adts.md.check_integrity():
            print("\nError: No data integrity in the server's database\n")
            if integrity_conn:
                send_encrypted_data(conn2, pre_master_secret, pad_message("\n\nError: No data integrity in the server's database\n".encode()), cipher)
        time.sleep(8)

# Start the check_integrity thread
stop_event = threading.Event()
check_integrity = threading.Thread(target=check_integrity_thread, args=(stop_event,))
check_integrity.start()

while True:

    try:

        # Create a new socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific IP address and port
        s.bind(('localhost', 1345))

        # Listen for incoming connections
        s.listen(1)

        # Accept a new connection from a client
        conn, addr = s.accept()

        # Generate a new RSA key pair
        rsa_key = RSA.generate(2048)

        # Send the RSA public key to the client
        public_key = rsa_key.publickey().exportKey()
        conn.sendall(public_key)

        # Receive the AES-encrypted pre-master secret from the client
        encrypted_secret = conn.recv(1024)
        # Decrypt the pre-master secret using the RSA private key
        pre_master_secret = rsa_key.decrypt(encrypted_secret)

        # Create an AES-GCM cipher object using the pre-master secret
        cipher = AESGCM(pre_master_secret)

        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.bind(('localhost', 1280))
        s2.listen(1)

        # conn2, addr2 = s2.accept()

        while True:
            conn2, addr2 = s2.accept()
            if addr[0] == addr2[0]:
                break
            conn2.close()
        
        integrity_conn = True

        decrypted_username = receive_and_decrypt(conn,cipher)
        decrypted_username = decrypted_username.rstrip(b"\0").decode()

        # sha_username = sha(decrypted_username.encode())
        # sha_username_str = str(sha_username)

        sha_username_str = sha(decrypted_username.encode())


        if sha_username_str in user_data:
            send_encrypted_data(conn, pre_master_secret, pad_message("Enter password".encode()), cipher)
            decrypted_password = receive_and_decrypt(conn,cipher)
            decrypted_password = decrypted_password.rstrip(b"\0").decode()
            sha_password = sha(decrypted_password.encode())
            if sha_password == user_data[sha_username_str][shaPassStr]:
                send_encrypted_data(conn, pre_master_secret, pad_message("Login successful".encode()), cipher)
                if user_data[sha_username_str][shaTypeStr] == shapatient:
                    usertype = "patient"
                    send_encrypted_data(conn, pre_master_secret, pad_message("patient".encode()), cipher)
                else:
                    usertype = "auditor"
                    send_encrypted_data(conn, pre_master_secret, pad_message("auditor".encode()), cipher)
            else:
                send_encrypted_data(conn, pre_master_secret, pad_message("Login unsuccessful".encode()), cipher)
                raise ValueError("Login unsuccessful")
        else:
            send_encrypted_data(conn, pre_master_secret, pad_message("You are not registered as a user. Please enter a password".encode()), cipher)
            decrypted_password = receive_and_decrypt(conn,cipher)
            decrypted_password = decrypted_password.rstrip(b"\0").decode()
            sha_password = sha(decrypted_password.encode())

            send_encrypted_data(conn, pre_master_secret, pad_message("Enter UserType".encode()), cipher)
            decrypted_usertype = receive_and_decrypt(conn,cipher)
            decrypted_usertype = decrypted_usertype.rstrip(b"\0").decode()
            if decrypted_usertype == "Y" or decrypted_usertype == "y":
                usertype = "patient"
                user_data[sha_username_str] = {shaPassStr: sha_password, shaTypeStr: shapatient}
            else:
                usertype = "auditor"
                user_data[sha_username_str] = {shaPassStr: sha_password, shaTypeStr: shaauditor}
            send_encrypted_data(conn, pre_master_secret, pad_message("Registration successful".encode()), cipher)
            save_data()


        send_encrypted_data(conn, pre_master_secret, pad_message("Welcome".encode()), cipher)

        # Receive encrypted data from the client
        while True:
            decrypted_data = receive_and_decrypt(conn,cipher)
            if decrypted_data==b"":
                break
            data = decrypted_data.rstrip(b"\0")
            datadict = json.loads(data)

            # datadict["user_type"] = usertype
            # datadict["user_id"] = decrypted_username
            response = adts.receive_data(datadict)
            padded_response = pad_message(response)
            send_encrypted_data(conn, pre_master_secret, padded_response, cipher)
    except ValueError: pass

    # Close the connection
    if conn: conn.close()
    if conn2: conn2.close()
    if integrity_conn: integrity_conn = False
    if s: s.close()
    if s2: s2.close()
    conn2,pre_master_secret,cipher = None,None,None

    a = input("\nPress Q to quit: ")
    if a == "q" or a=="Q":
        if stop_event: stop_event.set()  # Signal the check_integrity thread to exit the loop
        if check_integrity: check_integrity.join()
        break