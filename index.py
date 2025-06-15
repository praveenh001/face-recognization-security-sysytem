import face_recognition
import cv2
import os
import time
from datetime import datetime
import numpy as np
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Directory containing known faces
KNOWN_FACES_DIR = "known_faces"
# Directory to save recorded videos
OUTPUT_DIR = "unknown_videos"
# Face recognition tolerance (lower = stricter)
TOLERANCE = 0.4
# Minimum face size (in pixels)
MIN_SIZE = 50
# Twilio credentials (replace with your own or use environment variables)
TWILIO_ACCOUNT_SID = "your-twilio-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_PHONE_NUMBER = "your-twilio-number"
RECIPIENT_PHONE_NUMBER = "recivers-phone-number"
# SMS cooldown period (in seconds) to avoid spamming
SMS_COOLDOWN = 60  # Send SMS at most every 60 seconds

# Create output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    print(f"Failed to initialize Twilio client: {e}")
    twilio_client = None

# Load known faces
known_face_encodings = []
known_face_names = []

for person_name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
    if os.path.isdir(person_dir):
        for filename in os.listdir(person_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(person_dir, filename)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if len(encodings) == 1:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(person_name)
                else:
                    print(f"Skipped {image_path}: Found {len(encodings)} faces (expected 1)")

def send_sms_alert():
    """Send SMS alert to the recipient phone number"""
    if twilio_client is None:
        print("Twilio client not initialized, skipping SMS")
        return False
    try:
        message = twilio_client.messages.create(
            body="Alert: Unknown person detected by security camera!",
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER
        )
        print(f"SMS sent successfully: {message.sid}")
        return True
    except TwilioRestException as e:
        print(f"Failed to send SMS: {e}")
        return False

def get_video_writer(frame, filename):
    """Initialize video writer"""
    height, width = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    return cv2.VideoWriter(filename, fourcc, 20.0, (width, height))

def main():
    # Initialize webcam
    video_capture = cv2.VideoCapture(0)
    
    # Recording and SMS variables
    is_recording = False
    out = None
    last_unknown_time = 0
    last_sms_time = 0
    RECORD_BUFFER_SECONDS = 5

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        current_unknown_detected = False
        names = []

        # Process each face
        for face_encoding, face_location in zip(face_encodings, face_locations):
            top, right, bottom, left = face_location
            face_size = right - left
            
            # Skip small faces
            if face_size < MIN_SIZE:
                continue
                
            # Compare with known faces
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                confidence = 1 - distances[first_match_index]
                print(f"Matched {name} with confidence: {confidence:.3f}")
            else:
                current_unknown_detected = True
                min_distance = np.min(distances)
                print(f"Unknown person (closest distance: {min_distance:.3f})")

            names.append(name)

        # Update recording and SMS
        if current_unknown_detected:
            last_unknown_time = time.time()
            if not is_recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_filename = os.path.join(OUTPUT_DIR, f"unknown_{timestamp}.avi")
                out = get_video_writer(frame, video_filename)
                is_recording = True
                print(f"Started recording: {video_filename}")
            
            # Send SMS if cooldown period has passed
            current_time = time.time()
            if current_time - last_sms_time > SMS_COOLDOWN:
                if send_sms_alert():
                    last_sms_time = current_time

        # Stop recording after buffer
        if is_recording and (time.time() - last_unknown_time > RECORD_BUFFER_SECONDS):
            is_recording = False
            out.release()
            print("Stopped recording")
            out = None

        # Write frame
        if is_recording:
            out.write(frame)

        # Draw rectangles
        for (top, right, bottom, left), name in zip(face_locations, names):
            color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

        # Display frame
        cv2.imshow('Video', frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    if is_recording:
        out.release()
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
