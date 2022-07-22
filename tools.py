'''
This version approaches the probles as an information retrieval problem. Returning video links that match any search query
tips:
#if a property is not set as stored, then you can not retrieve it as a result i.e. the document will be retrived but that property won't show.
'''

import codecs, os, json, requests, re, dotenv
import vimeo_utils as vimeo
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.highlight import UppercaseFormatter 


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv()
punctuations = """!"#$%&()*+,-—*/.“'’`<=>?@\^_”:;{|}~"""
output_file = "output.csv"
sub_pattern = "[0-9]{2}:[0-9]{2}:[0-9]{2}"
subs_dir = "subtitles"
logs_file = "logs.txt"
queue = vimeo.Queue(3)  

def logError(message):
    with codecs.open(logs_file, encoding='utf-8', mode='a') as logFile:
         logFile.write(message)


def preproText(doc):
    doc = doc.lower()
    doc = ''.join([' ' if ch in punctuations else ch for ch in doc])
    doc = doc.split()
    doc = [word for word in doc if len(word) > 1]
    return " ".join(doc)
    
    
def preproSubs(file_path):
    #Preprocess subtitle file
    i=0
    text = ""
    with codecs.open(file_path, encoding='utf-8', mode='r') as inputFile:
         for line in inputFile:
             line = line.strip()
             if i==0 or not line.strip() or re.match("[0-9]+", line) or re.match(sub_pattern, line[0:10]):
                i+=1
                continue 
             else:
                 text = text + " " + line                       
    text = preproText(text)
    return text
    
   
def getSubtitles(video_id):
    subs = vimeo.getSubs(video_id)
    if subs is not None and len(subs) != 0: #if the video has subtitles
       sub_link = subs[0]["link"]
       sub_file = subs_dir + "/" + video_id + ".en.vtt" 
       if os.path.isfile(sub_file):   #if you already downloaded the subtitles
          pass
       else:  #If you didn't, then download them.
          resp = requests.get(sub_link, allow_redirects=True)
          open(sub_file, 'wb').write(resp.content)
       subtitles = preproSubs(sub_file)
       return subtitles
    else: 
         sub_file = vimeo.generateAutoSubs(video_id)
         if sub_file is not None:
            try:
                vimeo.writeSubs(video_id, sub_file)
                subtitles = preproSubs(sub_file)
                return subtitles
            except:
                message = "couldn't write subtitles to video " +  video_id + "\n"
                logError(message)
                return None
         else: 
             message = "couldn't write subtitles to video " +  video_id + "\n"
             logError(message)
             return None  
             
             
def updateIndex():

    schema = Schema(v_id=ID(unique=True), v_name=TEXT(stored=True), v_link=ID(stored=True),  v_date=TEXT(stored=True), v_text=TEXT(stored=True))
    if not os.path.exists("whoosh_index"): os.mkdir("whoosh_index")
    index = create_in("whoosh_index", schema=schema, indexname="vimeo_index") #creates an index, if already exists the existing is cleared out.
    last_indexed_vids = os.environ.get("LAST_INDEXED_VIDS").split(",") if os.environ.get("LAST_INDEXED_VIDS") is not None else []
    
    try:
         writer = index.writer()
         page = 0   
         processed = 0
         while True: 
               page += 1
               try:
                  videos, next_page = vimeo.getVideoMetadata(page)
               except:
                  message = "couldn't get links for videos on page " + str(page) + "\n"
                  logError(message)
                  continue
                  
               if videos is not None:
                  for v in videos:
                      v_id =  v["uri"].split("/")[-1]
                      v_name = v["name"]
                      v_link = v["link"]
                      v_date = v["created_time"]
                      
                      if v_id in last_indexed_vids:
                         processed += 1
                      if processed > 2:
                         break
                      
                      month, year = vimeo.formatDate(v_date)
                      v_date = month + " " + year
                      v_tags = v["tags"] 
                      v_tags = [tag["name"] for tag in v_tags] if v_tags is not None and len(v_tags) != 0 else  [month,year]                     
                      v_tags.extend([month, year])
                      v_tags = " ".join(list(set(v_tags)))
                      
                                   
                      v_description = v["description"] if v["description"] is not None else ""
                      try:
                         v_subtitles = getSubtitles(v_id)
                      except:
                         message = "couldn't get subitiles for videos " + str(v_id) + "\n"
                         logError(message)
                         continue
                         
                      v_subtitles = v_subtitles if v_subtitles is not None else ""
                      v_text = v_name + " " + v_tags + " " +  v_description + " "  + v_subtitles
                      v_text =  preproText(v_text) 
                      
                      try:
                         writer.add_document(v_id=v_id, v_name=v_name, v_link=v_link, v_date=v_date, v_text=v_text)
                         queue.enqueue(v_id)  
                      except:
                         message = "couldn't index video " + str(v_id) + "\n"
                         logError(message)
                         continue   
                      
                      '''
                      with codecs.open(output_file, encoding='utf-8',mode='a') as outputFile:
                           outputFile.write("%s, %s, %s \n" %(v_id, v_link, v_tags))
                      '''

                       
               if next_page is None or processed > 2 or page >= 2: break
         writer.commit()
         dotenv.set_key(dotenv_file, "LAST_INDEXED_VIDS", ",".join(queue.queue))
         return True
    except:
         writer.commit()
         dotenv.set_key(dotenv_file, "LAST_INDEXED_VIDS", ",".join(queue.queue))
         logError("End of session \n\n\n") 
         return False

    
        


def queryIndex(query):
    index = open_dir("whoosh_index", indexname="vimeo_index")
    dic = []
    with index.searcher() as searcher:
         parser = QueryParser("v_text", index.schema)
         query= parser.parse(query)
         results = searcher.search(query, terms=True)
         results.formatter = UppercaseFormatter()
         for r in results:
             dic.append({"v_name": r["v_name"], "v_link": r["v_link"], "v_date": r["v_date"], "highlights": r.highlights("v_text", top=1)})
             
    return dic


   
