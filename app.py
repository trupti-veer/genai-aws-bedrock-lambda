import boto3
import botocore.config
import json
from datetime import datetime

def generate_blog_using_bedrock(blog_topic: str) -> str:
    prompt = f""" <s>[INST] Human: Write a 200 words blog on the topic {blog_topic}
    Assistant: [/INST]
    """

    body = {
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 50
    }

    #Model used for blog generation is Mistral-8-7B-Instruct Model
    try:
        bedrock = boto3.client("bedrock-runtime", region_name = "us-east-1", 
                               config = botocore.config.Config(read_timeout=300, retries={'max_attempts':3}))
        response = bedrock.invoke_model(body = json.dumps(body), modelId="mistral.mixtral-8x7b-instruct-v0:1")
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog : {e}")
        return ""

#Save the generated blog to S3 bucket.
def save_blog_to_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_blog)
    except Exception as e:
        print("Failed to save blog output")

#Lambda function
def lambda_handler(event, context):    
    event = json.loads(event['body'])
    blog_topic = event['blog_topic']
    blog = generate_blog_using_bedrock(blog_topic=blog_topic)

    if blog:
        current_time = datetime().now.strftime("%H%M%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'genai-aws-bedrock'
        save_blog_to_s3(s3_key, s3_bucket, blog)
    else:
        print("No blog was generated")
  

    return {
        "statusCode": 200,
        "body": json.dumps("Blog generation is complete")
    }

