from twilio.twiml.messaging_response import MessagingResponse
from fastapi import APIRouter, Form, Request, Response
from app.Utils.extract_text import complete_text

router = APIRouter()
@router.post("/reply_sms")
async def reply_sms(request: Request):
    # Parse the form data from Twilio
    form_data = await request.form()
    body = form_data.get('Body', None)
    print(body)
    
    # openai_result = await complete_text(body)    
    # Start our TwiML response
    resp = MessagingResponse()
        
    # Determine the right reply for this message
    # if body == 'hello':
    #     resp.message("Hi!")
    # elif body == 'bye':
    #     resp.message("Goodbye")
    # else :
    #     resp.message("Dear Client.")
    resp.message(body)
    print(str(resp))
    # Convert the Twilio response to a string and return it
    return Response(content=str(resp), media_type="application/xml")