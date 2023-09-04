import time
from pathlib import Path
from flask import Flask, request
from detect import run
import uuid
import yaml
from loguru import logger
import os
import boto3
from pymongo import MongoClient
import subprocess

# Load environment variable
images_bucket = os.environ['BUCKET_NAME']

# Initialize S3 client
s3 = boto3.client('s3')

# Initialize the MongoDB client (replace with your MongoDB connection details)
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['mongosh'] #your_database_name
collection = db['myReplicaSet'] #your_collection_name

# Load object detection model class names from coco128.yaml
with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

# Initialize Flask app
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Generates a UUID for this current prediction HTTP request. This id can be used as a reference in logs to
    # identify and track individual prediction requests.
    prediction_id = str(uuid.uuid4())

    logger.info(f'prediction: {prediction_id}. start processing')

    # Receives a URL parameter representing the image to download from S3
    img_name = request.args.get('imgName')

    # TODO download img_name from S3, store the local image path in original_img_path
    # Specify the key (path) of the image within the bucket
    filename = img_name.split('/')[-1]
    local_dir = 'photos/'
    os.makedirs(local_dir, exist_ok=True)
    original_img_path = local_dir + filename
    s3.download_file(images_bucket, img_name, original_img_path)

    # Download the image from S3 to a local directory
    local_image_path = f'temporary_folder/{img_name}'  # Update the path accordingly
    s3.download_file(images_bucket, s3_image_key, local_image_path)

    logger.info(f'prediction id: {prediction_id}, path: \"{original_img_path}\" Download img completed')

    # Predicts the objects in the image
    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=local_image_path,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction: {prediction_id}, path: {original_img_path}. done')

    # This is the path for the predicted image with labels
    predicted_img_path = Path(f'static/data/{prediction_id}/{filename}')

    # TODO Uploads the predicted image (predicted_img_path) to S3 (be careful not to override the original image).
    predicted_img_path = Path(f'static/data/{prediction_id}/{filename}')
    predicted_img_name = f'predicted_{filename}'
    os.rename(f'/usr/src/app/static/data/{prediction_id}/{filename}',
              f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}')
    s3_path_to_upload_to = '/'.join(img_name.split('/')[:-1]) + f'/{predicted_img_name}'
    file_to_upload = f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}'
    s3.upload_file(file_to_upload, images_bucket, s3_path_to_upload_to)
    os.rename(f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}',
              f'/usr/src/app/static/data/{prediction_id}/{filename}')

    logger.info(f'prediction: {prediction_id}/{local_image_path}. Image uploaded to S3.')

    # Parse prediction labels and create a summary
    pared_summary_path = Path(f'static/data/{prediction_id}/labels/{original_img_path.split(".")[0]}.txt')
    if pared_summary_path.exists():
        with open(pared_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': local_image_path,
            'predicted_img_path': predicted_img_path,
            'labels': labels,
            'time': time.time()
        }

        # TODO store the prediction_summary in MongoDB
        collection.insert_one(prediction_summary)

        return prediction_summary
    else:
        return f'prediction: {prediction_id}/{local_image_path}. prediction result not found', 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
