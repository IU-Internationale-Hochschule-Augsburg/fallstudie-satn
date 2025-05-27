import cv2
from src.Classes.ObjectDetection.ObjectDetection import ObjectDetection
from computer_vision.src.Classes.ObjectDetection.object_detection import ObjectDetection
from computer_vision.src.Utils.pathfinding import get_next_task

img = cv2.imread('img2.jpg')
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
img_edited = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

od = ObjectDetection()
cropped_img = od.crop_image(img_edited)
cv2.imshow('cropped_img', cropped_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
objects = od.get_object_position(cropped_img)
zumo = od.getZumoPosition(cropped_img)
positions = {
    "zumo": zumo,
    "objects": objects
}
print(positions)
#print(vars(get_next_task(positions)))
