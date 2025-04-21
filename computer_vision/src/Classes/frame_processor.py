import cv2

class FrameProcessor():
    """
    Encapsulation of the pi cam stream
    """
    def __init__(self, src=0, width=854, height=480, alpha=2.0, beta=0, blur_ksize=3):
        """
        :param src: camera-path (Index oder Pfad)
        :param width: width of the output
        :param height: hight of the output
        :param alpha: contrast
        :param beta: lightnest
        :param blur_ksize: blursize
        """
        self.src = src
        self.width = width
        self.height = height
        self.alpha = alpha
        self.beta = beta
        self.blur_ksize = blur_ksize
        self.vc = None

    def open(self):
        """Opens camera with the settings"""
        self.vc = cv2.VideoCapture(self.src)
        self.vc.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vc.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not self.vc.isOpened():
            raise RuntimeError(f"camera {self.src} coundnt be accessd")
        # read first frame 
        ok, frame = self.vc.read()
        if not ok:
            raise RuntimeError("first camera access failed")
        

    def release(self):
        """Release camera """
        if self.vc:
            self.vc.release()
            self.vc = None

    def _process_frame(self, frame):
        """
        Convert the input image to grayscale, enhance contrast, and reduce noise.
        :param frame: Input image (BGR or grayscale)
        :return: Processed image (grayscale, denoised)
        """
        # Adjust contrast and brightness
        contrast = cv2.convertScaleAbs(frame, alpha=self.alpha, beta=self.beta)

        # Check if the image is already in grayscale
        if contrast.ndim == 3 and contrast.shape[2] == 3:
            # Convert to grayscale
            gray = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
        else:
            # Image is already in grayscale
            gray = contrast

        # Reduce noise using median filter
        denoised = cv2.medianBlur(gray, ksize=self.blur_ksize)

        return denoised


    def get_frame(self):
        """
        reads frame and encode it as JPEG.
        :return: (ok: bool, jpeg_bytes: bytes)
        """
        if not self.vc:
            raise RuntimeError("no camera available")
        ok, frame = self.vc.read()
        if not ok:
            return False, None
        processed = self._process_frame(frame)
        # encode as JPEG
        ok2, jpeg = cv2.imencode('.jpg', processed)
        if not ok2:
            return False, None
        return True, jpeg.tobytes()

    def frame_generator(self):
        """
        Generator for flask endpoint
        """
        try:
            while True:
                ok, jpeg = self.get_frame()
                if not ok:
                    break
                # HTTP-Multipart-Format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
        finally:
            self.release()

