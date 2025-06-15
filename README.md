
# 🛡️ Face Recognition Surveillance with SMS Alerts

A Python-based home surveillance system that uses **face recognition** to detect known and unknown individuals in real-time via webcam. When an unknown person is detected, it **starts video recording** and sends an **SMS alert** to the specified phone number using **Twilio**.

---

## 📌 Features

- 🔍 Detects faces using `face_recognition` and classifies as **known** or **unknown**.
- 🧠 Loads known faces from a directory and matches with live video feed.
- 🎥 Automatically **records video** when an unknown face is detected.
- 📱 Sends **SMS alerts** via Twilio when unknown faces appear.
- ✅ Stops recording automatically after a few seconds of no unknown activity.
- 📂 Saves recorded videos in a designated directory.

---

## 📁 Project Structure

```text
face-surveillance/
├── known_faces/                  # Folder for known people's images
│   ├── Alice/                    # Person 1
│   │   ├── alice1.jpg            # Image 1
│   │   └── alice2.png            # Image 2
│   └── Bob/                      # Person 2
│       └── bob.jpg               # Single image
│
├── unknown_videos/               # Auto-created recordings
│   └── unknown_20231115_1430.avi # Example video filename
│
├── surveillance.py               # Main application script
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```
---

## ⚙️ Setup Instructions

1. 📦 Install Required Libraries:
    pip install face_recognition opencv-python numpy twilio

> Note: `face_recognition` requires `dlib` which might need CMake and Visual Studio Build Tools on Windows.

2. 📁 Add Known Faces:
```text
    known_faces/
    ├── John/
    │   ├── john1.jpg
    │   └── john2.jpg
    └── Alice/
        └── alice.jpg
```
4. 🔐 Configure Twilio:
Replace the placeholders in the script:

    TWILIO_ACCOUNT_SID = "YOUR_ACCOUNT_SID"
   
    TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
   
    TWILIO_PHONE_NUMBER = "+1234567890"
   
    RECIPIENT_PHONE_NUMBER = "+91XXXXXXXXXX"

6. ▶️ Run the Program:
    python surveillance.py

---

## 🛠️ Configuration

| Variable                | Description                                 | Default         |
|-------------------------|---------------------------------------------|-----------------|
| `TOLERANCE`             | Face matching tolerance (lower = stricter)  | `0.4`           |
| `MIN_SIZE`              | Minimum face size to be considered (pixels) | `50`            |
| `SMS_COOLDOWN`          | SMS cooldown period (in seconds)            | `60` seconds    |
| `RECORD_BUFFER_SECONDS` | Time to keep recording after last unknown   | `5` seconds     |


For bugs or suggestions, open an issue or email:  
📧 `praveenpuni80@gmail.com`  
🌐 GitHub: [@praveenh001](https://github.com/praveenh001)
