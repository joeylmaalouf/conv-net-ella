import numpy as np
import os
import glob
import cv2


def get_data():
	x_paths = []
	y = []
	datasets_dir = "/".join(os.path.abspath(__file__).split("/")[:-1])+"/data_set/"
	for d in glob.glob(datasets_dir+"*/"):
		label = int(d[-2])
		paths = glob.glob(d+"*-full.png")
		x_paths.extend(paths)
		for path in paths:
			y.append(0 if "out" in path else label)
	l=[]
	for p in x_paths:
		img=cv2.imread(p)
		size=img.shape
		print "---"
		print size
		m=10
		size=(size[1]/m,size[0]/m)
		img=cv2.resize(img,size)
		print img.shape
		l.append(img)
	print l
	x = np.asarray(l)
	y = np.asarray(y)
	return x, y


if __name__ == "__main__":
	x, y = get_data()
	np.save("data_x.npy", x)
	np.save("data_y.npy", y)
