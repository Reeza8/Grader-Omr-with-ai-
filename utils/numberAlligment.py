import cv2
import numpy as np

# Load the image
image = cv2.imread('2QC.jpg')

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply threshold to get a binary image (inverse the binary for white background)
_, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

# Use connected components to find the components in the image
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

# We skip the first label (background), and use the first detected component for cropping
if num_labels > 1:  # Ensure at least one component is detected
    x, y, w, h = stats[1, cv2.CC_STAT_LEFT], stats[1, cv2.CC_STAT_TOP], stats[1, cv2.CC_STAT_WIDTH], stats[
        1, cv2.CC_STAT_HEIGHT]

    # Crop the image to the bounding box of the first component
    cropped_image = image[y:y + h, x:x + w]
    print(f"{y}:y + {h}, {x}:x + {w}")
    # Show or save the cropped image
    cv2.imshow('Cropped Image', cropped_image)
    cv2.imwrite('cropped_image.jpg', cropped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No component found!")
