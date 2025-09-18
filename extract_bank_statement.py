import os
import json
#from urllib import response
import boto3
from PIL import Image
import requests
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

url = ''

def upload_file(filename):

    # Let's use Amazon S3
    s3 = boto3.resource('s3')
    
    s3_client = boto3.client("s3") 
    # Print out bucket names
    for bucket in s3.buckets.all():
        print('bucket: ' + bucket.name)

    # Upload a new file
    try:
        with open('images/' + filename, 'rb') as data:
            s3.Bucket('mmcpdocs').put_object(Key=filename, Body=data)
        
        url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": 'mmcpdocs', "Key": filename},
        ExpiresIn=3600
        )

        print("S3 presigned URL:", url)
    except Exception as e:
        print(e)
        
    return url


#url2 = upload_file('Bank_statement.png')

def extract_statement(url3):

    try:
        apiKey = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=apiKey)

        # Upload a PDF we will reference in the variables
        prompt = '''
        # Identity
        You are a bank credit officer assistant that extracts information from customer bank statement to determine their eligibility for credit by extracting relevant information from bank statement
        # Instructions
        * Extract only following data from bank statement attached in the image - Account No, Account Name, Address of account holder, opening balance, closing balance, total count and amount  of depoisit or credit, total count and amount of withdrawal or debit
        * Extract salary, wage, income payment and provide count and total amount
        *Extract highest and lowest deposit or credit
        *Extract Start date and end date 
        *The output must be JSON format  {“account_no”: ”0000000”, “account_name”: “Ojo Taiwo”, “address”: “100 Lagos Road,Ikeja,Lagos,Nigeria”, 
        “opening_bal”: 2000, “closing_bal”: 5000,  “total_deposit_amount”: 60000, “total_deposit_count”: 6,  “total_withdrawal_amount”: 60000, 
        “total_withdrawal_count”: 6,  “total_salary_or_wage”: 60000, “highest_salary_or_wage”:  6000, “lowest_salary_or_wage”:  1000, “start_date” : “01-01-2000”,
        “end_date” : “03-12-2020”  }
        *Output must be JSON only
        '''

        response = client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {
                            "type": "input_image",
                            "image_url": url3
                        }
                    ]
                }
            ]
        )

        print(response.output_text)
        return response.output_text  
    except Exception as e:
        print(e)

    return ""

