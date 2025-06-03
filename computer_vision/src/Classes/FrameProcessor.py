try:
    from picamera2 import Picamera2, Preview
except ImportError:
    Picamera2 = None
    Preview = None

import cv2

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
        processed = self._process_frame(frame)
        return True, processed

    def frame_generator(self):
        """
        Generator für Flask-Endpoint, um MJPEG-Stream zu liefern.
        """
        try:
            while True:
                ok, jpeg = self.get_frame()
                if not ok:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
        finally:
            self.release()