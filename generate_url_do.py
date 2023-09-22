import boto3, botocore
import os

access_key_id = os.environ['do_key_id']
secret_access_key = os.environ['do_access_secret']

# Upload the downloaded file to S3
s3 = boto3.client(
  's3',
  region_name="us-east-1",
  aws_access_key_id=access_key_id,
  config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
  # region_name='nyc3',
  endpoint_url='https://nyc3.digitaloceanspaces.com',
  aws_secret_access_key=secret_access_key)


def generate_pre_signed_url_do(file_key, bucket="videos-bein"):
  try:
    url = s3.generate_presigned_url('get_object',
                                    Params={
                                      'Bucket': bucket,
                                      'Key': file_key
                                    },
                                    ExpiresIn=60 * 60 * 4)
    return url
  except:
    return None
