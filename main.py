import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput.mouse import Listener as MouseListener
import pynput.mouse
import threading
import time

KEY_QUIT                       = 'q'
KEY_TOGGLE_PAUSE               = ' '
KEY_AUTO_SET_SECOND            = '2'
KEY_MANUAL_BLINK_TRIGGER       = 'b'
KEY_BLANK_BACKGROUND_SWITCH    = 's'
KEY_ALLOW_SWITCH_ON_MOUSE_DRAG = 'd'

# Stored to avoid recalculating every frame
KEY_ORD_KEY_QUIT                   = ord(KEY_QUIT)
KEY_ORD_TOGGLE_PAUSE               = ord(KEY_TOGGLE_PAUSE)
KEY_ORD_AUTO_SET_SECOND            = ord(KEY_AUTO_SET_SECOND)
KEY_ORD_MANUAL_BLINK_TRIGGER       = ord(KEY_MANUAL_BLINK_TRIGGER)
KEY_ORD_BLANK_BACKGROUND_SWITCH    = ord(KEY_BLANK_BACKGROUND_SWITCH)
KEY_ORD_ALLOW_SWITCH_ON_MOUSE_DRAG = ord(KEY_ALLOW_SWITCH_ON_MOUSE_DRAG)

font = cv2.FONT_HERSHEY_SIMPLEX

screen_w, screen_h = pyautogui.size()

videoCaptureDeviceId = 0
cam = cv2.VideoCapture(videoCaptureDeviceId)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
# Set face_mesh settings
face_mesh.num_faces = 1

frameWindowTitle = "Facial Monitor Cursor Switching View Frame"
windowWidth = 840

meshPointsFaceOutline = [ #Ordered clockwise
     10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172,  58, 132,  93, 234, 127, 162,  21,  54, 103,  67, 109
]

