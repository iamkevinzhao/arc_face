#!/usr/bin/env python
import rospy
import cv2
import socket
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

bridge = CvBridge()

class TCPServer:
    conn = []
    def __init__(self):
        sockin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockin.bind(("127.0.0.1", 2368))
        sockin.listen(1)
        self.conn, addr = sockin.accept()
    def __del__(self):
        self.conn.close()
    def parse(self):
        data = self.conn.recv(1024)
        data = data.decode()
        suf = data.rfind(']')
        prf = data.rfind('[')
        data = data[prf:suf+1]
        return data

server = TCPServer()

def callback(data):
    try:
        cv_img = bridge.imgmsg_to_cv2(data, 'bgr8')
    except CvBridgeError as e:
        print(e)
    msg = server.parse()
    print(msg)



def listener():

    rospy.init_node('arc_face', anonymous=True)
    rospy.Subscriber("/camera/color/image_raw", Image, callback)

    rospy.spin()


if __name__ == '__main__':
    listener()