import cv2
import numpy as np
from tensorflow.keras.models import load_model

def getCode(images):
    result = ''  # Initialize result as an empty string
    model = load_model('utils/my_model2.keras')
    kernel = np.ones((3, 3), np.uint8)
    for i, image in enumerate(images):
        # Find connected components
        if i != 0:
            image = cv2.dilate(image, kernel, iterations=6)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        x, y, w, h = stats[largest_label, cv2.CC_STAT_LEFT], stats[largest_label, cv2.CC_STAT_TOP], stats[largest_label, cv2.CC_STAT_WIDTH], stats[largest_label, cv2.CC_STAT_HEIGHT]

        # Crop and resize the image
        cropped_image = image[y:y + h, x:x + w]
        img = cv2.resize(cropped_image, (41, 76), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'aa{i}.jpg', img)
        img = img.astype('float32')  # Normalize
        img = np.expand_dims(img, axis=-1)  # Add channel dimension
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        try:
            prediction = model.predict(img, verbose=0)  # Suppress output
            predicted_class = np.argmax(prediction, axis=1)[0]
            result += str(predicted_class)  # Append directly to result string

        except ValueError as e:
            print(f"Prediction error: {str(e)}")

    return result  # Return the final string
