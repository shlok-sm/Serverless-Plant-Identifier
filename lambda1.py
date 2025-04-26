import json
import urllib.parse
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = ' '  #enter your bucket name

    # Parse query string param: ?filename=xyz
    params = event.get("queryStringParameters") or {}
    filename = params.get("filename")

    if not filename:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing filename"})
        }

    # Encode the filename to make it URL-safe
    key = f"uploads/{urllib.parse.quote(filename)}"

    # Generate the presigned URL with a 5-minute expiration
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ContentType": 'image/webp'  #currently accepting only webp type image 

        },
        ExpiresIn=300
    )

    # Return the URL along with CORS headers for frontend access
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # CORS header to allow requests from any domain
            "Access-Control-Allow-Methods": "GET, POST, PUT",  # Allow PUT method for file upload
            "Content-Type": "application/json"
        },
        "body": json.dumps({"url": url})
    }
