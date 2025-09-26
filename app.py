from flask import Flask, request, jsonify, render_template
import json
import base64
import cv2
import numpy as np
from emotion_model.facial_recognition import detect_emotion_from_frame
from emotion_model.text_classifier import detect_emotion_from_text

# Initialize Flask app
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

# Load mood-to-playlist mappings
try:
    with open('dataset/mood_playlists.json', 'r') as f:
        mood_playlists = json.load(f)
except FileNotFoundError:
    print("Error: mood_playlists.json not found. Please create the file.")
    mood_playlists = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect_emotion', methods=['POST'])
def detect_emotion():
    """API endpoint to detect emotion from a webcam frame."""
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided.'}), 400
            
        image_data = data['image'].split(',')[1] # Get base64 string
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        emotion = detect_emotion_from_frame(frame)
        
        # Get recommended songs based on the detected emotion
        recommended_playlist = mood_playlists.get(emotion, mood_playlists.get('Neutral', {}))
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'playlist': recommended_playlist
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search_mood', methods=['POST'])
def search_mood():
    """API endpoint for text-based mood search."""
    try:
        data = request.json
        user_text = data.get('mood', '')
        
        emotion = detect_emotion_from_text(user_text)
        recommended_playlist = mood_playlists.get(emotion, mood_playlists.get('Neutral', {}))
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'playlist': recommended_playlist
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)