try:
    from picamera2 import Picamera2, Preview
except ImportError:
    Picamera2 = None
    Preview = None

import cv2
import numpy as np

class FrameProcessor:
    """
    Encapsulation of the pi cam stream using Picamera2,
    ohne Hintergrund-Thread: get_frame holt jeweils nur ein Frame.
    """
    def __init__(self, width=1280, height=720, alpha=2.0, beta=0, blur_ksize=3):
        """
        :param width: Breite des Ausgabebildes
        :param height: Höhe des Ausgabebildes
        :param alpha: Kontrastfaktor
        :param beta: Helligkeitsoffset
        :param blur_ksize: Kernelgröße für Median-Blur
        """
        self.width = width
        self.height = height
        self.alpha = alpha
        self.beta = beta
        self.blur_ksize = blur_ksize
        self.picam2 = None

    def open(self):
        """Initialisiert und startet die Picamera2-Pipeline."""
        if self.picam2 is not None:
            # Bereits geöffnet
            return

        print("Opening Picamera2...")
        self.picam2 = Picamera2()
        # Optional: Auflösung oder Konfiguration einstellen
        # config = self.picam2.create_preview_configuration(
        #     main={"format": "RGB888", "size": (self.width, self.height)}
        # )
        # self.picam2.configure(config)
        self.picam2.start()

    def release(self):
        """Stoppt die Kamera und gibt Ressourcen frei."""
        if self.picam2:
            self.picam2.stop()
            self.picam2.close()
            self.picam2 = None

    def _process_frame(self, frame):
        """
        Verarbeitet das aufgenommene Bild: Kontrast/ Helligkeit anpassen,
        Graustufen und Rauschreduzierung.
        :param frame: Eingabebild (RGB als numpy array)
        :return: verarbeiteter Graustufen-Frame
        """
        # RGB → BGR für OpenCV
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Kontrast und Helligkeit anpassen
        contrasted = cv2.convertScaleAbs(bgr, alpha=self.alpha, beta=self.beta)
        # In Graustufen umwandeln
        gray = cv2.cvtColor(contrasted, cv2.COLOR_BGR2GRAY)
        # Rauschen mit Median-Filter reduzieren
        denoised = cv2.medianBlur(gray, ksize=self.blur_ksize)
        return denoised

    def get_frame(self):
        """
        Holt ein einzelnes Bild von der Kamera, verarbeitet es und kodiert als JPEG.
        :return: (ok: bool, jpeg_bytes: bytes)
        :rtype: Boolean, numpy.ndarray
        """
        if self.picam2 is None:
            return False, None

        try:
            # Einmaliges Capture
            frame = self.picam2.capture_array()
        except Exception as e:
            print(f"Fehler beim Frame-Capture: {e}")
            return False, None
        finally:
            self.release()

        if frame is None:
            return False, None

        # Verarbeiten
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fixed = self.fix_perspective(gray)
        return True, fixed

    def frame_generator(self):
        """
        Generator für Flask-Endpoint, um MJPEG-Stream zu liefern.
        """
        try:
            while True:
                try:
                    ok, jpeg = self.get_frame()
                except StopIteration:
                    break
                if not ok:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
        finally:
            self.release()

    def fix_perspective(self,img):
        _, tresh = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(tresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if hierarchy is None or len(hierarchy) == 0:
            return None

        hierarchy = hierarchy[0]

        for i, contour in enumerate(contours):
            if hierarchy[i][3] == -1:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

                if len(approx) == 4 and cv2.isContourConvex(approx):
                    pts = approx.reshape(4, 2)
                    rect = self.order_points(pts)

                    # Zielrechteck (z. B. 300x400 px)
                    width, height = 300, 400
                    dst = np.array([
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1]
                    ], dtype="float32")

                    # Transformation berechnen und anwenden
                    M = cv2.getPerspectiveTransform(rect, dst)
                    warped = cv2.warpPerspective(img, M, (width, height))

                    return warped

    def order_points(self,pts):
        # Punkte sortieren: [top-left, top-right, bottom-right, bottom-left]
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect