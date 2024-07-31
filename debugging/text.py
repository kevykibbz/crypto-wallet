from pdf2image import convert_from_path
import os

def save_images_from_pdf(pdf_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    image_paths = []
    for page_num, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    
    return image_paths

# Example usage
pdf_file = '../docs/m0.pdf'
output_folder = 'images'

# Convert PDF to images and save them
image_paths = save_images_from_pdf(pdf_file, output_folder)

# Print the paths of the saved images
for image_path in image_paths:
    print(f"Saved image: {image_path}")