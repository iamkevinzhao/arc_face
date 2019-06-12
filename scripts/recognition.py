import sys
sys.path.append("/home/kevin/.local/lib/python3.5/site-packages")
import os
import face_recognition
import cv2
import numpy as np
import glob
import math

class Recognition:
    known_face_encodings = []
    known_face_names = []
    process_this_frame = True
    face_locations = []
    face_encodings = []
    face_names = []
    def __init__(self):
        files = glob.glob('./images/*.jpeg')
        for file in files:
            img = face_recognition.load_image_file(file)
            encoding = face_recognition.face_encodings(img)[0]
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(os.path.splitext(os.path.basename(file))[0])
        print(self.known_face_names)
    def process(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        best_name = []
        max_box_ratio = 0
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # size = sqrt(pow(top - bottom, 2) + pow(left - right, 2))
            w = np.size(frame, 0)
            h = np.size(frame, 1)
            center = ((bottom + top) / 2, (right + left) / 2)
            margin = 0.25
            # print(center, w * margin, w * (1 - margin))
            if (center[0] < w * margin) or (center[0] > w * (1 - margin)):
                continue
            if (center[1] < h * margin) or (center[1] > h * (1 - margin)):
                continue
            ratio = math.sqrt(pow(top - bottom, 2) + pow(left - right, 2)) / math.sqrt(pow(w, 2) + pow(h, 2))
            # if ratio < 0.20:
            #     continue
            if ratio > max_box_ratio:
                best_name = name
                max_box_ratio = ratio

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        cv2.waitKey(1)

        return best_name, max_box_ratio


