

# Secure Medical Audit System

This is a secure server-client communication system, specifically tailored for a medical audit use case. The system employs several cryptographic techniques such as RSA and AES-GCM for secure data transfer. The server side manages user authentication and data integrity, while the client side interacts with the server to access or modify data.

## Code Structure

The code consists of several Python files:

- `server.py`: Manages the server-side of the system.
- `client.py`: Manages the client-side of the system.
- `audit_client.py`: A helper class for handling user interaction on the client side.
- `audit_server.py`: A class for processing client requests on the server side.
- `medical_data_system.py`: A class for managing medical records and interacting with the blockchain.
- `blockchain.py`: A class for implementing a blockchain system for maintaining the integrity of medical records.

## Execution Instructions

To execute the system on a Mac OS operating system using the command line interface (CLI), follow these steps:

1. Create a Python virtual environment in the workspace by running the following command: 

```bash
python3 -m venv myenv
```

2. Activate the virtual environment:

```bash
source myenv/bin/activate
```

3. Install the required packages using the `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

4. Rename the `user.json`, `medical_data.json`, and `blockchain.txt` files as per your requirements.

5. Start the server by running the following command:

```bash
python3 server.py
```

6. In a separate terminal, start the client by running the following command:

```bash
python3 client.py
```

7. Follow the on-screen prompts to enter your username, password, and user type (if you are a new user). Once you have entered the system, you will be presented with a menu of options based on your user type (patient or auditor).

8. Perform various tasks by entering the corresponding number from the menu and following the on-screen prompts. You may need to provide additional information, such as the patient ID or the medical record details like temperature and blood pressure.

9. You can continue interacting with the system and performing various operations until you exit the system by not pressing "Y" for the continue option. Once you exit, the client will disconnect from the server, and you can close the terminals.

In the server side after an interaction with a client has ended you can end the server by pressing "Q" or continue with connecting to another client by pressing anything else.

## Conclusion

This system provides a secure way of managing medical audit data, ensuring data integrity and user authentication. The use of cryptographic techniques like RSA and AES-GCM adds an extra layer of security to the communication channel. The implementation of a blockchain system ensures the integrity of the medical records. However, further implementation of the `MedicalDataSystem` class, especially the methods for handling medical data operations, is necessary to fully realize the potential of this system.
