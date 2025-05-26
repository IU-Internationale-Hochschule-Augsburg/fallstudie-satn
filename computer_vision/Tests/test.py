import cv2
from src.Classes.ObjectDetection.object_detection import ObjectDetection

img = cv2.imread('img2.jpg')

od = ObjectDetection()

od.demo_object_detection(img)

print(od.getZumoPosition(img))