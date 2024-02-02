"""
Big thanks to a great mind codenamed: atulapra
Reference: https://github.com/atulapra/Emotion-detection
"""

from __future__ import division, absolute_import
import numpy as np
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected, flatten
from tflearn.layers.conv import conv_2d, max_pool_2d, avg_pool_2d
from tflearn.layers.merge_ops import merge
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
from os.path import isfile, join
import sys
import tensorflow as tf
import cv2
import os

# prevents opencl usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# prevents appearance of tensorflow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.logging.set_verbosity(tf.logging.ERROR)

EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']

emotion_util_path = os.path.join(os.getcwd(), 'emotion_util')

class EMR:
  def __init__(self):
    self.target_classes = EMOTIONS
    self.build_network()

  def format_image(self, image):
    """
    Function to format frame
    """
    if len(image.shape) > 2 and image.shape[2] == 3:
        # determine whether the image is color
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        # Image read from buffer
        image = cv2.imdecode(image, cv2.CV_LOAD_IMAGE_GRAYSCALE)

    cascade_classifier = cv2.CascadeClassifier(os.path.join(emotion_util_path, 'haarcascade_frontalface_default.xml'))
    faces = cascade_classifier.detectMultiScale(image, scaleFactor = 1.3 ,minNeighbors = 5)

    if not len(faces) > 0:
        return None

    # initialize the first face as having maximum area, then find the one with max_area
    max_area_face = faces[0]
    for face in faces:
        if face[2] * face[3] > max_area_face[2] * max_area_face[3]:
            max_area_face = face
    face = max_area_face

    # extract ROI of face
    image = image[face[1]:(face[1] + face[2]), face[0]:(face[0] + face[3])]

    try:
        # resize the image so that it can be passed to the neural network
        image = cv2.resize(image, (48,48), interpolation = cv2.INTER_CUBIC) / 255.
    except Exception:
        print("----->Problem during resize")
        return None

    return image

  def build_network(self):
      """
      Build the convnet.
      Input is 48x48
      3072 nodes in fully connected layer
      """ 
      self.network = input_data(shape = [None, 48, 48, 1])
      self.network = conv_2d(self.network, 64, 5, activation = 'relu')
      self.network = max_pool_2d(self.network, 3, strides = 2)
      self.network = conv_2d(self.network, 64, 5, activation = 'relu')
      self.network = max_pool_2d(self.network, 3, strides = 2)
      self.network = conv_2d(self.network, 128, 4, activation = 'relu')
      self.network = dropout(self.network, 0.3)
      self.network = fully_connected(self.network, 3072, activation = 'relu')
      self.network = fully_connected(self.network, len(self.target_classes), activation = 'softmax')
      # Generates a TrainOp which contains the information about optimization process - optimizer, loss function, etc
      self.network = regression(self.network,optimizer = 'momentum',metric = 'accuracy',loss = 'categorical_crossentropy')
      # Creates a model instance.
      self.model = tflearn.DNN(self.network,checkpoint_path = 'model_1_atul',max_checkpoints = 1,tensorboard_verbose = 2)
      # Loads the model weights from the checkpoint
      self.load_model()

  def predict(self, image):
    """
    Image is resized to 48x48, and predictions are returned.
    """
    if image is None:
      return None
    image = image.reshape([-1, 48, 48, 1])
    
    return self.model.predict(image)

  def load_model(self):
    """
    Loads pre-trained model.
    """
    if isfile(os.path.join(emotion_util_path, "model_1_atul.tflearn.meta")):
      self.model.load(os.path.join(emotion_util_path, "model_1_atul.tflearn"))
    else:
        print("---> Couldn't find model")
  
  def get_emotion(self, image_file):
    img = cv2.imread(image_file)
    result = self.predict(self.format_image(img))
    if result is not None:
    # find the emotion with maximum probability and display it
      maxindex = np.argmax(result[0])
      return EMOTIONS[maxindex]

