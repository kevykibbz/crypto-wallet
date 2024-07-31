import cv2
import pytesseract

# Path to the image file
image_path = 'images/mo_page_1.png'

# Load the image using OpenCV
image = cv2.imread(image_path)

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply some preprocessing (if needed)
# For example, you can apply thresholding
_, threshold_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

# Alternatively, you can use other preprocessing techniques like blurring, dilation, etc.
# blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Extract text from the image using Tesseract
extracted_text = pytesseract.image_to_string(threshold_image)

# Print the extracted text
print(extracted_text)
