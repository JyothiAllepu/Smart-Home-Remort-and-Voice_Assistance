from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import speech_recognition as sr
import threading

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
LIGHT_PIN = 0           # GPIO 4 for main light
FAN_PIN = 12            # GPIO 12 for fan
BALCONY_LIGHT_PIN = 8   # GPIO 0 for balcony light

GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(BALCONY_LIGHT_PIN, GPIO.OUT)  # Setup balcony light pin

# Initialize Flask app
app = Flask(_name_)

@app.route('/')
def home():
    return render_template('index.html')  # Render the HTML file

@app.route('/light/on')
def light_on():
    GPIO.output(LIGHT_PIN, GPIO.HIGH)
    return "Main Light is ON"

@app.route('/light/off')
def light_off():
    GPIO.output(LIGHT_PIN, GPIO.LOW)
    return "Main Light is OFF"

@app.route('/fan/on')
def fan_on():
    GPIO.output(FAN_PIN, GPIO.HIGH)
    return "Fan is ON"

@app.route('/fan/off')
def fan_off():
    GPIO.output(FAN_PIN, GPIO.LOW)
    return "Fan is OFF"

@app.route('/balcony_light/on')
def balcony_light_on():
    GPIO.output(BALCONY_LIGHT_PIN, GPIO.HIGH)
    return "Balcony Light is ON"

@app.route('/balcony_light/off')
def balcony_light_off():
    GPIO.output(BALCONY_LIGHT_PIN, GPIO.LOW)
    return "Balcony Light is OFF"

@app.route('/light/toggle')
def toggle_light():
    current_state = GPIO.input(LIGHT_PIN)
    new_state = not current_state
    GPIO.output(LIGHT_PIN, new_state)
    return "Main Light is ON" if new_state else "Main Light is OFF"

@app.route('/fan/toggle')
def toggle_fan():
    current_state = GPIO.input(FAN_PIN)
    new_state = not current_state
    GPIO.output(FAN_PIN, new_state)
    return "Fan is ON" if new_state else "Fan is OFF"

@app.route('/balcony_light/toggle')
def toggle_balcony_light():
    current_state = GPIO.input(BALCONY_LIGHT_PIN)
    new_state = not current_state
    GPIO.output(BALCONY_LIGHT_PIN, new_state)
    return "Balcony Light is ON" if new_state else "Balcony Light is OFF"

@app.route('/status')
def get_status():
    status = {
        "light": "ON" if GPIO.input(LIGHT_PIN) else "OFF",
        "fan": "ON" if GPIO.input(FAN_PIN) else "OFF",
        "balcony_light": "ON" if GPIO.input(BALCONY_LIGHT_PIN) else "OFF"
    }
    return jsonify(status)


def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Listening for command...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized: {command}")
                control_devices(command)
            except sr.UnknownValueError:
                print("Could not understand the command")
            except sr.RequestError:
                print("Could not request results, check internet connection")
            except sr.WaitTimeoutError:
                print("No command received in time")

def control_devices(command):
    if "turn on main light" in command:
        GPIO.output(LIGHT_PIN, GPIO.HIGH)
        print("Main Light turned ON")
    elif "turn off main light" in command:
        GPIO.output(LIGHT_PIN, GPIO.LOW)
        print("Main Light turned OFF")
    elif "turn on fan" in command:
        GPIO.output(FAN_PIN, GPIO.HIGH)
        print("Fan turned ON")
    elif "turn off fan" in command:
        GPIO.output(FAN_PIN, GPIO.LOW)
        print("Fan turned OFF")
    elif "turn on balcony light" in command:
        GPIO.output(BALCONY_LIGHT_PIN, GPIO.HIGH)
        print("Balcony Light turned ON")
    elif "turn off balcony light" in command:
        GPIO.output(BALCONY_LIGHT_PIN, GPIO.LOW)
        print("Balcony Light turned OFF")
    else:
        print("Command not recognized")

# Start voice recognition in a separate thread
def start_voice_recognition():
    thread = threading.Thread(target=recognize_command)
    thread.daemon = True
    thread.start()

# Start Flask server
if _name_ == '_main_':
    try:
        start_voice_recognition()  # Start voice recognition
        app.run(host='0.0.0.0', port=5005, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        GPIO.cleanup()  # Reset GPIO on exit