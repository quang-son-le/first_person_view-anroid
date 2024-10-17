import cv2
import io
import socket
import struct
import time
import pickle
import zlib
import sim as vrep
import numpy as np
from PIL import Image as I
import array
clientID = vrep.simxStart('127.0.0.1', 19998, True,
                          True, 5000, 5)  # Connect to V-REP
res, v0 = vrep.simxGetObjectHandle(
    clientID, 'v0', vrep.simx_opmode_oneshot_wait)  # 'Quadricopter_frontCamera'

# end of vrep
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8485))
connection = client_socket.makefile('wb')

cam = cv2.VideoCapture('test.mp4')

cam.set(3, 320)
cam.set(4, 240)

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
err, resolution, image = vrep.simxGetVisionSensorImage(
    clientID, v0, 0, vrep.simx_opmode_streaming)
time.sleep(1)

while True:
    ret, frame = cam.read()
    res, resolution, image = vrep.simxGetVisionSensorImage(
        clientID, v0, 0, vrep.simx_opmode_buffer)
    print(res)
    # print(resolution)
    # print(image)
    if res == vrep.simx_return_ok:
        # print(resolution[1])
        img = np.array(image, dtype=np.uint8)
        img.resize([resolution[1], resolution[0], 3])
        result, frame = cv2.imencode('.jpg', img, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)
    # print("{}: {}".format(img_counter, size))
        client_socket.sendall(struct.pack(">L", size) + data)
        img_counter += 1
    if res == vrep.simx_return_novalue_flag:
        # result, frame = cv2.imencode('.jpg', frame, encode_param)
        print('no image')
        pass
#    data = zlib.compress(pickle.dumps(frame, 0))


cam.release()
