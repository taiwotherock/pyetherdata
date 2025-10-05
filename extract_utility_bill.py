import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def extract_utility_bill(url3: str):
    """
    Extracts structured information from a Nigerian utility bill image/PDF.
    Returns JSON text with key fields for credit assessment.
    """

    try:
        apiKey = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=apiKey)

        # Prompt engineering for Utility Bill
        prompt = '''
        # Identity
        You are a bank credit officer assistant that extracts information 
        from Nigerian customer utility bills (electricity, water, waste, telecom) 
        to verify address, identity, and bill payment history for credit eligibility.

        # Instructions
        * Extract ONLY the following fields from the utility bill attached in the image:
          - customer_name
          - address
          - utility_provider
          - account_number (or meter number / reference number)
          - bill_number
          - issue_date
          - due_date
          - amount_due
          - amount_paid
          - payment_status (e.g. "Paid", "Unpaid", "Partially Paid")

        * The output must be in strict JSON format, e.g.:

        {
          "customer_name": "JOHN DOE",
          "address": "12 Adekunle Street, Ikeja, Lagos, Nigeria",
          "utility_provider": "Ikeja Electric",
          "account_number": "1234567890",
          "bill_number": "BILL-2025-01",
          "issue_date": "01-01-2025",
          "due_date": "31-01-2025",
          "amount_due": "20000",
          "amount_paid": "15000",
          "payment_status": "Partially Paid"
        }

        *Output must be ONLY valid JSON (no text outside the JSON object).
        '''

        # Call GPT model
        response = client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": url3}
                    ]
                }
            ]
        )

        output_text = response.output_text.strip()
        print(output_text)
        return output_text  # return raw JSON string

    except Exception as e:
        print("Error extracting utility bill:", e)
        return ""
