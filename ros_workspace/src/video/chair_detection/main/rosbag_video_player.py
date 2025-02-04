#!/usr/bin/env python
# license removed for brevity

import pygtk
pygtk.require('2.0')
import gtk
import rosbag
import rospy
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float64
import sys
from os.path import exists


class Rosbag_video_player:
    def __init__(self):
        self.filew = gtk.FileSelection("File selection")
        self.filew.connect("destroy", gtk.main_quit)
        self.filew.ok_button.connect("clicked", self.file_ok_sel)
        self.filew.cancel_button.connect("clicked",
                                         lambda w: self.filew.destroy())
        filepath = "./test.txt"
        if exists(filepath):
            self.f = open(filepath, "r+")
            self.pre_filename=self.f.read()
        else:
            self.f = open(filepath, "w")
            self.pre_filename = None
        if self.pre_filename:
            self.filew.set_filename(str(self.pre_filename))
        self.filew.show()

    def file_ok_sel(self, w):
        filename=self.filew.get_filename()
        self.f.seek(0)
        self.f.truncate()
        self.f.write(filename)
        self.f.close()
        self.filew.destroy()
        gtk.main_quit()
        self.rosbag_play(filename)
        sys.exit(0)
    
    def rate_callback(self, data):
        rate=data.data
        self.r=rospy.Rate(rate)

    def rosbag_play(self, filename="test.bag"):
        bag = rosbag.Bag(filename)
        rospy.init_node('rosbag_publish', anonymous=True)
        self.r=rospy.Rate(15)
        pub = rospy.Publisher("/camera/rgb/image_color/compressed", CompressedImage, queue_size=10)
        rospy.Subscriber("rosbag_rate", Float64, self.rate_callback)
        for topic, msg, t in bag.read_messages(topics=['/camera/rgb/image_color/compressed']):
           pub.publish(msg)
           self.r.sleep()
           if rospy.is_shutdown():
               break
           print"publish ", msg.header
        bag.close()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    Rosbag_video_player()
    main()