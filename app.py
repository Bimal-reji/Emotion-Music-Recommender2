from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
import json
import base64
import cv2
import numpy as np
import os
import random
from werkzeug.utils import secure_filename
from emotion_model.facial_recognition import detect_emotion_from_frame
from emotion_model.text_classifier import detect_emotion_from_text
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------
# Flask + Spotify Configuration
# ------------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Spotify API setup
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)

# Mapping from emotion to Spotify search query keywords
EMOTION_KEYWORDS = {
    "Happy": ["happy", "feel good", "party"],
    "Sad": ["sad", "melancholy", "broken heart"],
    "Angry": ["rage", "metal", "pump up"],
    "Surprise": ["energetic", "pop hits", "trending"],
    "Fear": ["calm", "soothing", "relax"],
    "Disgust": ["dark", "grunge", "emo"],
    "Neutral": ["chill", "lofi", "focus"]
}

# Helper: get Spotify playlist recommendation based on emotion
def get_spotify_playlist(emotion):
    try:
        keywords = EMOTION_KEYWORDS.get(emotion, ["mood"])
        search_term = random.choice(keywords)

        # Search for Spotify playlists related to the emotion keyword
        results = sp.search(q=search_term, type='playlist', limit=5)
        playlists = results['playlists']['items']

        if not playlists:
            return {"error": "No playlists found for this mood."}, None

        # Pick a random playlist
        playlist = random.choice(playlists)
        playlist_info = {
            "name": playlist['name'],
            "description": playlist.get('description', ''),
            "url": playlist['external_urls']['spotify'],
            "image": playlist['images'][0]['url'] if playlist['images'] else None
        }

        # Get playlist tracks
        tracks_data = sp.playlist_tracks(playlist['id'], limit=10)
        tracks = [
            {
                "title": track['track']['name'],
                "artist": track['track']['artists'][0]['name'],
                "url": track['track']['external_urls']['spotify']
            }
            for track in tracks_data['items'] if track.get('track')
        ]

        random_song = random.choice(tracks) if tracks else None

        return {"playlist": playlist_info, "songs": tracks}, random_song

    except Exception as e:
        print(f"Spotify API Error: {e}")
        return {"error": "Spotify fetch failed."}, None


# --- ROUTE FOR SERVING UPLOADED FILES ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- MAIN WEB INTERFACE ---
@app.route('/')
def index():
    return render_template('index.html')


# --- API 1: Webcam Emotion Detection ---
@app.route('/api/detect_emotion', methods=['POST'])
def detect_emotion():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided.'}), 400

        image_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        emotion = detect_emotion_from_frame(frame)
        playlist_data, random_song = get_spotify_playlist(emotion)

        return jsonify({
            'success': True,
            'emotion': emotion,
            'playlist': playlist_data,
            'random_song': random_song
        })
    except Exception as e:
        print(f"Error in detect_emotion: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# --- API 2: Image Upload Detection ---
@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        frame = cv2.imread(filepath)
        if frame is None:
            return jsonify({'success': False, 'error': 'Invalid image file'}), 400

        emotion = detect_emotion_from_frame(frame)
        playlist_data, random_song = get_spotify_playlist(emotion)
        image_url = url_for('uploaded_file', filename=filename)

        return jsonify({
            'success': True,
            'emotion': emotion,
            'playlist': playlist_data,
            'random_song': random_song,
            'image_url': image_url
        })
    except Exception as e:
        print(f"Error in upload_image: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# --- API 3: Text Mood Detection ---
@app.route('/api/search_mood', methods=['POST'])
def search_mood():
    try:
        data = request.json
        user_text = data.get('mood', '')
        emotion = detect_emotion_from_text(user_text)

        playlist_data, random_song = get_spotify_playlist(emotion)

        return jsonify({
            'success': True,
            'emotion': emotion,
            'playlist': playlist_data,
            'random_song': random_song
        })
    except Exception as e:
        print(f"Error in search_mood: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
