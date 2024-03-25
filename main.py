from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import app.Routers.chatbot as chatbot
import app.Routers.reply_sms as reply_sms

import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI().include_router() method is used to include routes delcared in other files in the golbal route handler.
app.include_router(chatbot.router, tags=["chatbot"])
app.include_router(reply_sms.router, tags=["reply"])

app.mount("/static", StaticFiles(directory="./data"), name="static")

# define the route:
@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello World"}

# define the entry point. In the entry point, using uvicorn to run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6000, reload=True)