import cv2
import numpy as np
from deepface import DeepFace

def detect_emotion_from_frame(frame):
    """Detects emotion from a single video frame using DeepFace."""
    try:
        # DeepFace.analyze() handles face detection and emotion classification
        demographies = DeepFace.analyze(
            img_path=frame,
            actions=['emotion'],
            enforce_detection=False  # Set to False to prevent raising an error if no face is detected
        )
        
        if not demographies:
            return "Neutral"

        # DeepFace returns a list of dictionaries, one for each detected face.
        # We'll just take the dominant emotion from the first detected face.
        dominant_emotion = demographies[0]['dominant_emotion']
        
        # DeepFace's emotions are: 'angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'
        
        # We'll map them to our desired categories
        if dominant_emotion in ['happy']:
            return 'Happy'
        elif dominant_emotion in ['sad', 'disgust', 'fear']:
            return 'Sad'
        elif dominant_emotion in ['angry']:
            return 'Angry'
        elif dominant_emotion in ['surprise']:
            return 'Energetic'
        elif dominant_emotion in ['neutral']:
            return 'Neutral'
        else: # Fallback for unexpected emotion
            return 'Neutral'
            
    except Exception as e:
        print(f"An error occurred in DeepFace analysis: {e}")
        return "Neutral"