import cv2
import numpy as np


def getRectangleCenter(points):
    # محاسبه مرکز مستطیل
    x_coords = [p[0] for p in points]  # اصلاح
    y_coords = [p[1] for p in points]  # اصلاح
    center_x = sum(x_coords) // len(x_coords)
    center_y = sum(y_coords) // len(y_coords)
    return (center_x, center_y)

def reorder(myPoints):
    try:
        myPoints = myPoints.reshape((4, 2)) # REMOVE EXTRA BRACKET
        myPointsNew = np.zeros((4, 1, 2), np.int32)  # NEW MATRIX WITH ARRANGED POINTS
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]  # [0,0]
        myPointsNew[3] = myPoints[np.argmax(add)]  # [w,h]
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] = myPoints[np.argmin(diff)]  # [w,0]
        myPointsNew[2] = myPoints[np.argmax(diff)]  # [h,0]
        return myPointsNew
    except Exception as e:
        myPoints = myPoints.reshape((len(myPoints), 2))

        # حذف نقاط تکراری یا نزدیک به هم
        unique_points = []
        for p in myPoints:
            if not any(np.allclose(p, up, atol=10) for up in unique_points):
                unique_points.append(p)
        myPoints = np.array(unique_points)

        if len(myPoints) < 4:
            raise ValueError("نقاط کافی برای تعیین مستطیل موجود نیستند.")

        # مرتب‌سازی نقاط بر اساس X
        myPoints = myPoints[myPoints[:, 0].argsort()]

        # تقسیم به نقاط چپ و راست
        left_points = myPoints[:2]
        right_points = myPoints[-2:]

        # مرتب‌سازی نقاط چپ و راست بر اساس Y
        left_points = left_points[left_points[:, 1].argsort()]
        right_points = right_points[right_points[:, 1].argsort()]

        # ترکیب نهایی
        ordered_points = np.array([left_points[0], right_points[0], left_points[1], right_points[1]], dtype=np.float32)
        return ordered_points


def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True) # LENGTH OF CONTOUR
    approx = cv2.approxPolyDP(cont, 0.05 * peri, True) # APPROXIMATE THE POLY TO GET CORNER POINTS
    return approx

def splitBoxes(img):
    height, width = img.shape[:2]
    # Resize the image to make it divisible by 40 rows and 4 columns
    img_resized = cv2.resize(img, (width - (width % 5), height - (height % 10)))
    rows = np.vsplit(img_resized,10)
    boxes=[]
    for r in rows:
        cols= np.hsplit(r,5)
        for c, box in enumerate(cols):
            if c != 0:
                boxes.append(box)

    return boxes

def myCut(img):
    left = 135
    top = 1015
    right = 475
    bottom = 1070

    nextChoice = 74
    choiceLeft = 45
    choiceTop = 3
    choiceRight = 110
    choiceBottom = 48
    # cropped_img = img.crop((left, top, right, bottom))
    for i in range(4):
        # cropped1_img = cropped_img.crop((left, top, right, bottom))
        copyImg = img.copy()
        copyImg=copyImg[left:right , top:bottom]
        right = right + nextChoice
        copyImg.save(f"./{i}.jpg")

def rectContour2(contours, img, justKey=False):
    large_rects = []
    small_rects = []
    c=0
    x_threshold = 50  # Threshold to group contours into columns
    large_area_threshold = 900
    img2=img.copy()
    img1=img.copy()
    # Classify contours based on area and shape (rectangular)
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        # cv2.drawContours(img1, contour, -1, (0, 255, 0), 1)
        # cv2.imwrite('img1.jpg', img1)
        aspect_ratio = float(w) / h
        # cv2.drawContours(img1, contour, -1, (0, 255, 0), 5)
        # cv2.imwrite('img1.jpg', img1)



        if 0.5 <= aspect_ratio <= 0.65 and area >= 200:
            # cv2.drawContours(img2, contour, -1, (0, 0, 255), 1)
            # cv2.imwrite('img2.jpg', img2)
            large_rects.append(contour)
            if len(large_rects) == 16 and justKey == True:
                break

        if 0.7 <= aspect_ratio <= 0.9 and y + h / 4 < img.shape[0] / 4 and 180 <= area <= 750:
                small_rects.append(contour)

    if len(large_rects)!=16:
        raise ValueError(f"Questions were not correctly detected. Only {len(large_rects)} question boxes were detected.")
    if len(small_rects)!=10 and justKey == False :
        raise ValueError(
            f"Student ID position was not detected correctly. Only {len(small_rects)} digits were detected.")

    # Helper functions for sorting
    def get_bounding_x(contour):
        return cv2.boundingRect(contour)[0]

    def get_bounding_y(contour):
        return cv2.boundingRect(contour)[1]

    # Sort large rectangles by horizontal position (x-axis)
    large_rects.sort(key=get_bounding_x)

    # Group rectangles into columns based on the x position
    columns = []
    current_column = []
    last_x = get_bounding_x(large_rects[0]) if large_rects else 0

    for rect in large_rects:
        current_x = get_bounding_x(rect)
        if abs(current_x - last_x) > x_threshold:  # New column
            columns.append(current_column)
            current_column = []
            last_x = current_x
        current_column.append(rect)

    if current_column:  # Add the last column if exists
        columns.append(current_column)

    # Sort each column from top to bottom (y-axis)
    for column in columns:
        column.sort(key=get_bounding_y)

    # Flatten the list of columns into a single sorted list of large rectangles
    large_rects_sorted = [rect for column in columns for rect in column]

    # Sort small rectangles by horizontal position (x-axis)
    if justKey == False:
        small_rects.sort(key=get_bounding_x)

    # Combine sorted large and small rectangles
    # all_rects_sorted = large_rects_sorted + small_rects
    # img1 = img.copy()
    # for i in all_rects_sorted:
    #     cv2.drawContours(img1, [i], -1, (0, 255, 0), 5)

    # cv2.imwrite('img1.jpg', img1)
    # print(len(large_rects_sorted),len(small_rects) )
    return large_rects_sorted, small_rects

