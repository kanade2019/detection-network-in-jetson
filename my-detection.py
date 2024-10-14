import jetson.inference
import jetson.utils
from jetson.inference import detectNet
from jetson.utils import videoSource, videoOutput
import argparse
import sys
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument("--useCamera", type=bool, default=False)
parser.add_argument("--input", type=str, default="/home/nvidia/jetson-inference/data/images/bird_0.jpg")
parser.add_argument("--output", type=str, default="")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# coco dataset labels
labels_file=open("coco-labels-paper.txt","r")
labels_data=labels_file.read()
labels_list=labels_data.split("\n")
colors=[tuple(np.random.choice(range(256), size=3)) for i in range(len(labels_list))]
font=ImageFont.truetype("Arial.ttf",20)
print(labels_list)
# read model
net =detectNet("ssd-mobilenet-v2", threshold=0.5)

if opt.useCamera is True:
	camera = videoSource("/dev/video0")

	display = videoOutput("display://0")

	while display.IsStreaming():
		img = camera.Capture()

		if img is None:
			continue
		detections = net.Detect(img)
		display.Render(img)
		display.SetStatus("Object Detection | Network{:.0f}FPS".format(net.GetNetworkFPS()))
else:
	img = Image.open(opt.input)
	imgD = ImageDraw.Draw(img)
	print("input:" + opt.input)
	#plt.imshow(img)
	#plt.show()
	detections = net.Detect(jetson.utils.cudaFromNumpy(np.array(img)))
	for one_detection in detections:
		print(one_detection)
		if opt.output:
			color=colors[one_detection.ClassID]
			#print([(one_detection.Left,one_detection.Top),(one_detection.Right,one_detection.Bottom)])
			imgD.rectangle([(one_detection.Left,one_detection.Top),(one_detection.Right,one_detection.Bottom)],outline=color,width=5)
			imgD.rectangle([(one_detection.Left,one_detection.Top),(one_detection.Left+120,one_detection.Top-20)],fill=color,outline=color,width=5)
			#print(str(labels_list[one_detection.ClassID-1]))
			imgD.text((one_detection.Left,one_detection.Top-20), str(labels_list[one_detection.ClassID-1])+" %.2f%%" % (one_detection.Confidence*100),fill="white", font=font)
	print("output:"+opt.output+"out-"+os.path.basename(opt.input))
	img.save(opt.output+"out-"+os.path.basename(opt.input))
