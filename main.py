import cv2
import mediapipe as mp
import pyautogui
import numpy as np

QUIT_KEY = "q"
font = cv2.FONT_HERSHEY_SIMPLEX

screen_w, screen_h = pyautogui.size()

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
# Set face_mesh settings
face_mesh.num_faces = 1

frameWindowTitle = "Facial Monitor Cursor Switching View Frame"
windowWidth = 840

meshPointsFaceOutline = [
    10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109
]

meshPointsCenterPointIndex = 1

# Coloring Decisions
SCALAR_COLOR_RED           = (0, 0, 255)
SCALAR_COLOR_LIGHTER_BLUE  = (255, 100, 0)
SCALAR_COLOR_GREEN         = (0, 255, 0)
SCALAR_COLOR_YELLOW        = (0, 255, 255)
SCALAR_COLOR_ORANGE        = (0, 165, 255)
SCALAR_COLOR_PURPLE        = (128, 0, 128)
SCALAR_COLOR_PURPLE_BRIGHT = (255, 0, 255)

color_faceOutline = SCALAR_COLOR_GREEN
color_pupilLeft   = SCALAR_COLOR_PURPLE_BRIGHT
color_pupilRight  = color_pupilLeft
color_centerPoint = SCALAR_COLOR_GREEN
color_allPoints   = SCALAR_COLOR_LIGHTER_BLUE
color_leftIris    = SCALAR_COLOR_GREEN
color_RightIris   = color_leftIris

# Decoration Decisions
size_faceOutlineLine  = 1
size_primaries        = 3
size_borderPrimaries  = 1
size_borderPupilBasic = -1 #TODO: Make able to take percentages and caculate to cover entire pupil depeding on eye height
size_allPoints        = 1
size_borderAllPoints  = -1

# SKIP OPTIONS
frame_blank = True

show_allPoints   = True
show_faceOutline = False
show_pupils      = True


paused = False
mainMonitorMousePos = pyautogui.position()
secondaryMonitorMousePos = pyautogui.position()
inMainMonitor = True

leftDividerSectionATop = (0, 0)
leftDividerSectionABottom = (0, 0)
rightDividerSectionATop = (0, 0)
rightDividerSectionABottom = (0, 0)

cutoff = 269  #Default value (works with my primary setup)
cutoffPercentage = int(cutoff/478*100)

# BUTTON PRESS FUNCTIONS
def nothing(x):
    pass
def setPercentageOfPoints(percentageOf100):
    global cutoff
    global cutoffPercentage
    cutoffPercentage = percentageOf100
    cutoff = int(percentageOf100 / 100 * 478)

