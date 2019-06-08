#!/usr/bin/env python
import rospy
import cv2
import socket
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
from recognition import Recognition

bridge = CvBridge()
recog = Recognition()

slam_pose = ""

class TCPClient:
    sock = []
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", 2369))
    def __del__(self):
        self.sock.close()
    def send(self, data):
        self.sock.send(data.encode())
    def parse(self):
        data = self.conn.recv(1024)
        data = data.decode()
        suf = data.rfind(']')
        prf = data.rfind('[')
        data = data[prf:suf+1]
        return data

tcp = TCPClient()

def callback(data):
    try:
        cv_img = bridge.imgmsg_to_cv2(data, 'bgr8')
    except CvBridgeError as e:
        print(e)
    pose = slam_pose
    (name, dist) = recog.process(cv_img)
    if name:
        pose = pose.replace('robot', name)
        pose = pose.replace('dist:0', 'dist:' + str(dist))
        print(pose)
        tcp.send(pose)


def pose_callback(data):
    global slam_pose
    slam_pose = data.data

def listener():

    rospy.init_node('arc_face', anonymous=True)
    rospy.Subscriber("/camera/color/image_raw", Image, callback)
    rospy.Subscriber("/arc_pose", String, pose_callback)
    rospy.spin()


if __name__ == '__main__':
    listener()