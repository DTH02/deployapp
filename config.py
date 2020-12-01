import os

S3_BUCKET                 = os.environ.get("elasticbeanstalk-ap-southeast-1-491953769123")
S3_KEY                    = os.environ.get("AKIAIXWN23BBYI5XQ7LQ")
S3_SECRET                 = os.environ.get("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")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000