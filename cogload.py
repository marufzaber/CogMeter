"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.


The algothim is based on the paper - 
'Measuring Cognitive Load using Eye Tracking Technology in Visual Computing. 
Johannes Zagermann, Ulrike Pfeil, and Harald Reiterer. HCI Group, University of Konstanz
{johannes.zagermann,ulrike.pfeil,harald.reiterer}@uni-konstanz.de'

"""

import cv2
import time
import math 
import tkinter
import requests
import datetime as dt
from gaze_tracking import GazeTracking
from dataclasses import dataclass
from operator import is_not
from functools import partial


@dataclass
class Pupil_position:
    position: str
    time: int


access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkM0TVYiLCJzdWIiOiI3UUNSVzMiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNjE1OTk1ODI1LCJpYXQiOjE2MTUzOTEyNDN9.et2RMh0Dc7Zipoz4xFHXCg_imyZFYLomhI3mLZ1852k"
header = {'Authorization': 'Bearer {}'.format(access_token)}

def calculate_cog_load():
    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0)

    pupil_position = Pupil_position('center', 0)

    t = dt.datetime.now()
    start_time = dt.datetime.now()
    blink_count = 0 
    saccades = 0
    pupil_dilation_x = []
    pupil_dilation_y = []
    fixations = [0]
    minute = 0
    blink_rate = 0
    saccades_rate = 0
    pup_dil_x = 0
    pup_dil_y = 0
    fixation_avg = 0
    cogload = 0

    while True:
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        response = requests.get(
            "https://api.fitbit.com/1/user/7QCRW3/activities/heart/date/today/today.json", 
            headers=header).json()

        frame = gaze.annotated_frame()
        text = ""

        pupil_dilation_x.append(gaze.horizontal_ratio())
        pupil_dilation_y.append(gaze.vertical_ratio())

        horizontal_ratio = gaze.horizontal_ratio()
        vertical_ratio = gaze.vertical_ratio()
       
        if horizontal_ratio is not None:
            pupil_dilation_x.append(horizontal_ratio)

        if vertical_ratio is not None:
            pupil_dilation_y.append(vertical_ratio)

        if gaze.is_blinking():
            text = "Blinking"
            blink_count = blink_count + 1

        elif gaze.is_right():
            delta = dt.datetime.now() - t
            position = Pupil_position('right', delta.seconds)
            if position.position != pupil_position.position:
                diff = delta.seconds - pupil_position.time
                fixations.append(diff)
                pupil_position = position
                saccades = saccades + 1

            text = "Looking right"

        elif gaze.is_left():
            delta = dt.datetime.now() - t
            position = Pupil_position('left', delta.seconds)
            if position.position != pupil_position.position:
                diff = delta.seconds - pupil_position.time
                fixations.append(diff)
                pupil_position = position
                saccades = saccades + 1

            text = "Looking left"

        elif gaze.is_center():
            delta = dt.datetime.now() - t
            position = Pupil_position('center', delta.seconds)
            if position.position != pupil_position.position:
                diff = delta.seconds - pupil_position.time
                fixations.append(diff)
                pupil_position = position
                saccades = saccades + 1

            text = "Looking center"

        cv2.putText(
            frame, 
            text, 
            (90, 60), 
            cv2.FONT_HERSHEY_DUPLEX, 
            1.6, 
            (147, 58, 31), 
            2
        )

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        cv2.putText(
            frame, 
            "Left pupil:  " + str(left_pupil), 
            (90, 130), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Right pupil: " + str(right_pupil), 
            (90, 165), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Blink Rate: " + str(blink_rate), 
            (90, 195), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Saccades Rate: " + str(saccades_rate), 
            (90, 225), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Pupil dilation x: " + str(pup_dil_x), 
            (90, 255), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Pupil dilation y: " + str(pup_dil_y), 
            (90, 285), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Fixation: " + str(fixation_avg), 
            (90, 315), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.putText(
            frame, 
            "Cognitive Load: " + str(cogload), 
            (90, 345), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        delta = dt.datetime.now() - t

        elapsed_time = dt.datetime.now() - start_time
        elapsed_time_second = elapsed_time.seconds

        cv2.putText(
            frame, 
            "Elapsed Time: " + str(elapsed_time_second), 
            (90, 375), 
            cv2.FONT_HERSHEY_DUPLEX, 
            0.9, 
            (147, 58, 31), 
            1
        )

        cv2.imshow("Demo", frame)

        if delta.seconds >= 10:
            minute = minute + 1
            blink_rate = blink_count / 10
            saccades_rate = saccades / 10

            Not_none_values_x = filter(None.__ne__, pupil_dilation_x)
            Not_none_values_y = filter(None.__ne__, pupil_dilation_y)

            pupil_dilation_x = list(Not_none_values_x)
            pupil_dilation_y = list(Not_none_values_y)
            
            pup_dil_x = sum(pupil_dilation_x) / len(pupil_dilation_x)
            pup_dil_y = sum(pupil_dilation_y) / len(pupil_dilation_y)

            fixation_avg = sum(fixations) / len(fixations)

            blink_count = 0 
            saccades = 0
            
            pupil_position = Pupil_position('center', 0)

            t = dt.datetime.now()

            pupil_dilation_x = []
            pupil_dilation_y = []
            fixations = [0]

            print(response['activities-heart-intraday']['dataset'][-1]['value'])

            cogload = blink_rate   \
                + math.sqrt(pup_dil_x * pup_dil_x + pup_dil_y * pup_dil_y) \
                + saccades_rate \
                - fixation_avg
            
            print(blink_rate)
            print(pup_dil_x)
            print(pup_dil_y)
            print(saccades_rate)
            print(fixation_avg)
            print(cogload)
            write_csv(
                'data.csv', 
                minute, 
                blink_rate, 
                pup_dil_x, 
                pup_dil_y, 
                fixation_avg, 
                saccades_rate, 
                cogload
            )

        if cv2.waitKey(33) == 27:
            break
        time.sleep(0.25)

def write_csv(
    filename, 
    minute, 
    blink_rate, 
    pupil_dilation_x, 
    pupil_dilation_y, 
    fixation, 
    Saccades, 
    cogload):
    with open(filename, mode='w', encoding='UTF-8', errors='strict', buffering=1) as file:
        data = str(minute) + \
            "," + str(blink_rate) + \
            "," + str(pupil_dilation_x) + \
            "," + str(pupil_dilation_y) + \
            "," + str(fixation) + \
            "," + str(Saccades) + \
            "," + str(cogload)
        print(data)
        file.write(data)
        file.write('\n')
def main():
    calculate_cog_load()

if __name__ == "__main__":
    main()
