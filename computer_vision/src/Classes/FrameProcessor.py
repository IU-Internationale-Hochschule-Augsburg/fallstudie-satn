try:
    from picamera2 import Picamera2, Preview
except ImportError:
    Picamera2 = None
    Preview = None
    
import cv2
import threading
import time

class FrameProcessor:
    """
    Encapsulation of the pi cam stream using Picamera2.
    """
    def __init__(self, width=1280, height=720, alpha=2.0, beta=0, blur_ksize=3):
        """
        :param width: width of the output
        :param height: height of the output
        :param alpha: contrast factor
        :param beta: brightness offset
        :param blur_ksize: kernel size for median blur
        """
        self.width = width
        self.height = height
        self.alpha = alpha
        self.beta = beta
        self.blur_ksize = blur_ksize
        self.picam2 = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()

    def open(self):
        """Initializes and starts the Picamera2 pipeline."""
        print("Opening Picamera2...")
        if self.running:
            print("is running")
            return
        # Configure Picamera2
        self.picam2 = Picamera2()
        self.picam2.start()
        self.running = True
        # Start background thread to grab frames
        threading.Thread(target=self._capture_loop, daemon=True).start()
        timeout = time.time() + 3
        while self.frame is None:
            if time.time() > timeout:
                raise RuntimeError("Timeout: Kamera liefert kein erstes Frame")
            time.sleep(0.1)

    def release(self):
        """Stops the camera and releases resources."""
        if not self.running:
            return
        self.running = False
        if self.picam2:
            self.picam2.stop()
            self.picam2.close()
            self.picam2 = None

    def _capture_loop(self):
        """Continuously captures frames from Picamera2 to self.frame."""
        while self.running:
            try:
                frame = self.picam2.capture_array()
                with self.lock:
                    self.frame = frame
            except Exception as e:
                print(f"Fehler beim Frame-Capture: {e}")

    def _process_frame(self, frame):
        """
        Convert the input image to grayscale, enhance contrast, and reduce noise.
        :param frame: Input image (RGB or grayscale as numpy array)
        :return: Processed image (grayscale, denoised)
        """
        # Convert RGB to BGR for OpenCV processing
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # Adjust contrast and brightness
        contrasted = cv2.convertScaleAbs(bgr, alpha=self.alpha, beta=self.beta)
        # Convert to grayscale
        gray = cv2.cvtColor(contrasted, cv2.COLOR_BGR2GRAY)
        # Reduce noise using median filter
        denoised = cv2.medianBlur(gray, ksize=self.blur_ksize)
        return denoised

    def get_frame(self):
        """
        Reads the latest frame, processes it, and encodes it as JPEG.
        :return: (ok: bool, jpeg_bytes: bytes)
        """
        print("is_running", self.running)
        print("has_frame", self.frame)
        if not self.running or self.frame is None:
            return False, None
        with self.lock:
            frame = self.frame.copy() if self.frame is not None else None
            print("frame copied")
        if frame is None:
            return False, None
        processed = self._process_frame(frame)
        print("processed")
        return True, processed

    def frame_generator(self):
        """
        Generator for Flask endpoint to stream video frames (MJPEG).
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
