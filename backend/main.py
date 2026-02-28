from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yt_dlp
import traceback
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-reel")
def get_reel(url: str = Query(..., description="Instagram Reel URL")):
    try:
        # Clean it by removing everything after "?" symbol
        clean_url = url.split("?")[0]
        
        ydl_opts = {
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract-info only
            info = ydl.extract_info(clean_url, download=False)
            
            # extract direct video URL from "url" or "formats"
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('vcodec') != 'none':
                        video_url = f.get('url')
                        break
                if not video_url and formats:
                    video_url = formats[-1].get('url')
                
            thumbnail_url = info.get('thumbnail')
            title = info.get('title', f"Reel_{int(time.time()*1000)}")
            
            if not video_url:
                return JSONResponse(status_code=400, content={"error": "Could not extract video url"})
                
            return {
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "title": title
            }
            
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
