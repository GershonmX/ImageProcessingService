from img_proc import Img

input_image_path = '/home/gershonx/ImageProcessingService/ImageProcessingService/polybot/test/beatles.jpeg'
my_img = Img(input_image_path)
# Rotate the image
my_img.rotate()
#my_img.rotate()
my_img.save_img()
