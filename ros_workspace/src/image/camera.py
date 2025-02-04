#!/usr/bin/env python
import roslib
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class Decompresser(object):
	def __init__(self):
		self.sub = rospy.Subscriber("camera/rgb/image_color/compressed", Image, self.callback)
		self.pub = rospy.Publisher("decompressed", Image)

	def callback(self, data):
		# figure out Python version of
		# rosrun image_transport republish in:=/camera/rgb/image_color compressed out:=/camera/rgb/image_color raw
		# http://wiki.ros.org/image_transport
		# "image_transport does not yet support Python, though it is on the Roadmap" :(
		# somehow use roslaunch python API (http://wiki.ros.org/roslaunch/API%20Usage)
		# to call the command from a .launch file?
		self.pub.publish(data)


class Converter(object):
	def __init__(self):
		self.sub = rospy.Subscriber("decompressed", Image, self.callback)
		self.bridge = CvBridge()

	def callback(self, data):
		try:
			self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
		except CvBridgeError, e:
			rospy.loginfo(e)

		rospy.loginfo(self.cv_image.shape)
		# manipulate self.cv_image, send to convnet for prediction


if __name__ == "__main__":
	rospy.init_node("image_decompresser_listener", anonymous = True)
	d = Decompresser()
	c = Converter()
	rospy.spin()
