import pytube
import config
import uyts
import uuid

def onprogress(chunk, fh, br):
    fh.write(chunk)
    print(f"{br} bytes is remaining")

def import_track(author, track):
    id = uuid.uuid4().hex

    name = (author + " - " + track).lower()

    print(name)
    
    s = uyts.Search(name)
    
    url = pytube.YouTube(f"www.youtube.com/watch?v={s.results[0].ToJSON()['id']}")

    stream = 0
    abr = 0
    for el in url.streams:
        if el.mime_type == "audio/mp4":    
            if int(el.abr.replace("kbps", "")) > abr:
                stream = el.itag
                abr = int(el.abr.replace("kbps", ""))
    print("downloading") 
    st = url.streams.get_by_itag(stream)
    st.on_progress = onprogress
    st.download(config.PATH + "/download", filename=id+".mp3")
    print("downloaded")
    return id
    