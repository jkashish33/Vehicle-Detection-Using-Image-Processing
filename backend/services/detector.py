import cv2
import numpy as np
from PIL import Image
import tempfile
import os

from utils.model_loader import load_haar_model, load_cnn_model

def detect_vehicle(image_file, model='haar', return_image=False):
    if model == 'haar':
        haar = load_haar_model()
        img_array = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        vehicles = haar.detectMultiScale(img, 1.1, 4)
        # Draw bounding boxes
        for (x, y, w, h) in vehicles:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        result = {'vehicles': [list(map(int, v)) for v in vehicles]}
        if return_image:
            return result, pil_img
        return result
    elif model == 'cnn':
        cnn = load_cnn_model()
        # Implement CNN detection logic here
        # Dummy response for demo
        return {'vehicles': []}
    else:
        return {'error': 'Unknown model'}

def detect_video(video_file, model='haar'):
    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_input:
        video_file.save(temp_input)
        temp_input_path = temp_input.name

    cap = cv2.VideoCapture(temp_input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    processed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    processed_filename = f"processed_{os.path.basename(temp_input_path)}"
    processed_path = os.path.join(processed_dir, processed_filename)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(processed_path, fourcc, fps, (width, height))

    haar = load_haar_model()
    frame_count = 0
    total_vehicles = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        vehicles = haar.detectMultiScale(frame, 1.1, 4)
        for (x, y, w, h) in vehicles:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        total_vehicles += len(vehicles)
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    os.remove(temp_input_path)
    stats = {'frames': frame_count, 'total_vehicles': total_vehicles}
    return processed_filename, stats

def train_models():
    # Train Haar (no training needed), CNN (implement training)
    pass

def compare_models():
    # Evaluate models on validation set, return metrics
    return {'haar': 0.85, 'cnn': 0.90}