import io
import json
from typing import List

import numpy as np
from PIL import Image
import face_recognition


def load_image_from_file_storage(file_storage) -> np.ndarray:
    """Convert Werkzeug FileStorage to an RGB numpy array."""
    image_stream = io.BytesIO(file_storage.read())
    image = Image.open(image_stream).convert("RGB")
    return np.array(image)


def load_image_from_base64(data_url: str) -> np.ndarray:
    """Convert a data URL (base64) image from browser to RGB numpy array."""
    import base64

    header, b64data = data_url.split(",", 1)
    image_bytes = base64.b64decode(b64data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)


def get_face_encodings(image_array: np.ndarray) -> List[np.ndarray]:
    """Return list of face encodings from an RGB numpy image array."""
    locations = face_recognition.face_locations(image_array)
    if not locations:
        return []
    encodings = face_recognition.face_encodings(image_array, locations)
    return encodings


def encode_to_json(encoding: np.ndarray) -> str:
    """Serialize a single 128-d embedding to JSON string."""
    return json.dumps(encoding.tolist())


def decode_from_json(encoding_str: str) -> np.ndarray:
    """Deserialize JSON string back to numpy array."""
    return np.array(json.loads(encoding_str), dtype="float32")


def check_face_exists(new_encoding: np.ndarray, existing_encodings: List[np.ndarray], tolerance: float = 0.6) -> bool:
    """Check if a face encoding already exists in the database."""
    if not existing_encodings:
        return False
    matches = face_recognition.compare_faces(existing_encodings, new_encoding, tolerance=tolerance)
    return any(matches)
