import socket
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import cryptography.exceptions
import secrets
from AuditClient import AuditClient
import json
import threading


try:
    prev_message = None

    # Create a new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2 = None

    # Connect to the server
    s.connect(('localhost', 1345))

    # Receive the RSA public key from the server
    server_public_key = s.recv(1024)

    # Import the RSA public key
    server_rsa_key = RSA.importKey(server_public_key)

    # Generate a new pre-master secret
    pre_master_secret = secrets.token_bytes(16)

    # Create an AES-GCM cipher object using the pre-master secret
    cipher = AESGCM(pre_master_secret)

    # Encrypt the pre-master secret using the RSA public key
    encrypted_secret = server_rsa_key.encrypt(pre_master_secret, 32)[0]

    # Send the encrypted pre-master secret to the server
    s.sendall(encrypted_secret)

    #padding function
    def pad_message(message):
        while len(message) % 16 != 0:
            message += b"\0"
        return message

    # Encrypt and send some data to the server using AES-GCM
    def send_encrypted_data(sock, key, data):
        if not sock:
            return
        nonce = secrets.token_bytes(12)
        encrypted_data = cipher.encrypt(nonce, data, None)
        encrypted_data = nonce + encrypted_data
        while True:
            sock.sendall(encrypted_data)
            ack = sock.recv(3)
            if ack == b"ok\0":
                break

    def receive_and_decrypt(sock:socket.socket)->bytes:
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



    # Function for handling the check_integrity thread
    def check_integrity_thread(stop_event):
        while (not stop_event.is_set()) and s2:
            decrypted_data = receive_and_decrypt(s2)
            if decrypted_data:
                data = decrypted_data.rstrip(b"\0").decode()
                print(data)
                s.close()
                s2.close()
                stop_event.set()
                ac.breakflag = True
                exit() # terminate the thread

    # Create a new socket for check_integritys
    def tryconnect(sock):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 1280))
        return sock

    s2 = None
    trybool = True
    while trybool:
        try:
            s2 = tryconnect(s2)
            trybool = False
        except ConnectionRefusedError:
            pass
        

    # Start the check_integrity thread with the second connection
    stop_event = threading.Event()
    check_integrity = threading.Thread(target=check_integrity_thread, args=(stop_event,))
    check_integrity.start()
        
    # Input Username
    username = input("Enter username: ")
    user_name = pad_message(username.encode())
    send_encrypted_data(s, pre_master_secret, user_name)

    #Receive a response from the server asking for password
    decrypted_data = receive_and_decrypt(s)
    data = decrypted_data.rstrip(b"\0").decode()
    print(data)

    #Input Password
    password = pad_message(input("Enter password: ").encode())
    send_encrypted_data(s, pre_master_secret, password)

    decrypted_data = receive_and_decrypt(s)
    data = decrypted_data.rstrip(b"\0").decode()
    print(data)

    if data == "Login successful":
        decrypted_usertype = receive_and_decrypt(s)
        usertype = decrypted_usertype.rstrip(b"\0").decode()
    elif data == "Login unsuccessful":
        raise ValueError("Login unsuccessful")
    else:
        user_type = input("Enter Y if you are a patient: ").encode()
        usertype = "patient" if (user_type == b"Y" or user_type== b"y") else "auditor"
        send_encrypted_data(s, pre_master_secret, pad_message(user_type)) 

        # receive a response from the server, registeration successful
        decrypted_data = receive_and_decrypt(s)
        data = decrypted_data.rstrip(b"\0").decode()
        print(data)

    decrypted_data = receive_and_decrypt(s).rstrip(b"\0").decode()
    print(decrypted_data)

    print("\nYou are {} usertype\n".format(usertype))

    # AuditClient object ac will be created here
    ac = AuditClient(usertype,username)

    returnloop = True

    while returnloop:
        
        send_encrypted_data(s,pre_master_secret,pad_message(ac.ask()))

        decrypted_data = receive_and_decrypt(s).rstrip(b"\0")
        data:list = json.loads(decrypted_data)
        ac.printresponse(data)

        returnloop = True if input("\nEnter Y to continue: ") in {"Y","y"} else False
except ValueError:
    pass

# Close the connection
if s: s.close()
if s2: s2.close()
if stop_event: stop_event.set()
if check_integrity: check_integrity.join()