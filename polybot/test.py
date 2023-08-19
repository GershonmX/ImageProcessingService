from img_proc import Img
import random

if __name__ == "__main__":
    input_image_path = '/home/gershonx/ImageProcessingService/ImageProcessingService/polybot/test/beatles.jpeg'
    my_img = Img(input_image_path)

    # Create a list of available processing methods
    available_methods = ['blur', 'contour', 'rotate', 'segment', 'salt_n_pepper', 'concat']
    # Randomly choose a method from the list
    chosen_method = random.choice(available_methods)

    # Apply the chosen method
    if chosen_method == 'blur':
        my_img.blur()
    elif chosen_method == 'contour':
        my_img.contour()
    elif chosen_method == 'rotate':
        my_img.rotate()
    elif chosen_method == 'segment':
        my_img.segment(num_segments=4)
    elif chosen_method == 'salt_n_pepper':
        my_img.salt_n_pepper()
    elif chosen_method == 'concat':
        my_img.concat(my_img, direction='horizontal')

    # Save the processed image
    output_path = my_img.save_img()
    print(f"Processed image saved to: {output_path}")