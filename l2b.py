import socket
import ssl
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from getpass import getpass
import zipfile

def xor_strings(s, t) -> bytes:
    """XOR two strings together."""
    return bytes(a ^ b for a, b in zip(s, t))

def get_strings(message):
    """Encrypt the message using a static key and return cipherText as hexadecimal."""
    static_key = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    key = (static_key * ((len(message) // len(static_key)) + 1))[:len(message)].encode('utf8')
    cipherText = xor_strings(message.encode('utf8'), key)
    print('Text:    ', format(int.from_bytes(message.encode('utf8'), byteorder='big'), '0100b'))
    print('Key:     ', format(int.from_bytes(key, byteorder='big'), '0100b'))
    print('New text:', format(int.from_bytes(cipherText, byteorder='big'), '0100b'))
    return cipherText.hex()  # Return hexadecimal string

def encrypt_filename(filename):
    """Encrypt only the file name, keeping the extension unchanged."""
    base, ext = os.path.splitext(filename)
    return get_strings(base) + ext

def send_email_via_socket(email_content, smtp_server, smtp_port, your_email, your_password):
    sock = socket.create_connection((smtp_server, smtp_port))
    sock.recv(1024).decode()
    sock.send(b'EHLO localhost\r\n')
    sock.recv(1024).decode()
    sock.send(b'STARTTLS\r\n')
    tls_ready = sock.recv(1024).decode()
    if '220' in tls_ready:
        context = ssl.create_default_context()
        secure_sock = context.wrap_socket(sock, server_hostname=smtp_server)
        secure_sock.send(b'EHLO localhost\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.send(b'AUTH LOGIN\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.send(base64.b64encode(your_email.encode()) + b'\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.send(base64.b64encode(your_password.encode()) + b'\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.send(f'MAIL FROM: <{your_email}>\r\n'.encode())
        secure_sock.recv(1024).decode()
        secure_sock.send(f'RCPT TO: <{destination_email}>\r\n'.encode())
        secure_sock.recv(1024).decode()
        secure_sock.send(b'DATA\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.send((email_content + '\r\n.\r\n').encode())
        secure_sock.recv(1024).decode()
        secure_sock.send(b'QUIT\r\n')
        secure_sock.recv(1024).decode()
        secure_sock.close()
    else:
        print("Failed to start TLS. Server response: " + tls_ready)
    sock.close()

smtp_server = 'smtp.gmail.com'
smtp_port = 587
your_email = input("Enter your email address: ")
your_password = getpass("Enter your password: ")
destination_email = input("Enter recipient's email address: ")

subject = input("Enter the subject of the email: ")
encrypted_subject = get_strings(subject)
print("Encrypted subject:", encrypted_subject)

body = input("Enter the body of the email: ")
encrypted_body = get_strings(body)
print("Encrypted body:", encrypted_body)

message = MIMEMultipart()
message['From'] = your_email
message['To'] = destination_email
message['Subject'] = encrypted_subject
message.attach(MIMEText(encrypted_body, 'plain'))

isFile = 1
attach_file = input("Do you want to attach a file to this email? (yes/no): ").lower()
if attach_file == 'yes':
    file_path = input("Enter the file path to attach: ")
    if os.path.isdir(file_path):
        isFile = 0
        zip_name = input("Enter the name for the zip file: ")
        encrypted_zip_name = encrypt_filename(zip_name) + ".zip"
        print("Encrypted zip name:", encrypted_zip_name)
        with zipfile.ZipFile(encrypted_zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    encrypted_filename = encrypt_filename(file)
                    zipf.write(os.path.join(root, file), arcname=encrypted_filename)
                    print("Encrypted file name:", encrypted_filename)

        file_path = encrypted_zip_name

    try:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)

        # Extract the base filename and encrypt it
            base_filename = os.path.basename(file_path)
            
        # Add header with encrypted filename but preserving the extension
            if isFile == 0:
                part.add_header("Content-Disposition", f"attachment; filename=\"{base_filename}\"")
            else:
                encrypted_filename = encrypt_filename(base_filename)
                print("Encrypted file name:", encrypted_filename)
                part.add_header("Content-Disposition", f"attachment; filename=\"{encrypted_filename}\"")
            message.attach(part)
    except Exception as e:
        print(f"Could not attach file: {e}")
        exit(1)

email_text = message.as_string()
try:
    send_email_via_socket(email_text, smtp_server, smtp_port, your_email, your_password)
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
