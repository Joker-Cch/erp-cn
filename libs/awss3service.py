from botocore.exceptions import ClientError
from libs.awsclient import awsclient


def awsS3PresignUrlUpload(ak, sk, region, bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    s3_client = awsclient("s3", ak, sk, region)
    print(fields)
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
        return response
    except ClientError as e:
        print(e)
        return None

def awsS3PresignUrlDownload(ak, sk, region, bucket_name, object_name,expiration= 3600):
    try:
        s3_client  = awsclient("s3", ak, sk, region)
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        return response

    except Exception as e:
        print(e)
        return None