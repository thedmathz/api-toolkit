import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.config import settings

router = APIRouter()

class MessageRequest(BaseModel):
    number      : str
    message     : str
    apikey      : str
    sendername  : str


'''
Expected JSON:
{
    "number"    : '+639123456789',  # comma separate if multiple
    "message"   : "", # the message
    "apikey"    : "", # this is not semaphore api key
}
'''
@router.post("/")
async def index(payload: MessageRequest):
    
    # invalid api key
    if settings.SMS_API_KEY != payload.apikey:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # has no message
    if not payload.message:
        raise HTTPException(status_code=401, detail="Invalid SMS message")
 
    # has no message
    if not payload.number:
        raise HTTPException(status_code=401, detail="Invalid receiver number")

    # has no sender id
    if not payload.number:
        raise HTTPException(status_code=401, detail="Invalid sender id")
    
    url     = "https://api.semaphore.co/api/v4/messages"
    data    = {
        "apikey"        : settings.SMS_SEMAPHORE_API_KEY, 
        "number"        : payload.number, 
        "message"       : payload.message, 
        "sendername"    : payload.sendername, 
    }
    
    response = requests.post(url, json=data)
    print(response.json())  
    
    return JSONResponse(content={ "status": "success" })
