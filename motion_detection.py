# Copyright (c) Senthil Seveelavanan 2014
#
# This software may be used and distributed
# according to the terms of the GNU General Public License version 2, incorporated
# herein by reference.

# Modified by Thykof in 2022

import cv2

import sys
from datetime import datetime
import numpy as np
import time
import email_with_attatchements as email_helper

IDLE = "IDLE"
ALERT = "ALERT"

class MotionDetector():
    def __init__(self, send_email, username, password, smpt_server_url, trigger_level=11, stack=5):
        print 'initialising, please wait...'
        self.send_email = send_email
        self.username = username
        self.password = password
        self. smpt_server_url = smpt_server_url
        self.trigger_level = trigger_level
        self.stack = stack

        self.status = IDLE

        self.camera = cv2.VideoCapture(0)
                
        self.es = email_helper.EmailServer(username, password, smpt_server_url)

        self.motion_images = []

    def start(self):
        try:
            self.monitor()
        except:
            # TODO: send email
            pass

    def monitor(self):
        while True:
            # get latest image
            _, opencv_image = camera.read() 

            # detect motion
            motion = self.detect_motion(opencv_image)

            timestamp = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

            if self.status == IDLE:
                self.motion_images = [{'image': opencv_image, "timestamp": timestamp}]
                if motion:
                    print 'motion detected !'
                    self.status = "ALERT"
                    content = '<b>Captured! {0}<br>'
                    for i in self.motion_images:
                        content += '<img src="cid:image{0}"><br><br>'.format(i)
                    content = content.format(timestamp)
                    self.es.create_email('MOTION CAPTURED!', content, 'pictures from motion detected')

            elif self.status == ALERT:
                self.motion_images.append({'image': opencv_image, "timestamp": timestamp})
                if (motion and len(self.motion_images) >= self.stack) or (not motion):
                    for i, image_dict in enumerate(self.motion_images):
                        image = image_dict['image']
                        timestamp = image_dict['timestamp']
                        image_filename = '{0} frame {1}.png'.format(timestamp, i)
                        cv2.imwrite(image_filename, image)
                        # send images as email
                        self.es.attach_file_image(image_filename)
                    self.es.send_email(self.send_email)
                    self.motion_images = []

    def detect_motion(self, image):
        resize_resolution = (640/8, 480/8)
        image = cv2.resize(image, resize_resolution)   # reduce image size

        # if self.avg1 doesn't exist, initialise
        try:
            self.avg1
        except:
            self.avg1 = np.float32(image)

        cv2.accumulateWeighted(image, self.avg1, 0.7)
        res1 = cv2.convertScaleAbs(self.avg1)
        difference = cv2.absdiff(res1, image)   # moving average - current_frame
        detection_level = np.sum(difference) / 1000

        if detection_level > self.trigger_level:
            return True
        return False

def main():
    if len(sys.argv) < 5:
        raise ValueError('wrong number of arguments')

    send_email = sys.argv[1]  # where you want the email sent to
    # smpt server settings...
    smpt_server_url = 'smtp.gmail.com'
    username = sys.argv[2]  # username of your smpt server
    # password is entered at commandline
    password = sys.argv[3]
    # trigger level
    trigger_level = int(sys.argv[3]);

    motion_detector = MotionDetector(send_email, username, password, smpt_server_url, trigger_level)
    motion_detector.start()

if __name__ == '__main__':
    main()