meshPointsFaceCenterLine = [ #Ordered top to bottom
     10, 151,   9,   8, 168,   6, 197, 195,   5,   4,   1,  19,
     94,   2, 164,   0,  11,  12,  13,  14,  15,  16,  17,  18,
    200, 199, 175, 152
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
SCALAR_COLOR_GRAY          = (100,100,100)

color_data_NA                 = SCALAR_COLOR_GRAY
color_calculatedSeperatorLine = SCALAR_COLOR_ORANGE

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

# OPTIONS
frame_blank = True
allow_switch_when_dragging = False
paused = False

show_allPoints   = True
show_faceOutline = False
show_pupils      = True

savedMonitorMousePositions = [pyautogui.position(), pyautogui.position()]
inMainMonitor = True
mouseButtonTracker = [ False, False, False ]
lastLeftMouseLocationBeforeDrag = pyautogui.position()
lastLeftMouseMonitorBeforeDrag = 0  #Assume starting in primary monitor, TODO: Move to area where get_monitor... is defined


leftDividerSectionATop = (0, 0)
leftDividerSectionABottom = (0, 0)
rightDividerSectionATop = (0, 0)
rightDividerSectionABottom = (0, 0)

cutoff = 215  #Default values (works with my primary setup) 269 = tip of nose version, 215 for insideFaceCenter
cutoffPercentage = int(cutoff/478*100)

helperStep = 0

# BUTTON PRESS FUNCTIONS

def set_percentage_of_points(percentageOf100):
    global cutoff
    global cutoffPercentage
    cutoffPercentage = percentageOf100
    cutoff = int(percentageOf100 / 100 * 478)

# SETUP HELPER
#  Setup helper tutorial
# def helperMessager():
    #cv2.putText(frame, " LEFT: " + str(int(leftCount / 478 * 100)) + "%", (40, 50), font, 1, SCALAR_COLOR_RED, 2, cv2.LINE_AA)


def on_second_monitor_scale_triggerd(percentage): # Make change between 50% and second monitor. Percentage should be between 0 & 1, recomended is 0.5
    global cutoff
    global cutoffPercentage
    global leftCount
    cutoff = (leftCount - 478/2)/2+(478*percentage)
    cutoffPercentage = int(cutoff/478*100)

# TRIGGERS
def on_blink():
    global show_faceOutline
    global show_allPoints

    print("Blinked!")
    show_faceOutline = show_allPoints
    show_allPoints = not show_allPoints

def on_move(x, y):
    pass

def on_click(x, y, mouseButton, pressed):
    global lastLeftMouseMonitorBeforeDrag  # Remove and just check off of mouse coordinates?
    global lastLeftMouseLocationBeforeDrag

    mouseButton = str(mouseButton)
    # print(f"Mouse button {mouseButton} clicked at ({x}, {y})")
    if pressed:
        if mouseButton == "Button.left":
            mouseButtonTracker[0] = True
            lastLeftMouseLocationBeforeDrag = (x, y)
            lastLeftMouseMonitorBeforeDrag = get_mouse_located_in_monitor_num()
        elif mouseButton == "Button.right":
            mouseButtonTracker[1] = True
        elif mouseButton == "Button.middle":
            mouseButtonTracker[2] = True
    else:
        if mouseButton == "Button.left":
            mouseButtonTracker[0] = False
            # lastLeftMouseLocationBeforeDrag = (None, None)
        elif mouseButton == "Button.right":
            mouseButtonTracker[1] = False
        elif mouseButton == "Button.middle":
            mouseButtonTracker[2] = False

# At present, this function is never called for some reason, using only on_click() workaround
def on_release(x, y, mouseButton):
    mouseButton = str(mouseButton)
    print(f"Mouse button {mouseButton} released at ({x}, {y})")
    if mouseButton == "Button.left":
        mouseButtonTracker[0] = False
    elif mouseButton == "Button.right":
        mouseButtonTracker[1] = False
    elif mouseButton == "Button.middle":
        mouseButtonTracker[2] = False

# Start the mouse tracking in another thread so that it can run at the same time
mouseListener = MouseListener(on_click=on_click, on_release=on_release, on_move=on_move)
mouseThread = threading.Thread(target=mouseListener.start)
mouseThread.start()


# At present, crashes entire program if used
# def get_if_any_mouse_buttons_held():
#     mouse_info = pyautogui.mouseInfo()
#     return (False if mouse_info["left"] is None else True) or (False if mouse_info["right"] is None else True) or (False if mouse_info["middle"] is None else True)

def get_if_any_mouse_buttons_held():
    return mouseButtonTracker[0] or mouseButtonTracker[1] or mouseButtonTracker[2]

def get_if_in_main_monitor():
    mouseX, mouseY = pyautogui.position()
    return pyautogui.onScreen(mouseX, mouseY)  #pyautogui only supports 1 monitor so as even though the position is valid on a diffrent screen, pyautogui does not count it

# Currently only works with 2 monitors as pyautogui only supports main monitor
def get_mouse_located_in_monitor_num():  #Index starts at 0 (main monitor)
    if get_if_in_main_monitor():
        return 0
    else:
        return 1

def monitor_move_cutoff_with_check():
    global inMainMonitor
    wasChanged = True
    if leftCount < cutoff and inMainMonitor:
        inMainMonitor = False
        savedMonitorMousePositions[0] = pyautogui.position()
        pyautogui.moveTo(savedMonitorMousePositions[1])
    elif leftCount > cutoff and not inMainMonitor:
        inMainMonitor = True
        savedMonitorMousePositions[1] = pyautogui.position()
        pyautogui.moveTo(savedMonitorMousePositions[0])
    else:
        wasChanged = False
    return wasChanged


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

        # GRAPHICAL UI OPTIONS
        # "Secondary Monitor Left %"
        cv2.createTrackbar("Left:", frameWindowTitle, cutoffPercentage, 100, set_percentage_of_points)

        # Always on text
        cv2.putText(frame, "Press the '" + KEY_AUTO_SET_SECOND + "' key while looking at your second monitor", (15, 650), font, 1, SCALAR_COLOR_GREEN, 1, cv2.LINE_AA)
        # cv2.putText(frame, "to auto-set second monitor location" + ("" if landmark_points else " (face needs to be detected)"), (15, 700), font, 1, SCALAR_COLOR_GREEN, 1, cv2.LINE_AA)
        cv2.putText(frame, f"to auto-set second monitor location{'' if landmark_points else ' (face needs to be detected)'}",(15, 700), font, 1, SCALAR_COLOR_GREEN, 1, cv2.LINE_AA)

        # Show counter values
        cv2.putText(frame, " LEFT: ", (40, 50), font, 1, SCALAR_COLOR_RED, 2, cv2.LINE_AA)
        cv2.putText(frame, "RIGHT: ", (40, 100), font, 1, SCALAR_COLOR_LIGHTER_BLUE, 2, cv2.LINE_AA)
        cv2.putText(frame, "Cursr: ", (40, 150), font, 1, SCALAR_COLOR_ORANGE, 2, cv2.LINE_AA)


        # setupHelperTutorial();

        leftCount = -1  #as always has +1
        rightCount = 0

        boxDisplayColorHolder = color_data_NA

        if landmark_points:
            landmarks = landmark_points[0].landmark
            centerPoint = (landmarks[meshPointsCenterPointIndex].x, landmarks[meshPointsCenterPointIndex].y)

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

            cv2.line(frame, leftDividerSectionATop, leftDividerSectionABottom, color_calculatedSeperatorLine, 2)
            cv2.line(frame, rightDividerSectionATop, rightDividerSectionABottom, color_calculatedSeperatorLine, 2)

            nextPoint = (int(landmarks[meshPointsFaceCenterLine[0]].x * frame_w), int(landmarks[meshPointsFaceCenterLine[0]].y * frame_h))
            originalPoint = nextPoint

            for i in range(len(meshPointsFaceCenterLine) - 1):
                # Access the element at the current index
                oldPoint = nextPoint
                nextPoint = (int(landmarks[meshPointsFaceCenterLine[i + 1]].x * frame_w),
                             int(landmarks[meshPointsFaceCenterLine[i + 1]].y * frame_h))
                cv2.line(frame, oldPoint, nextPoint, color_calculatedSeperatorLine, 2)
            # Connect back to front
            cv2.line(frame, originalPoint, nextPoint, SCALAR_COLOR_GREEN, 1)

            # Center-point between top and bottom
            centerInsideFaceX = int(originalPoint[0] + (nextPoint[0] - originalPoint[0]) / 2)
            centerInsideFaceY = int(originalPoint[1] + (nextPoint[1] - originalPoint[1]) / 2)

            centerPoint = (centerInsideFaceX, centerInsideFaceY) #Overrride landmark tip of nose
            # centerPoint = (int(landmarks[meshPointsCenterPointIndex].x * frame_w), int(landmarks[meshPointsCenterPointIndex].y * frame_h))
            cv2.circle(frame, centerPoint, size_primaries, SCALAR_COLOR_PURPLE_BRIGHT, 6)



            # ALL POINTS
            for id, landmark in enumerate(landmarks):
            # for id, landmark in enumerate(landmarks[474:480]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                if x < centerPoint[0]:
                    leftCount = leftCount + 1
                    color = SCALAR_COLOR_RED  #TODO: Make more efficient when not selected
                else:
                    rightCount = rightCount + 1
                    color = SCALAR_COLOR_LIGHTER_BLUE
                if show_allPoints:
                    cv2.circle(frame, (x, y), size_allPoints, color, size_borderAllPoints)

            # Show counter values
            cv2.putText(frame, str(int(leftCount/478*100))+"%", (150, 50), font, 1, SCALAR_COLOR_RED, 2, cv2.LINE_AA)  # left
            cv2.putText(frame, str(int(rightCount/478*100))+"%", (150, 100), font, 1, SCALAR_COLOR_LIGHTER_BLUE, 2, cv2.LINE_AA) # right
            cv2.putText(frame, str(pyautogui.position()), (150, 150), font, 1, SCALAR_COLOR_ORANGE, 2, cv2.LINE_AA) # cursor

            # if allow_switch_when_dragging or (not get_if_any_mouse_buttons_held()):
            if allow_switch_when_dragging:  #Ignoreing dragging
                monitor_move_cutoff_with_check()
            elif not get_if_any_mouse_buttons_held():  #Not ignoring dragging and not held
                # if lastLeftMouseLocationBeforeDrag[0] is None:  #For after dragging, see if in a new monitor
                if lastLeftMouseMonitorBeforeDrag is get_mouse_located_in_monitor_num():  #Same monitor
                    monitor_move_cutoff_with_check()
                else:  #Diffrent Monitor
                    tempCurrentPosStore = pyautogui.position()
                    if(monitor_move_cutoff_with_check()): #If monitor changed
                        savedMonitorMousePositions[lastLeftMouseMonitorBeforeDrag] = lastLeftMouseLocationBeforeDrag  #Make saved position of the previous monitor the location before the drag
                        savedMonitorMousePositions[get_mouse_located_in_monitor_num()] = pyautogui.position()
                        pyautogui.moveTo(tempCurrentPosStore)
                    lastLeftMouseMonitorBeforeDrag = get_mouse_located_in_monitor_num()  # Reset so it is not called again



            # else # cutoff line does not trigger change, stays as it was

            if inMainMonitor:
                boxDisplayColorHolder = SCALAR_COLOR_RED
            else:
                boxDisplayColorHolder = SCALAR_COLOR_LIGHTER_BLUE

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
            if (left[0].y - left[1].y) < 0.008:
                on_blink()
            # Pupils
            if show_pupils:
                lPupil = 468
                rPupil = 473
                cv2.circle(frame, (int(landmarks[lPupil].x * frame_w), int(landmarks[lPupil].y * frame_h)), size_primaries, color_pupilLeft, size_borderPupilBasic)
                cv2.circle(frame, (int(landmarks[rPupil].x * frame_w), int(landmarks[rPupil].y * frame_h)), size_primaries, color_pupilRight, size_borderPupilBasic)
            # Center point
            if centerPoint:
                cv2.circle(frame, (int(centerPoint[0] * frame_w), int(centerPoint[1] * frame_h)), size_primaries, color_centerPoint, size_borderPrimaries)

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


        # CONTINUE ALWAYS SHOW UI ELEMENTS
        cv2.rectangle(frame, (55, 180), (105, 230), boxDisplayColorHolder, -1) # Should be gray by default


        # Create a named window with the specified width
        cv2.namedWindow(frameWindowTitle, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(frameWindowTitle, windowWidth, int(windowWidth/frame.shape[1] * frame.shape[0]))

        cv2.imshow(frameWindowTitle, frame)

    k = cv2.waitKey(1) & 0xff
    if k == 27:  # (Escape key)
        break
    elif k == KEY_ORD_TOGGLE_PAUSE:  # (Pause toggle w/ cam shutoff)
        if(paused):  # If already paused, take control of the capture again
            print("Restarting camera stream")
            cam = cv2.VideoCapture(videoCaptureDeviceId)
        else:        # If needs to pause
            print("Stopping camera stream")
            cam = 0  # Destroys object, stops taking up stream
        paused = not paused
    elif k == KEY_ORD_BLANK_BACKGROUND_SWITCH:  # (Switch blank background display)
        frame_blank = not frame_blank
        print("Toggling show rgb to "+str(frame_blank))
    elif k == KEY_ORD_MANUAL_BLINK_TRIGGER:  # (Manually trigger blink)
        print("Manual blink command")
        on_blink()
    elif k == KEY_ORD_AUTO_SET_SECOND:  # (2nd monitor auto)
        print("Automatic setting of right side second monitor")
        on_second_monitor_scale_triggerd(0.5)
    elif k == KEY_ORD_ALLOW_SWITCH_ON_MOUSE_DRAG:
        print("Toggling allow switch when dragging to "+str(allow_switch_when_dragging))
        allow_switch_when_dragging = not allow_switch_when_dragging
    elif k == 13:  # (ENTER KEY) ord(RESET_KEY):
        print("Enter key")
    elif k == 127:  # Backspace
        print("Backspace")
    elif k == KEY_ORD_KEY_QUIT:
        break
    elif k == ord("u"):
        print(":get_mouse_located_in_monitor_num:"+str(get_mouse_located_in_monitor_num())+":")
        # test = pyautogui.prompt('This lets the user type in a string and press OK.')

    elif k != ord("ÿ"):  # Any key
        print("The key you pressed had an number of \""+str(k)+"\"")
