import vimeo, codecs, json, requests, os
from datetime import datetime
from vimeo_downloader import Vimeo
from dotenv import load_dotenv


load_dotenv()
client = vimeo.VimeoClient(
         token=os.environ.get("VIMEO_ACCESS_TOKEN"), 
         key=os.environ.get("VIMEO_CLIENT_ID"), 
         secret=os.environ.get("VIMEO_CLIENT_SECRET"))

subs_dir = "subtitles"

def getVideoMetadata(page):
    '''
    Dowloads the metadata of videos from vimeo
    '''
    
    url = "https://api.vimeo.com/me/videos?direction=desc&page=" + str(page)      #Note: asc="old to new",  desc="new to old" 
    resp = client.get(url)
    if resp.status_code == 200:
       return resp.json()['data'], resp.json()["paging"]["next"]
    else:
       return None
       
       
def editVideo(video_id, download):
    '''
    Edits the downlaod settings of a vimeo video
    '''
    url = "https://api.vimeo.com/videos/" + video_id 
    headers = {'content-type': 'application/json'}
    data = {"privacy": {"download": download}}
    resp = client.patch(url, data=data, headers=headers)
    
    if resp.status_code == 200:
       return True
    else:
       return None
             

def downloadVideo(video_id):
    '''
    Downloads a vimeo video
    '''
    file_name = "videos/" + video_id + ".mp4"
    if os.path.isfile(file_name):
       pass
    else:
       accepted_vid_link = "https://vimeo.com/" + video_id
       v = Vimeo(accepted_vid_link)
       try:
          s = v.streams
          smallest_stream = s[0]
          smallest_stream.download(download_directory='videos', filename=video_id)
       except: 
          return None
    return file_name
    
    
def generateAutoSubs(video_id):
    '''
    If a given vimeo does not have subtitles, this functions automatically generates subtitles.
    '''
    
    try:
       video_file_name = downloadVideo(video_id)
       if video_file_name is not None:
          os.chdir("AutoSub")
          command = "autosub/main.py --file " + "../" + video_file_name +  " --format srt"
          os.system(command)
          os.chdir("../")
          generated_file = subs_dir + "/" + video_id + ".en.vtt"
          os.rename("AutoSub/output/" + video_id + ".srt", generated_file) #rename file to vtt, and move it to the subitiles folder vimeo only accepts vtt.
          return generated_file
       else:
          return None
    except:
       return None



def getTags(video_id):
    '''
    Downloads all tags from a given vimeo video.
    '''

    url = "https://api.vimeo.com/videos/" + video_id + "/tags"
    resp = client.get(url)
    if resp.status_code == 200:
       tags = resp.json()["data"]
       tags = [tag["name"] for tag in tags]  
       return tags
    else:
       print (resp.text)
       return None
    

def writeTags(video_id, tags):
    '''
    Writes tags to a vimeo video.
    '''
    
    url = "https://api.vimeo.com/videos/" + video_id + "/tags"
    headers = {'content-type': 'application/json'}
    data = json.dumps([{"name": tag} for tag in tags])
    resp = client.put(url, data=data, headers=headers)
    if resp.status_code == 200:
       return True
    else:
       print (resp.text)
       return None
       

def getSubs(video_id):
    '''
    Downloads subtitles from a given vimeo video.
    '''

    url = "https://api.vimeo.com/videos/" + video_id + "/texttracks"
    resp = client.get(url)
    if resp.status_code == 200:
       subs = resp.json()["data"]
       return subs
    else:
       print (resp.text)
       return None
       
       
def writeSubs(video_id, subs_file):
    '''
    Writes subtitles file to a vimeo video.
    '''
    
    url = "https://api.vimeo.com/videos/" + video_id + "/texttracks"
    data = json.dumps({"active": True, "language":"en", "type": "captions", "name": video_id + ".en.vtt"})
    header = {'Authorization': 'bearer d3c6e8c1bcdbbecfe45053c231ca14f8', 'content-type': 'application/json','Accept': 'application/vnd.vimeo.*+json;version=3.4' }
    resp = client.post(url, data=data, headers=header)
    if resp.status_code == 201:
       upload_link =  resp.json()['link']
       header = {'Accept': 'application/vnd.vimeo.*+json;version=3.4'}
       with codecs.open(subs_file, encoding='utf-8',mode='r') as inputFile:
            data = inputFile.read()
       resp = client.put(upload_link, data=data, headers=header)
       return True
    else:
       print (resp.text)
       return None
       

def formatDate(dateString):
    '''
    Formats a given string to a proper date-time object
    '''
    
    dateString =  dateString.split("T")[0].replace("-","/")
    date = datetime.strptime(dateString, "%Y/%m/%d")
    monthYear = date.strftime("%B %Y").split()
    return monthYear[0], monthYear[1]
    
    
class Queue:
     def __init__(self, length):
         self.queue = ['0000'] * 3
         
     def isEmpty(self) -> bool:
         return True if len(self.queue) == 0 else False
         

     def enqueue(self, x):
         self.queue.pop()
         self.queue.insert(0, x)       

         
