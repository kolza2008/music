import os.path
import pytube
import config
import uyts
import uuid

def onprogress(chunk, fh, br):
    fh.write(chunk)
    print(f"{br} bytes is remaining")

def import_track(author, track, filename=None):
    id = uuid.uuid4().hex

    name = (author + " - " + track).lower()

    print(name)
    
    s = uyts.Search(name)
    
    url = pytube.YouTube(f"www.youtube.com/watch?v={s.results[0].ToJSON()['id']}")

    if filename is None and os.path.exists(os.path.join(config.PATH + "/download", id+".mp3")):
        return id
    elif filename is not None and os.path.exists(config.PATH + "/download", filename+".mp3"):
        return filename

    stream = 0
    abr = 0
    for el in url.streams:
        if el.mime_type == "audio/mp4":    
            if int(el.abr.replace("kbps", "")) > abr:
                stream = el.itag
                abr = int(el.abr.replace("kbps", ""))
    st = url.streams.get_by_itag(stream)
    st.on_progress = onprogress
    if filename is None:
        st.download(config.PATH + "/download", filename=id+".mp3")
        return id
    else:
        st.download(config.PATH + "/download", filename=filename+".mp3")
        return filename
    