def detect_emotion_from_text(text):
    """
    A simple rule-based function to detect emotion from text.
    For a production-ready system, you would use a pre-trained NLP model.
    """
    text = text.lower()
    
    if any(word in text for word in ['happy', 'joy', 'excited', 'upbeat', 'great', 'good']):
        return 'Happy'
    elif any(word in text for word in ['sad', 'lonely', 'depressed', 'gloomy', 'down', 'blue']):
        return 'Sad'
    elif any(word in text for word in ['angry', 'frustrated', 'annoyed', 'mad', 'furious']):
        return 'Angry'
    elif any(word in text for word in ['calm', 'relax', 'peaceful', 'chilled', 'serene']):
        return 'Relaxed'
    elif any(word in text for word in ['energetic', 'pumped', 'hype', 'active', 'ready']):
        return 'Energetic'
    else:
        return 'Neutral'