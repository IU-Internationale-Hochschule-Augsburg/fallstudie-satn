import cv2

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

ret, frame = vc.read()
print("Eingestellte Auflösung",frame.shape[1]," x ", frame.shape[0])
while rval:
    #contrast erhöhen
    alpha = 2.0
    beta = 0
    contrast_enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

    #grey scale
    gray = cv2.cvtColor(contrast_enhanced, cv2.COLOR_BGR2GRAY)

    denoised = cv2.medianBlur(gray, ksize=3)

    cv2.imshow("preview", denoised)

    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()