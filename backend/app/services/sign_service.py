import json
import os

import numpy as np

# Gracefully import tensorflow to avoid crash if not installed
try:
    import tensorflow as tf
except ImportError:
    tf = None


class SignService:
    def __init__(self):
        self.model: object | None = None
        self.label_map: dict = {}
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "ml",
            "sign_model",
            "weights",
        )
        self.label_map_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "ml",
            "data",
            "label_map.json",
        )
        self.load_model()
        self.load_label_map()

    def load_model(self):
        if tf is None:
            print("TensorFlow not installed. Sign classification running in mock mode.")
            return

        # Look for saved model weights
        h5_path = os.path.join(self.model_path, "sign_lstm_model.h5")
        if os.path.exists(h5_path):
            try:
                self.model = tf.keras.models.load_model(h5_path)
                print(f"Loaded trained LSTM model from {h5_path}")
            except Exception as e:
                print(f"Failed to load LSTM model from {h5_path}: {e}")
        else:
            print("No pre-trained LSTM weights found. Initializing dummy/mock sign inference.")

    def load_label_map(self):
        if os.path.exists(self.label_map_path):
            try:
                with open(self.label_map_path) as f:
                    self.label_map = json.load(f)
                print("Loaded label map mapping indices to signs.")
            except Exception as e:
                print(f"Failed to load label map: {e}")
        else:
            # Default placeholder labels for MVP testing
            self.label_map = {
                "0": "hello",
                "1": "thank you",
                "2": "sorry",
                "3": "need help",
                "4": "water",
                "5": "yes",
                "6": "no",
                "7": "wait",
                "8": "stop",
                "9": "meeting",
            }

    def predict(self, landmarks_sequence: list) -> tuple[str, float]:
        """
        Classifies a sequence of landmarks (expected shape: 30 frames x feature_dims).
        Returns a tuple of (predicted_sign_label, confidence_score).
        """
        if not landmarks_sequence:
            return "unknown", 0.0

        # Ensure correct length (pad or truncate to 30 frames)
        target_len = 30
        seq_len = len(landmarks_sequence)

        if seq_len < target_len:
            # Pad with zeros
            padding_dims = len(landmarks_sequence[0]) if seq_len > 0 else 126
            padding = [[0.0] * padding_dims] * (target_len - seq_len)
            sequence = landmarks_sequence + padding
        else:
            # Truncate
            sequence = landmarks_sequence[:target_len]

        # Check if we run mock inference
        if self.model is None:
            # Random mock choice from label map for testing client-server flow
            import random

            random.seed(
                sum(landmarks_sequence[0]) if landmarks_sequence and landmarks_sequence[0] else 42
            )
            mock_idx = str(random.randint(0, len(self.label_map) - 1))
            label = self.label_map.get(mock_idx, "hello")
            confidence = float(random.uniform(0.75, 0.98))
            return label, confidence

        try:
            # Prepare input tensor shape (1, 30, feature_dims)
            input_tensor = np.expand_dims(np.array(sequence, dtype=np.float32), axis=0)
            predictions = self.model.predict(input_tensor, verbose=0)[0]
            max_idx = int(np.argmax(predictions))
            confidence = float(predictions[max_idx])
            label = self.label_map.get(str(max_idx), "unknown")
            return label, confidence
        except Exception as e:
            print(f"LSTM prediction error: {e}")
            return "error", 0.0
