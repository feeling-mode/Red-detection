# -*- coding: utf-8 -*-
"""
Spyder Editor
---------- MWR - LAB01 - s17186 --------------------
This script is for tracking objects of specified color
in the video file provided as a path
                        as input argument.

"""
import math
import argparse
import cv2
import numpy as np

def play(video):
    '''
    takes video file path
        opens 3 windows:
            slider - to adjust HSV chanel split values
            transform - to display binary transformation of a video frame
            main - video display with tracked objects marked
        * user can adjust transform params in real time while video played
        * user can pause a video with 'space'key
            * when paused, press 'space' key' again to refresh the transform img
            * press 'q' to close the program
            * press any other key to continue video play
        * pressing 'q' breaks the video loop and closes the program
          otherwise video loops indefinitely
    waits for user to close the window(s) or error to terminate the program
    '''
    frame_counter = 0
    pause_time = 15
    print("\t starting video")
    print("\t # press 'space' to pause \n\t # press 'q' to exit")
    show_slider()
    while video.isOpened():
        frame_grabbed, frame = video.read()
        if frame_grabbed:
            show_transform_window(frame)
            show_main_window(frame)
            frame_counter += 1
            key = cv2.waitKey(pause_time)
            print_pause_info = True
            while pause(key):
                print("\t\t *** paused for ", pause_time, " sec ***   ")
                if print_pause_info:
                    print("\t\t"+
                          "# you can adjust params in 'Control' window \n\t\t" +
                          "# press 'space' again to refresh the " +
                          "transform window and adjust pause time \n\t\t" +
                          "# press 'q' to exit \n\t\t" +
                          "# press any other key to continue the video")
                    print_pause_info = False
                show_transform_window(frame)
                key = cv2.waitKey(pause_time*1000) #15sec
                if close(key):
                    break
                if not pause(key):
                    print("\t # press 'space' to pause \n\t\t 'q' to exit")
            if close(key):
                print ("\t closing...")
                break
            if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
                frame_counter = 0
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            print ("\t no frame grabbed... breaking")
            break
    video.release()
    cv2.destroyAllWindows()

def show_slider():
    '''
    displays slider - requires create_trackbar method
    '''
    cv2.namedWindow("Control")
    create_trackbar()
    set_slider_values()

def create_trackbar():
    '''
    creates trackbar with OpenCV for HSV chanels
    '''
    cv2.createTrackbar("1. HighHue", "Control", 0, 180, do_nothing)
    cv2.createTrackbar("2. LowHue", "Control", 180, 180, do_nothing)
    cv2.createTrackbar("3. HighSat", "Control", 0, 255, do_nothing)
    cv2.createTrackbar("4. LowSat", "Control", 255, 255, do_nothing)
    cv2.createTrackbar("5. HighVal", "Control", 0, 255, do_nothing)
    cv2.createTrackbar("6. LowVal", "Control", 255, 255, do_nothing)
    cv2.createTrackbar("7. Trnsfrm", "Control", 1, 20, do_nothing)
    cv2.createTrackbar("8. RESET", "Control", 0, 2, set_slider_values)

def set_slider_values(_=1):
    '''
    sets slider values - HSV model chanels
    '''
    cv2.setTrackbarPos("1. HighHue", "Control", 180)
    cv2.setTrackbarPos("2. LowHue", "Control", 118)
    cv2.setTrackbarPos("3. HighSat", "Control", 255)
    cv2.setTrackbarPos("4. LowSat", "Control", 145)
    cv2.setTrackbarPos("5. HighVal", "Control", 255)
    cv2.setTrackbarPos("6. LowVal", "Control", 75)
    cv2.setTrackbarPos("7. Trnsfrm", "Control", 5)
    cv2.setTrackbarPos("8. RESET", "Control", 1)

def do_nothing(_):
    '''
    empty function
    '''

def show_transform_window(frame):
    '''
    takes video frame
        calls for frame binary transform
    displays window with frame transformed (done with HSV chanel split)
    '''
    frame_transformed = transform_image(frame)
    cv2.startWindowThread()
    cv2.namedWindow('Transformed frame')
    cv2.imshow('Transformed frame', frame_transformed)

