import os
#from urllib import response
import boto3
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

url = ''

def extract_payslip(url3):

    try:
        apiKey = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=apiKey)

        # Upload a PDF we will reference in the variables
        prompt = '''
        # Identity
        You are a bank credit officer assistant that extracts information from customer salary or wage payslip to determine their eligibility for credit by extracting relevant information from monthly payslip
        # Instructions
        * Extract only following data from payslip attached in the image 
        -  Employee name, name of employer, Monthly Net Pay, salary payment date, tax amount, Gross pay, national Id,
        paylsip number 
        *The output must be JSON format  {"employee_name": "TIMI EMMANUEL", 
        "employer_name": "ABC Nigeria Limited", "net_monthly_pay": "1300", 
        "gross_pay": "2000", "tax_amount": "100",  "payslip_date": "20-01-2025",
        "payslip_number" "77", "national_id" : "NG0000"}
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

