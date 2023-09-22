from fastapi import FastAPI, HTTPException
from sqlitedict import SqliteDict
import generate_url_do as do
import requests
import json
from pydantic import BaseModel

app = FastAPI()
db = SqliteDict('videos.db', autocommit=True)
DEFAULT_QUALITY_FOR_VIMEO = 360
DEFAULT_QUALITY_FOR_VIMEO_LESS = True  # true = less || false = or more
debug_with_lite_videos = False


@app.get("/")
async def root():
  return {"message": "Hello world"}


@app.get("/name/{name}")
async def name(name: str):
  return {"message": f"Hello {name}"}


use_vimeo = False
use_do = True


@app.get("/video/{video_id}")
async def get_video(video_id: int):
  global debug_with_lite_videos
  if (debug_with_lite_videos):
    return {
      "link":
      "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
      "other_links": {
        "720":
        "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
        "1080":
        "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4"
      }
    }
  if use_vimeo:
    rsp = requests.get(f'https://player.vimeo.com/video/{video_id}/config')
    if rsp.status_code != 200:
      raise HTTPException(status_code=404, detail="Item not found")
    rsp_json = json.loads(rsp.text)
    prog = rsp_json['request']['files']["progressive"]
    qualities = {}
    choosen_default_quality = 0
    for i, d in enumerate(prog):
      if choosen_default_quality == 0:
        choosen_default_quality = d["height"]
      if d["height"] == DEFAULT_QUALITY_FOR_VIMEO:
        choosen_default_quality = d["height"]
      if choosen_default_quality != DEFAULT_QUALITY_FOR_VIMEO:
        if DEFAULT_QUALITY_FOR_VIMEO_LESS:
          if d["height"] < DEFAULT_QUALITY_FOR_VIMEO and d[
              "height"] > choosen_default_quality:
            choosen_default_quality = d["height"]
        else:
          if d["height"] > DEFAULT_QUALITY_FOR_VIMEO and d[
              "height"] < choosen_default_quality:
            choosen_default_quality = d["height"]
      qualities[d["height"]] = d["url"]
    return {
      "link": qualities[choosen_default_quality],
      "other_links": qualities
    }
  elif use_do:
    if list(db.keys()).__contains__(f"{video_id}"):
      urls_result = {}
      lll = ""
      for quality in list(db.keys()):
        lll = do.generate_pre_signed_url_do(db[quality])
        urls_result[quality] = lll
      return {"link": lll, "other_links": urls_result}
    url = do.generate_pre_signed_url_do(f"{video_id}.mp4")
    return {"link": url, "other_links": {"360": url}}
  else:
    if str(video_id) in db:
      link = db[str(video_id)]
      return {"link": f"{link}"}
    else:
      return {
        "link":
        "https://d1skfs7pstim74.cloudfront.net/CEPHALOSPORINS AND REST OF BETA-LACTAM ANTIBIOTICS_AgADzA4AAimWKFM.mp4"
      }


class VideoData(BaseModel):
  video_id: int
  links: dict


@app.post("/video")
async def add_video(video_data: VideoData):
  db[str(video_data.video_id)] = video_data.links
  return {
    "message":
    f"Video with ID {video_data.video_id} associated with the links: {video_data.links}"
  }