while True:
    if not paused:
        _, frame = cam.read()

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        frame_h, frame_w, _ = frame.shape
        if frame_blank:
            frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
        # "Secondary Monitor Left %"
        cv2.createTrackbar("Left:", frameWindowTitle, cutoffPercentage, 100, setPercentageOfPoints)

        leftCount = -1  #as always has +1
        rightCount = 0

        if landmark_points:
            landmarks = landmark_points[0].landmark
            centerPoint = landmarks[meshPointsCenterPointIndex]

            xAvgTop = int((landmarks[93].x + landmarks[127].x)/2 * frame_w)
            yAvgTop = int((landmarks[93].y + landmarks[127].y)/2 * frame_h)
            xAvgBottom = int((landmarks[93].x + landmarks[58].x)/2 * frame_w)
            yAvgBottom = int((landmarks[93].y + landmarks[58].y)/2 * frame_h)
            leftDividerSectionATop = (xAvgTop + (xAvgTop - xAvgBottom), yAvgTop + (yAvgTop - yAvgBottom))
            leftDividerSectionABottom = (xAvgBottom - (xAvgTop - xAvgBottom), yAvgBottom - (yAvgTop - yAvgBottom))

            xAvgTop = int((landmarks[323].x + landmarks[356].x)/2 * frame_w)
            yAvgTop = int((landmarks[323].y + landmarks[356].y)/2 * frame_h)
            xAvgBottom = int((landmarks[323].x + landmarks[288].x)/2 * frame_w)
            yAvgBottom = int((landmarks[323].y + landmarks[288].y)/2 * frame_h)
            # rightDividerSectionATop = (xAvgTop + (xAvgTop - xAvgBottom), yAvgTop + (yAvgTop - yAvgBottom))
            # rightDividerSectionABottom = (xAvgBottom - (xAvgTop - xAvgBottom), yAvgBottom - (yAvgTop - yAvgBottom))
            rightDividerSectionATop = (xAvgTop + (xAvgTop - xAvgBottom), yAvgTop + (yAvgTop - yAvgBottom))
            rightDividerSectionABottom = (xAvgBottom - (xAvgTop - xAvgBottom), yAvgBottom - (yAvgTop - yAvgBottom))

            cv2.line(frame, leftDividerSectionATop, leftDividerSectionABottom, SCALAR_COLOR_ORANGE, 2)
            cv2.line(frame, rightDividerSectionATop, rightDividerSectionABottom, SCALAR_COLOR_ORANGE, 2)

            # cv2.circle(frame, (xAvgTop, yAvgTop), 4, SCALAR_COLOR_YELLOW, -1)
            # cv2.circle(frame, (xAvgBottom, yAvgBottom), 4, SCALAR_COLOR_GREEN, -1)
            # for id, landmark in enumerate(landmarks[0:478]):
            #     cv2.circle(frame, (int(landmark.x * frame_w), int(landmark.y * frame_h)), 4, SCALAR_COLOR_RED, -1)

            # ALL POINTS
            for id, landmark in enumerate(landmarks):
            # for id, landmark in enumerate(landmarks[474:480]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                if x < centerPoint.x * frame_w:
                    leftCount = leftCount + 1
                    color = SCALAR_COLOR_RED  #TODO: Make more efficent when not selected
                else:
                    rightCount = rightCount + 1
                    color = SCALAR_COLOR_LIGHTER_BLUE
                if show_allPoints:
                    cv2.circle(frame, (x, y), size_allPoints, color, size_borderAllPoints)

            # Show counter values
            cv2.putText(frame, " LEFT: "+str(int(leftCount/478*100))+"%", (40, 50), font, 1, SCALAR_COLOR_RED, 2, cv2.LINE_AA)
            cv2.putText(frame, "RIGHT: "+str(int(rightCount/478*100))+"%", (40, 100), font, 1, SCALAR_COLOR_LIGHTER_BLUE, 2, cv2.LINE_AA)
            cv2.putText(frame, "Cursr: "+str(pyautogui.position()), (40, 150), font, 1, SCALAR_COLOR_ORANGE, 2, cv2.LINE_AA)

            if leftCount < cutoff and inMainMonitor:
                inMainMonitor = False
                mainMonitorMousePos = pyautogui.position()
                pyautogui.moveTo(secondaryMonitorMousePos)
            elif leftCount > cutoff and not inMainMonitor:
                inMainMonitor = True
                secondaryMonitorMousePos = pyautogui.position()
                pyautogui.moveTo(mainMonitorMousePos)
            # else # cutoff line does not trigger change, stays as it was

            if inMainMonitor:
                cv2.rectangle(frame, (40, 180), (90, 230), SCALAR_COLOR_LIGHTER_BLUE, -1)
            else:
                cv2.rectangle(frame, (40, 180), (90, 230), SCALAR_COLOR_RED, -1)

            # Iris's
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), size_primaries, color_RightIris, size_borderPrimaries)
                if id == 1:
                    screen_x = screen_w * landmark.x
                    screen_y = screen_h * landmark.y
                    # pyautogui.moveTo(screen_x, screen_y)
            left = [landmarks[145], landmarks[159]]
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), size_primaries, color_leftIris, size_borderPrimaries)
            if (left[0].y - left[1].y) < 0.004:
                print("Blinked!")
                show_faceOutline = show_allPoints
                show_allPoints = not show_allPoints
            # Pupils
            if show_pupils:
                lPupil = 468
                rPupil = 473
                cv2.circle(frame, (int(landmarks[lPupil].x * frame_w), int(landmarks[lPupil].y * frame_h)), size_primaries, color_pupilLeft, size_borderPupilBasic)
                cv2.circle(frame, (int(landmarks[rPupil].x * frame_w), int(landmarks[rPupil].y * frame_h)), size_primaries, color_pupilRight, size_borderPupilBasic)
            # Center point
            if centerPoint:
                cv2.circle(frame, (int(centerPoint.x * frame_w), int(centerPoint.y * frame_h)), size_primaries, color_centerPoint, size_borderPrimaries)

            # Outer face outline
            if show_faceOutline:
                nextPoint = (int(landmarks[meshPointsFaceOutline[0]].x * frame_w), int(landmarks[meshPointsFaceOutline[0]].y * frame_h))
                originalPoint = nextPoint

                for i in range(len(meshPointsFaceOutline) - 1):
                    # Access the element at the current index
                    oldPoint = nextPoint
                    nextPoint = (int(landmarks[meshPointsFaceOutline[i + 1]].x * frame_w),
                                 int(landmarks[meshPointsFaceOutline[i + 1]].y * frame_h))
                    cv2.line(frame, oldPoint, nextPoint, color_faceOutline, 1)
                # Connect back to front
                cv2.line(frame, originalPoint, nextPoint, color_faceOutline, 1)


        # Create a named window with the specified width
        cv2.namedWindow(frameWindowTitle, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(frameWindowTitle, windowWidth, int(windowWidth/frame.shape[1] * frame.shape[0]))

        cv2.imshow(frameWindowTitle, frame)

    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break
    # elif k != ord("ÿ"):  # Any key
    elif k == 32:  # (Spacebar key)
        paused = not paused
    elif k == 115:  # (S KEY)
        frame_blank = not frame_blank
        print("Toggling show rgb to "+str(frame_blank))
    elif k == 13:  # (ENTER KEY) ord(RESET_KEY):
        print("Enter key")
    elif k == 127:  # Backspace
        print("Backspace")
    elif k == ord(QUIT_KEY):
        break
