# Smart Door Bell System

An IoT-based smart doorbell that uses deep learning–powered facial recognition to identify visitors in real time. Built with ESP32-CAM, Flask, and DeepFace (Facenet), the system enhances home security by distinguishing known family members from unknown visitors and displaying results on a web dashboard.

---

## About the Project

Traditional doorbells provide no information about visitors. This project integrates IoT and AI to automatically capture a visitor’s image, perform facial recognition, and display the identity on a dashboard. The system is designed to be cost-effective, scalable, and suitable for smart home security applications.

---

## Features

* ESP32-CAM–based image capture
* Button-triggered operation for energy efficiency
* Facial recognition using DeepFace (Facenet + RetinaFace)
* Flask backend for image processing
* Web dashboard for real-time results
* Identification of known vs unknown visitors

---

## System Architecture

1. Visitor presses the doorbell button
2. ESP32-CAM captures the image
3. Image is sent to the Flask server via HTTP
4. Facial embeddings are extracted and compared
5. Recognition result is displayed on the dashboard

---

## Tech Stack

* **Hardware:** ESP32-CAM, Push Button, FTDI Programmer
* **Backend:** Flask (Python)
* **Deep Learning:** DeepFace, Facenet, RetinaFace
* **Communication:** HTTP over Wi-Fi
* **Development Tools:** Arduino IDE, VS Code, Google Colab
* **Tunneling:** Ngrok

---

## Dataset

Custom facial dataset of registered family members:

* Shreya – 93 images
* Lakshmi – 69 images
* Nikhil – 33 images

Images include variations in lighting, angles, and expressions to improve recognition accuracy.

---

## Installation

### Prerequisites

* Python 3.8+
* Arduino IDE
* ESP32 board support installed
* Ngrok account

### Backend Setup

```bash
pip install flask deepface numpy opencv-python
```

1. Clone the repository
2. Place the trained `.pkl` embeddings file in the backend directory
3. Start the Flask server

```bash
python app.py
```

4. Expose the local server using Ngrok

```bash
ngrok http 5000
```

---

## Usage

1. Power the ESP32-CAM and connect it to Wi-Fi
2. Press the doorbell button
3. The captured image is sent to the server
4. Recognition result appears on the web dashboard

---

## Results

* Average recognition accuracy: ~92%
* Response time: 5–8 seconds
* Stable communication between ESP32-CAM and Flask server
* Reliable detection of known and unknown visitors

---

## Limitations

* Dependent on internet connectivity
* Processing delay due to cloud-based inference
* Limited dataset size

---

## Future Enhancements

* Cloud deployment (AWS / Azure)
* Mobile application integration
* Multi-factor authentication
* Edge-based face recognition
* Real-time notifications (SMS / Email)

---

## Project Structure

```
Smart-Door-Bell/
│── esp32_cam/
│   └── firmware.ino
│── backend/
│   ├── app.py
│   ├── embeddings.pkl
│   └── templates/
│       └── index.html
│── dataset/
│── README.md
```
