# version 1
# from flask import Flask, request, render_template
# import os
# from deepface import DeepFace
# from datetime import datetime
# from pyngrok import ngrok
# ngrok.set_auth_token("34erTHBTd3aLR9F3DNcXFFHP3U2_4FqtVm6bCKdKwwVvzxV96") # 👈 import ngrok

# app = Flask(__name__)

# latest_image_path = None
# latest_name = None
# latest_score = None

# @app.route('/')
# def home():
#     return render_template("index.html", image_path=latest_image_path, name=latest_name, score=latest_score)

# @app.route('/verify_face', methods=['POST'])
# def verify_face():
#     global latest_image_path, latest_name, latest_score
#     file_path = "static/latest.jpg"

#     # Save uploaded image
#     with open(file_path, "wb") as f:
#         f.write(request.data)

#     # Run face recognition
#     result = DeepFace.find(img_path=file_path, db_path="faces", model_name="Facenet")
#     if not result.empty:
#         latest_name = result.iloc[0]["identity"].split("/")[-1].split(".")[0]
#         latest_score = 1 - result.iloc[0]["distance"]
#     else:
#         latest_name = "Unknown"
#         latest_score = 0.0

#     latest_image_path = file_path
#     print(f" Recognized: {latest_name} ({latest_score:.3f})")

#     return " Face verified!"

# if __name__ == '__main__':
#     #  Start ngrok tunnel automatically
#     public_url = ngrok.connect(5000)
#     print(f"\n Public URL: {public_url.public_url}")
#     print("Copy this URL into your ESP32 sketch as `serverUrl`\n")

#     # Start Flask app
#     app.run(host='0.0.0.0', port=5000)


# version 2, 1

# from flask import Flask, request, render_template
# from deepface import DeepFace
# import numpy as np
# import pickle
# from datetime import datetime
# import os
# from pyngrok import ngrok

# # Flask app setup
# app = Flask(__name__)

# # Authenticate ngrok (only once needed per system)
# ngrok.set_auth_token("34erTHBTd3aLR9F3DNcXFFHP3U2_4FqtVm6bCKdKwwVvzxV96")

# # Load pretrained embeddings (update the path to your local .pkl file)
# with open("family_doorbell_embeddings.pkl", "rb") as f:
#     embeddings = pickle.load(f)

# # Globals to track latest recognition
# latest_image_path = None
# latest_name = None
# latest_score = None

# # Cosine similarity function
# def cosine_similarity(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# @app.route('/')
# def home():
#     return render_template("index.html",
#                            image_path=latest_image_path,
#                            name=latest_name,
#                            score=latest_score)

# @app.route('/verify_face', methods=['POST'])
# def verify_face():
#     global latest_image_path, latest_name, latest_score
#     file_path = "static/latest.jpg"

#     # Save the incoming image
#     with open(file_path, "wb") as f:
#         f.write(request.data)

#     # Get embedding for the new face
#     new_emb = DeepFace.represent(img_path=file_path, model_name="Facenet", enforce_detection=False)[0]["embedding"]

#     # Compare embeddings
#     best_name, best_score = "Unknown", 0
#     for item in embeddings:
#         sim = cosine_similarity(new_emb, item["embedding"])
#         if sim > best_score:
#             best_name, best_score = item["name"], sim

#     latest_image_path = file_path
#     latest_name = best_name
#     latest_score = best_score

#     print(f" Recognized: {best_name} (score: {best_score:.3f})")

#     return f"{best_name} ({best_score:.2f})"

# if __name__ == '__main__':
#     # Start ngrok tunnel
#     public_url = ngrok.connect(5000).public_url
#     print(f"\n Public URL: {public_url}")
#     print(" Copy this URL into your ESP32 sketch as `serverUrl`\n")

#     # Run Flask
#     app.run(host='0.0.0.0', port=5000)

# Version 2, 2
from flask import Flask, request, render_template
from deepface import DeepFace
import numpy as np
import pickle
import os
import time
from datetime import datetime
from pyngrok import ngrok

# =========================
# Flask app setup
# =========================
app = Flask(__name__)

# Authenticate ngrok (replace token if needed)
ngrok.set_auth_token("34erTHBTd3aLR9F3DNcXFFHP3U2_4FqtVm6bCKdKwwVvzxV96")

# Load pretrained embeddings (dict: {name: embedding(s)})
with open("family_doorbell_embeddings.pkl", "rb") as f:
    embeddings = pickle.load(f)

# Globals for UI
latest_image_path = None
latest_name = None
latest_score = None

# =========================
# Cosine similarity
# =========================
def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# =========================
# Disable caching for browser
# =========================
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# =========================
# Home route
# =========================
@app.route('/')
def home():
    return render_template(
        "index.html",
        image_path=latest_image_path,
        name=latest_name,
        score=latest_score,
        timestamp=time.time()  # forces new image reload each refresh
    )

