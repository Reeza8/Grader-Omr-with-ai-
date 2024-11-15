import cv2
import numpy as np
from utils.common import *
from utils.extractCode import *

heightImg, widthImg = 1500, 1000

def getScore(answerBoxes,img):
    temp = 0
    questions, choices = 10, 4
    answers = [4, 3, 2, 1, 1, 3, 2, 1, 2, 3, 1, 4, 1, 2, 1, 3, 2, 3, 3, 4]
    emptyChoiceThreshold = 4000
    correct_count = 0
    incorrect_count = 0
    userAnswers = []
    for i in range(16):
        # Get and reorder corner points for perspective transformation
        biggestPoints = reorder(getCornerPoints(answerBoxes[i]))

        # نمایش نقاط گوشه‌ای روی تصویر برای دیباگ
        # Apply perspective transformation
        pts1 = np.float32(biggestPoints)
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
        # cv2.imwrite(f"imgWarpColored{i}.jpg", img)
        # Convert to grayscale and apply adaptive threshold
        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgThresh = cv2.adaptiveThreshold(imgWarpGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 101, 5)

        # Black out the border regions
        margin = 20
        imgThresh[:margin, :] = 0
        imgThresh[-margin:, :] = 0
        imgThresh[:, :margin] = 0
        imgThresh[:, -margin:] = 0

        # Split the thresholded image into individual boxes
        boxes = splitBoxes(imgThresh)

        # Count non-zero pixels in each box
        myPixelVal = np.array([cv2.countNonZero(box) for box in boxes]).reshape(questions, choices)

        # Determine user answers based on the maximum pixel count in each row
        max_indices = np.argmax(myPixelVal, axis=1) + 1  # Indices of the max pixel counts (1-based)
        myIndex = np.where(np.max(myPixelVal, axis=1) < emptyChoiceThreshold, -1, max_indices)

        # Store the answers
        userAnswers.extend(myIndex.tolist())

        # Compare user answers with the correct answers
        for i in range(questions):
            if temp == len(answers):
                break
            if myIndex[i] == answers[temp]:
                correct_count += 1  # Increment correct count if the answer is correct
            elif myIndex[i] != -1:
                incorrect_count += 1  # Increment incorrect count if the answer is wrong
            temp += 1

    # Calculate the final score
    net_correct = 3 * correct_count - incorrect_count
    score = (net_correct / float(3 * questions)) * 100
    return score, correct_count, incorrect_count

def getCodeBox(codeBoxes,img):
    codes=[]
    high_res_size = (200, 400)
    for i in range(10):
        # Get and reorder corner points for perspective transformation
        biggestPoints = reorder(getCornerPoints(codeBoxes[i]))


        pts1 = np.float32(biggestPoints)
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        # Convert to grayscale and apply adaptive threshold
        # imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        # imgThresh = cv2.adaptiveThreshold(imgWarpGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 101, 5)

        imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
        imgThresh = cv2.adaptiveThreshold(cv2.resize(imgWarpGray, high_res_size), 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                 cv2.THRESH_BINARY_INV, 51, 5)
        # Black out the border regions
        margin = 35
        imgThresh[:margin, :] = 0
        imgThresh[-margin:, :] = 0
        imgThresh[:, :margin] = 0
        imgThresh[:, -margin:] = 0
        codes.append(imgThresh)
    stringCodes=getCode(codes)
    return stringCodes

def scan(byteImage):
    np_arr = np.frombuffer(byteImage, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    img=img[650:, :]
    img = cv2.resize(img, (widthImg, heightImg)) # Resize the image
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    imgGray = cv2.GaussianBlur(imgGray, (3, 3), 2)  # Apply Gaussian blur
    imgCanny = cv2.Canny(imgGray, 10, 30)  # Apply Canny edge detection
    # Find and draw contours
    contours, _ = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(img1, contours, -1, (0, 255, 0), 5)
    # cv2.imwrite("imgaaaaaaa.jpg",img1)
    # Filter for rectangular contours
    try:
        answerBoxes, codeBoxes = rectContour2(contours, img)
    except Exception as e:
        print(f"Error finding rectangular contours: {e}")

    codes = getCodeBox(codeBoxes,img)
    score, correct_count, incorrect_count=getScore(answerBoxes,img)

    print("Correct Answers:", correct_count)
    print("Incorrect Answers:", incorrect_count)
    print("FINAL SCORE:", score)
    print("code code:", codes)
    return score,codes

