import requests
import time

# Zumo IP from Arduino IDE serial monitor
zumo_ip = "http://7.32.122.209"

# function for HTTP request  
def send_command(command):
    try:
        url = f"{zumo_ip}/{command}"
        response = requests.get(url)
        print(f"Sent: {command} | Status: {response.status_code}")
    except Exception as e:
        print("Error:", e)

# example commands
send_command("forward")
time.sleep(1)
send_command("stop")

