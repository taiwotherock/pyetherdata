from ast import And
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from etherblockdata import fetchTransaction
from extract_bank_statement import extract_statement
from extract_payslip import extract_payslip
import json

from dotenv import load_dotenv
import os
load_dotenv()


# --------------------------
# Configuration
# --------------------------
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
#SOURCE_CODE = os.getenv("X_SOURCE_CODE")

# --------------------------
# FastAPI setup
# --------------------------

app = FastAPI(
    title="EVM Transaction History",
    description="EVM Transaction History",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Request body model
# --------------------------
class FetchWalletDataRequest(BaseModel):
    walletAddress: str   # Wallet Public Address
    chainEndpoint: str  # optional: Chain

class DocumentUploadRequest(BaseModel):
    docUrl: str   #  Document Url
    docType: str  # document Type



# --------------------------
# API Route to fetch wallet transaction onchain by address
# --------------------------
@app.post("/fetch-transaction-status")
def fetchTransactionEntry(
    req: FetchWalletDataRequest,
     x_client_id: str = Header(..., alias="x-client-id"),
    x_client_secret: str = Header(..., alias="x-client-secret")
):
    # Check authorization
    #if not authorization or authorization != f"Bearer {API_TOKEN}":
     #   raise HTTPException(status_code=401, detail="Unauthorized")
    x_source_code: Optional[str] = Header(None, alias="x-source-code")
    #x_client_id: Optional[str] = Header(None, alias="x-client-id")
    #x_client_secret: Optional[str] = Header(None, alias="x-client-secret")

    wa = req.walletAddress
    chain = req.chainEndpoint
    print(x_client_id) 
    print( CLIENT_ID)
    print( 'chain: ' + chain)
    print( 'wa: ' + wa)
    #print(x_client_secret + " " + CLIENT_SECRET)

    #if x_client_id != CLIENT_ID or x_client_secret != CLIENT_SECRET :
    #   return {"data": "ERROR: DENIED"}

    try:

        result =  fetchTransaction(wa,chain)
       
        return {"data": result}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/document-extractor")
def documentExtractor(
    req: DocumentUploadRequest,
     x_client_id: str = Header(..., alias="x-client-id"),
    x_client_secret: str = Header(..., alias="x-client-secret")
):
    # Check authorization
    #if not authorization or authorization != f"Bearer {API_TOKEN}":
     #   raise HTTPException(status_code=401, detail="Unauthorized")
    x_source_code: Optional[str] = Header(None, alias="x-source-code")
    #x_client_id: Optional[str] = Header(None, alias="x-client-id")
    #x_client_secret: Optional[str] = Header(None, alias="x-client-secret")

    docUrl = req.docUrl
    docType = req.docType
    print(docUrl) 
    print( docType)
    

    try:

        result =''
        if docType == 'BANK_STATEMENT':
             result = extract_statement(docUrl)
        elif docType == 'PAY_SLIP':
            print('payslip')
            result = extract_payslip(docUrl)
    
       
        try:
            # Convert string to JSON safely
            extracted_json = json.loads(result)
        except Exception:
            return {"error": "Invalid JSON returned from extractor", "raw": result}

        return extracted_json
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)