# =========================
# Face verification route
# =========================
@app.route('/verify_face', methods=['POST'])
def verify_face():
    global latest_image_path, latest_name, latest_score

    # Save image with temp name then overwrite
    temp_path = f"static/latest_{int(time.time())}.jpg"
    with open(temp_path, "wb") as f:
        f.write(request.data)

    final_path = "static/latest.jpg"
    if os.path.exists(final_path):
        os.remove(final_path)
    os.rename(temp_path, final_path)

    # Generate embedding for the new face
    try:
        new_emb = DeepFace.represent(
            img_path=final_path,
            model_name="Facenet",
            enforce_detection=False
        )[0]["embedding"]
    except Exception as e:
        print("Error generating embedding:", e)
        return "Error processing image", 500

    # Compare with stored embeddings
    best_name, best_score = "Unknown", 0.0
    for name, emb in embeddings.items():
        emb_array = np.array(emb)

        if len(emb_array.shape) == 2:  # multiple embeddings per person
            sims = [cosine_similarity(new_emb, e) for e in emb_array]
            sim = max(sims)
        else:
            sim = cosine_similarity(new_emb, emb_array)

        if sim > best_score:
            best_name, best_score = name, sim

    # Threshold for recognition
    THRESHOLD = 0.70
    if best_score < THRESHOLD:
        best_name = "Unknown"

    # Update globals
    latest_image_path = final_path
    latest_name = best_name
    latest_score = best_score

    print(f" Recognized: {best_name} (score: {best_score:.3f})")

    return f"{best_name} ({best_score:.2f})"

# =========================
# Run Flask + Ngrok
# =========================
if __name__ == '__main__':
    public_url = ngrok.connect(5000).public_url
    print(f"\n🌍 Public URL: {public_url}")
    print("📡 Copy this URL into your ESP32 sketch as `serverUrl`\n")

    app.run(host='0.0.0.0', port=5000)

# Version -3
# from flask import Flask, request, jsonify, render_template
# from deepface import DeepFace
# import numpy as np
# import pickle, os, time
# from sklearn.metrics.pairwise import cosine_similarity
# from pyngrok import ngrok

# # ==================================
# # Flask Setup
# # ==================================
# app = Flask(__name__)
# os.makedirs("static", exist_ok=True)

# # Ngrok Authentication
# ngrok.set_auth_token("34erTHBTd3aLR9F3DNcXFFHP3U2_4FqtVm6bCKdKwwVvzxV96")

# # Load Pretrained Embeddings
# with open("family_doorbell_embeddings.pkl", "rb") as f:
#     embeddings = pickle.load(f)

# # Globals for the UI
# latest_image_path = None
# latest_name = None
# latest_score = None


# # ==================================
# # Helper: Cosine Similarity
# # ==================================
# def cosine_sim(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# # ==================================
# # Face Recognition Logic
# # ==================================
# def recognize_face(image_path):
#     try:
#         rep = DeepFace.represent(
#             img_path=image_path,
#             model_name="Facenet",
#             enforce_detection=False
#         )[0]["embedding"]

#         scores_by_person = {}

#         for person_name, person_embs in embeddings.items():
#             sims = [cosine_sim(rep, emb) for emb in person_embs]
#             top_k = sorted(sims, reverse=True)[:3]
#             avg_sim = np.mean(top_k)
#             scores_by_person[person_name] = avg_sim

#         best_person = max(scores_by_person, key=scores_by_person.get)
#         best_score = scores_by_person[best_person]

#         if best_score < 0.5:
#             return "Unknown", float(best_score)
#         else:
#             return best_person, float(best_score)

#     except Exception as e:
#         print("Recognition error:", e)
#         return "Error", 0.0


# # ==================================
# # Route: ESP32-CAM sends image
# # ==================================
# @app.route("/verify_face", methods=["POST"])
# def verify_face():
#     global latest_image_path, latest_name, latest_score

#     try:
#         image_data = request.data
#         if not image_data:
#             return jsonify({"status": "error", "message": "No image data received"}), 400

#         # Optional: remove old image
#         old_path = os.path.join("static", "latest.jpg")
#         if os.path.exists(old_path):
#             os.remove(old_path)

#         # Save new image
#         img_path = os.path.join("static", "latest.jpg")
#         with open(img_path, "wb") as f:
#             f.write(image_data)

#         # Recognize the face
#         name, score = recognize_face(img_path)
#         print(f" Recognized: {name} (Confidence: {score:.2f})")

#         # Cache-busting trick for browser
#         timestamp = int(time.time())
#         latest_image_path = f"static/latest.jpg?t={timestamp}"
#         latest_name = name
#         latest_score = score

#         # Return response to ESP32
#         return jsonify({
#             "status": "success",
#             "name": name,
#             "confidence": score
#         })

#     except Exception as e:
#         print("Error verifying face:", e)
#         return jsonify({"status": "error", "message": str(e)}), 500


# # ==================================
# # Home Page (Live Status)
# # ==================================
# @app.route("/")
# def home():
#     return render_template(
#         "index.html",
#         image_path=latest_image_path,
#         name=latest_name,
#         score=latest_score
#     )


# # ==================================
# # Run Flask + Ngrok
# # ==================================
# if __name__ == "__main__":
#     print(" Smart Doorbell Flask server started!")
#     public_url = ngrok.connect(5000).public_url
#     print(f"\n Public URL: {public_url}")
#     print(" Copy this URL into your ESP32 sketch as `serverUrl`\n")

#     app.run(host="0.0.0.0", port=5000)

