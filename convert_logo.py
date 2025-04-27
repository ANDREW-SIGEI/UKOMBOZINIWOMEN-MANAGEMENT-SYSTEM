import os
from pdf2image import convert_from_path

# Set paths
input_pdf = 'ukombozini_products/logo kombozini(1).pdf'
output_dir = 'static/images/'
output_file = os.path.join(output_dir, 'ukombozi-logo.png')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    # Convert the first page of the PDF to an image
    pages = convert_from_path(input_pdf, 300, first_page=1, last_page=1)
    
    # Save the first page as PNG
    if pages:
        pages[0].save(output_file, 'PNG')
        print(f"Successfully converted {input_pdf} to {output_file}")
    else:
        print("No pages found in the PDF.")
except Exception as e:
    print(f"Error converting PDF: {e}")
    
    # Manual fallback - create a simple text-based logo
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image with a green background
        img = Image.new('RGB', (400, 100), color=(46, 125, 50))
        d = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
            
        # Draw the text
        d.text((50, 35), "Ukombozi Women", fill=(255, 255, 255), font=font)
        
        # Save the image
        img.save(output_file)
        print(f"Created fallback logo at {output_file}")
    except Exception as e2:
        print(f"Error creating fallback logo: {e2}") 