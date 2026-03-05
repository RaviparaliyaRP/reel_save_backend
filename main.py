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

@app.get("/get-audio")
def get_audio(url: str = Query(..., description="Instagram Reel URL for Audio"), format: str = Query(None)):
    try:
        clean_url = url.split("?")[0]
        
        ydl_opts = {
            'quiet': True,
            'format': format if format else 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # For audio, we look for formats with no video (vcodec='none')
            audio_url = None
            if 'formats' in info:
                # filter for audio only formats
                audio_formats = [f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                if audio_formats:
                    # pick the best audio format
                    audio_url = audio_formats[-1].get('url')
            
            if not audio_url:
                audio_url = info.get('url')
                
            thumbnail_url = info.get('thumbnail')
            title = info.get('title', f"Audio_{int(time.time()*1000)}")
            
            if not audio_url:
                return JSONResponse(status_code=400, content={"error": "Could not extract audio url"})
                
            return {
                "audio_url": audio_url,
                "thumbnail_url": thumbnail_url,
                "title": title
            }
            
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/get-reel")
def get_reel(url: str = Query(..., description="Instagram Reel URL"), format: str = Query(None)):
    try:
        # Clean it by removing everything after "?" symbol
        clean_url = url.split("?")[0]
        
        ydl_opts = {
            'quiet': True,
            'format': format if format else 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract-info only
            info = ydl.extract_info(clean_url, download=False)
            
            # extract direct video URL from "url" or "formats"
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = info.get('formats', [])
                
                # First, try to find a format that has both video and audio
                for f in reversed(formats):
                    vcodec = f.get('vcodec')
                    acodec = f.get('acodec')
                    if vcodec and vcodec != 'none' and acodec and acodec != 'none':
                        video_url = f.get('url')
                        break
                        
                # Fallback to any format with video if no combined stream is found
                if not video_url:
                    for f in reversed(formats):
                        if f.get('vcodec') and f.get('vcodec') != 'none':
                            video_url = f.get('url')
                            break
                
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
