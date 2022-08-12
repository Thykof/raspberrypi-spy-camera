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



class MotionDetector():
    def __init__(self, send_email, username, password, smpt_server_url, user_email=None, trigger_level=100):
        print 'initialising, please wait...'

        NUM_MOTION_FRAMES = 6

        self.NUM_MOTION_FRAMES = NUM_MOTION_FRAMES
        self.trigger_level = trigger_level

        camera = cv2.VideoCapture(0)

        if camera:
            motion = False

            while True:
                time.sleep(1)
                if not motion:
                    # save last image if it exists
                    try:
                        motion_images = []
                        motion_images.append(opencv_image)
                    except:
                        pass

                    # get latest image
                    ret, opencv_image = camera.read() 

                    # detect motion
                    detection_level = self.detect_motion(opencv_image)
                    motion = self.refire_rate_limit(detection_level)

                    if motion:
                        print 'motion detected !'
                        print 'saving images...'
                        time_stamp = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
                        motion_images.append(opencv_image)
                        
                        es = email_helper.EmailServer(username, password, smpt_server_url)
                        subject = 'MOTION CAPTURED!'
                        text = '''<b>Captured! {0}<br>
                                    <img src="cid:image0"><br><br>
                                    <img src="cid:image1"><br><br>
                                    <img src="cid:image2"><br><br>
                                    <img src="cid:image3"><br><br>
                                    <img src="cid:image4"><br><br>
                                    <img src="cid:image5"><br><br>
                                '''.format(time_stamp)
                        alternative_text = 'pictures from motion detected'
                        es.create_email(subject, text, alternative_text)
                elif motion:
                    motion_images.append(opencv_image)

                    if len(motion_images) >= NUM_MOTION_FRAMES:
                        for i, image in enumerate(motion_images):
                            image_filename = '{0} frame {1}.png'.format(time_stamp, i)
                            cv2.imwrite(image_filename, image)
                            # send images as email
                            es.attach_file_image(image_filename)
                        es.send_email(send_email)

                        motion = False
                        motion_images = []

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
        return detection_level

    def refire_rate_limit(self, detection_level):
        REFIRE_TIME = 6    # seconds
        # initialisation
        try:
            self.last_alarm_time
        except:
            self.last_alarm_time = datetime.now()

        current_time = datetime.now()
        time_since_last_alarm = (current_time - self.last_alarm_time).seconds
        if time_since_last_alarm > REFIRE_TIME:
            print 'monitoring: level {0} (trigger level {1})'\
                .format(detection_level, self.trigger_level)
            if detection_level > self.trigger_level:
                self.last_alarm_time = current_time
                return True
        else:
            return False


def main():
    if len(sys.argv) < 4:
        raise ValueError('wrong number of arguments')

    send_email = sys.argv[1]  # where you want the email sent to
    # smpt server settings...
    smpt_server_url = 'smtp.gmail.com'
    username = sys.argv[2]  # username of your smpt server
    # (password is entered at commandline)
    user_email = None  # if different from username (leave 'None' for gmail)
    # trigger level
    trigger_level = 10
    password = sys.argv[3]

    MotionDetector(send_email, username, password, smpt_server_url, user_email, trigger_level)

if __name__ == '__main__':
    main()
