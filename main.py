import os
import cv2
import numpy as np
import base64
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import cv2
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
import io
from io import BytesIO
import boto3

application = Flask(__name__)

S3_BUCKET                 = os.environ.get("elasticbeanstalk-ap-southeast-1-491953769123")
S3_KEY                    = os.environ.get("AKIAIXWN23BBYI5XQ7LQ")
S3_SECRET                 = os.environ.get("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")

# application.config.from_object("config")

s3 = boto3.client(
                "s3",
                region_name='us-east-2',
                aws_access_key_id=S3_KEY,
                aws_secret_access_key=S3_SECRET
            )

dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=S3_KEY,
                    aws_secret_access_key=S3_SECRET)

from boto3.dynamodb.conditions import Key, Attr


UPLOAD_FOLDER = os.path.basename('uploads')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@application.route("/")
def start_page():
    print("Start")
    return render_template('index.html')

@application.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']

    # Save file
    #filename = 'static/' + file.filename
    #file.save(filename)

    # Read image
    image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    images = os.listdir(f'./static/data')
    num=len(images)
    cv2.imwrite(f'./static/data/{num + 1}.jpg',image)
    file_name = f'static/data/{num + 1}.jpg'
    object_name = f'static/data/{num + 1}.jpg'

    region = "us-east-2"
    bucket = "elasticbeanstalk-ap-southeast-1-491953769123"
    folder = f"static/data"
    filename = f"{num + 1}.jpg"

    s3.upload_file(file_name,bucket,object_name) 
    url = f"https://s3.console.aws.amazon.com/s3/object/{bucket}/{folder}/{filename}?region={region}"

    #DYNAMODB
    table = dynamodb.Table('Story')
    table.put_item(
            Item={
    'link': url,
    'result': 1
        }
    )

    # Detect faces
    faces = detect_faces(image)

    if len(faces) == 0:
        faceDetected = False
        num_faces = 0
        to_send = ''
    else:
        faceDetected = True
        num_faces = len(faces)
        
        # Draw a rectangle
        for item in faces:
            draw_rectangle(image, item['rect'])
        
        # Save
        #cv2.imwrite(filename, image)
        
        # In memory
        image_content = cv2.imencode('.jpg', image)[1].tostring()
        encoded_image = base64.encodestring(image_content)
        to_send = 'data:image/jpg;base64, ' + str(encoded_image, 'utf-8')

    return render_template('index.html', faceDetected=faceDetected, num_faces=num_faces, image_to_show=to_send, init=True)

# ----------------------------------------------------------------------------------
# Detect faces using OpenCV
# ----------------------------------------------------------------------------------  
def detect_faces(img):
    '''Detect face in an image'''
    
    faces_list = []

    # Convert the test image to gray scale (opencv face detector expects gray images)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load OpenCV face detector (LBP is faster)
    face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')

    # Detect multiscale images (some images may be closer to camera than others)
    # result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

    # If not face detected, return empty list  
    if  len(faces) == 0:
        return faces_list
    
    for i in range(0, len(faces)):
        (x, y, w, h) = faces[i]
        face_dict = {}
        face_dict['face'] = gray[y:y + w, x:x + h]
        face_dict['rect'] = faces[i]
        faces_list.append(face_dict)

    # Return the face image area and the face rectangle
    return faces_list
# ----------------------------------------------------------------------------------
# Draw rectangle on image
# according to given (x, y) coordinates and given width and heigh
# ----------------------------------------------------------------------------------
def draw_rectangle(img, rect):
    '''Draw a rectangle on the image'''
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

if __name__ == "__main__":
    application.debug = True
    myPort = int(os.environ.get('PORT', 80))
    application.run(host='0.0.0.0', port=myPort, debug=True)