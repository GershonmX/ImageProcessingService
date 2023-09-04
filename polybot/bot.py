import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img
import boto3
import requests


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.processing_completed = True

    def handle_message(self, msg):
        if not self.processing_completed:
            logger.info("Previous message processing is not completed. Ignoring current message.")
            return

        if "photo" in msg:
            # If the message contains a photo, check if it also has a caption
            if "caption" in msg:
                caption = msg["caption"].lower()
                # Check for different processing methods in the caption
                if 'blur' in caption:
                    self.process_image_blur(msg)
                elif 'contour' in caption:
                    self.process_image_contour(msg)
                elif 'rotate' in caption:
                    self.process_image_rotate(msg)
                elif 'segment' in caption:
                    self.process_image_segment(msg)
                elif 'salt and pepper' in caption:
                    self.process_image_salt_and_pepper(msg)
                elif 'concat' in caption:
                    self.process_image_concat(msg)
                else:
                    self.send_text(msg['chat']['id'],
                                   "Unknown processing method. Please provide a valid method in the caption.")

            else:
                logger.info("Received photo without a caption.")
        elif "text" in msg:
            super().handle_message(msg)  # Call the parent class method to handle text messages

    def process_image(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)
        another_image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)
        another_image = Img(another_image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.concat(another_image)  # Concatenate the two images

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True

    def process_image_contur(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.contour()  # contur the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True

    def process_image_rotate(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.rotate()  # rotate the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True

    def process_image_blur(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.blur()  # blur the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True


    def process_image_contour(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.contour()  # contour the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True

    def process_image_segment(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.segment()  # segment the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True

    def process_image_salt_and_pepper(self, msg):
        self.processing_completed = False

        # Download the two photos sent by the user
        image_path = self.download_user_photo(msg)

        # Create two different Img objects from the downloaded images
        image = Img(image_path)

        # Process the image using your custom methods (e.g., apply filter)
        image.salt_and_pepper()  # salt_and_pepper the image

        # Save the processed image to the specified folder
        processed_image_path = image.save_img()

        if processed_image_path is not None:
            # Send the processed image back to the user
            self.send_photo(msg['chat']['id'], processed_image_path)

        self.processing_completed = True


    def process_image_concat(self, msg):
        pass
        
        
# class ObjectDetectionBot(Bot):
#    def handle_message(self, msg):
#        logger.info(f'Incoming message: {msg}')
#
#       if self.is_current_msg_photo(msg):
#            photo_path = self.download_user_photo(msg)
#
#           # Task 1: Upload the Photo to S3
#            # Replace 'your-access-key', 'your-secret-key', 'your-bucket-name', and 'your-object-key' with your S3 credentials and desired locations.
#            s3 = boto3.client('s3', aws_access_key_id='your-access-key', aws_secret_access_key='your-secret-key')
#            s3.upload_file(photo_path, 'your-bucket-name', 'your-object-key')
#
#            # Task 2: Send a Request to the `yolo5` Service for Prediction
#            # Replace 'yolo5-service-url' with the actual URL or endpoint of the `yolo5` service.
#            yolo5_service_url = 'yolo5-service-url'
#            with open(photo_path, 'rb') as photo_file:
#               files = {'photo': (photo_path, photo_file)}
#                response = requests.post(yolo5_service_url, files=files)
#
#            # Task 3: Send Results to the Telegram End-User
#            if response.status_code == 200:
#                detected_objects = response.json()  # Assuming the response contains detected object data.
#                # Process and format the detected_objects as needed.
#
#               # Send the formatted results back to the Telegram end-user.
#                self.send_text(msg['chat']['id'], f'Detected Objects: {detected_objects}')
#            else:
#                self.send_text(msg['chat']['id'], 'Object detection service error.')
#
#        # Example usage:
#        # object_detection_bot = ObjectDetectionBot(token='your-bot-token', telegram_chat_url='your-telegram-chat-url')
#
#            # TODO upload the photo to S3
#            # TODO send a request to the `yolo5` service for prediction
#            # TODO send results to the Telegram end-user
