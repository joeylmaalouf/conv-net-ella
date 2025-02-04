from collections import Counter
import lmdb
import math
import numpy as np
import os
import sys
import time

sys.path.insert(0, "../")
from functions.Array import binarize

# so we can access the data files
os.chdir("../../caffe")
# let us import caffe
sys.path.insert(0, "./python")
# hide caffe output
os.environ["GLOG_minloglevel"] = "2"
import caffe


# create our own prediction function
def __predict(self, input):
	if len(input.shape) > 4:
		input = input[np.newaxis]

	num_items = input.shape[0]
	batch_items = net.blobs["data"].data.shape[0]
	num_batches = int(math.ceil(float(num_items)/batch_items))

	predictions = np.zeros(input.shape[0], dtype = np.int64)

	for batch in range(num_batches):
		indices = slice(batch*batch_items, (batch+1)*batch_items)
		batch_data = input[indices]

		for ind, val in enumerate(batch_data):
			self.blobs["data"].data[ind] = val

		self.forward(start = "conv1")

		predictions[indices] = self.blobs["ip2"].data.argmax(1)[:len(batch_data)].copy()
	return predictions
caffe.Net.predict = __predict


def open_dataset(path):
	cursor = lmdb.open(path, map_size = 100000000).begin(write = False).cursor()
	X, Y = [], []
	for key, val in cursor:
		datum = caffe.proto.caffe_pb2.Datum.FromString(val) # opposite of val = datum.SerializeToString(), just like the opposite of val = cursor.get(id) is db_cursor.put(id, val, overwrite = True)
		X.append(caffe.io.datum_to_array(datum))
		Y.append(datum.label)
	return np.asarray(X), np.asarray(Y)


if __name__ == "__main__":
	caffe.set_device(0)
	caffe.set_mode_gpu()

	net = caffe.Net("examples/mnist/lenet_auto_test.prototxt", "examples/mnist/lenet_iter_10000.caffemodel", caffe.TEST)
	trX, trY = open_dataset("examples/mnist/mnist_train_lmdb")
	teX, teY = open_dataset("examples/mnist/mnist_test_lmdb")
	predictions = net.predict(teX)
	print("\nNet Predictions:")
	print("Predicted: {0}".format(Counter(predictions)))
	print("Actual:    {0}".format(Counter(teY)))
	print("Accuracy:  {0:0.04f}".format(np.mean(predictions == teY)))


	# todo:

	# figure out how to extract activations for top-layer model
	# these seem to be the weights, not activations
	print("\nNet Blobs:")
	for key, val in net.blobs.items():
		print("  {0}, {1}".format(key, val.data.shape))

	# make binary nets for multi-net model
	# I can change values here, but it needs to be done before training and loading the nets
	print("\nBinarized Labels:")
	print(trY[:20].tolist())
	for c in range(10):
		print(binarize(trY[:20], c).tolist())
