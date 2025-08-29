# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
import os

app = FastAPI(title="TechVJ Bot API", version="1.0")

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "TechVJ"

# Optional: health check endpoint
@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