def show_main_window(frame):
    '''
    takes video frame
        calls for frame object tracking
    displays main video frame window (with tracked objects marked)
    '''
    frame = track_selected_objects(frame)
    cv2.startWindowThread()
    cv2.namedWindow('Main frame')
    cv2.imshow('Main frame', frame)

def close(key):
    '''
    taked key pressed by user
        checks if the video loop closing condition is met
    returns boolean
    '''
    closure = False
    if key == ord('q'):
        closure = True
    elif cv2.getWindowProperty('Main frame',cv2.WND_PROP_AUTOSIZE) == -1:
        closure = True
    elif cv2.getWindowProperty('Transformed frame',cv2.WND_PROP_AUTOSIZE) == -1:
        closure = True
    elif cv2.getWindowProperty('Control',cv2.WND_PROP_AUTOSIZE) == -1:
        closure = True
    return closure

def pause(key):
    '''
    taked key pressed by user
        checks if pauseing video condition is met - space was pressed
    returns boolean
    '''
    if key == 32:
        return True # key == space
    return False

def transform_image(frame):
    '''
    takes video frame
        changes frame encoding to HSV (hue, saturation, value)
        reads values from (displayed) sliders
    returns a frame binary-transformed with stated values
    '''
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    low_hue = cv2.getTrackbarPos('2. LowHue', 'Control')
    high_hue = cv2.getTrackbarPos('1. HighHue', 'Control')
    low_sat = cv2.getTrackbarPos('4. LowSat', 'Control')
    high_sat = cv2.getTrackbarPos('3. HighSat', 'Control')
    low_val = cv2.getTrackbarPos('6. LowVal', 'Control')
    high_val = cv2.getTrackbarPos('5. HighVal', 'Control')
    transform = cv2.getTrackbarPos("7. Trnsfrm", "Control")
    lower_hsv = np.array([low_hue, low_sat, low_val])
    higher_hsv = np.array([high_hue, high_sat, high_val])
    mask = cv2.inRange(frame, lower_hsv, higher_hsv)
    if transform == 0:
        transform = 1
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel )
    mask = cv2.dilate(mask, kernel )
    mask = cv2.dilate(mask, kernel )
    mask = cv2.erode(mask, kernel )
    return mask

def track_selected_objects(frame):
    '''
    takes video frame
        uses binary mask to track selected objects -
        marks objects on the main video frame with circle
        shows distance-from-center of x-axis bar
    returns the frame with objects and distance marked
    '''
    mask = transform_image(frame)
    moments = cv2.moments(mask)
    m_01 = moments['m01']
    m_10 = moments['m10']
    total_area = moments['m00']
    white_area = total_area/255
    white_radius = int(math.sqrt(white_area/np.pi) )
    (_, _, frame_width, _) = cv2.getWindowImageRect('Main frame')
    window_middle_x = int(frame_width/2)
    if total_area == 0:
        white_center_x = window_middle_x
        white_center_y = window_middle_x
    else:
        white_center_x = int(m_10/total_area)
        white_center_y = int(m_01/total_area)
    start_point = (window_middle_x, 0)
    end_point = (white_center_x, 5)
    frame = cv2.rectangle(frame,
                       (white_center_x-white_radius, white_center_y-white_radius), (white_center_x+white_radius, white_center_y+white_radius),
                       color=(0,0,255), thickness=2)
    frame = cv2.rectangle(frame, start_point, end_point,
                          color=(0,0,255), thickness=-1)
    return frame

def main(args):
    '''
    standard main TODO function
    '''
    print("---------- MWR - LAB01 - s17186 --------------------\n")
    # Play video
    video = cv2.VideoCapture(args.input_video)  # 'F1_r.MOV'
    if not video.isOpened():
        print(f'Unable to open video at {args.input_video}')
    print("Loading...")
    play(video)
    # Terminate
    print("Program terminated. Goodbye. ")
    SystemExit()

def parse_args():
    '''
    parses input arguments for this simple program
        mandatory args:
            input_video = 'path to a video file'
    returns parsed args
    '''
    parser = argparse.ArgumentParser(
        description="Simple program to track objects of specified color " +
        "in the input video file. ")
    parser.add_argument('-i', '--input_video',
                        required=True, type=str, help='Path to video file')
    return parser.parse_args()

if __name__ == "__main__":
    arguments = parse_args()
    main(arguments)
    