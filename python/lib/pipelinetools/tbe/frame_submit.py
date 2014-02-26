#import shotgun
import getpass
import subprocess
import json
import re
import os
import logging

log = logging.getLogger(__name__)

def get_media_info_ffprobe(path):
    """
    """
    cmd = ["ffprobe", "-show_streams", "-print_format", "json", path]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()

    if not p.returncode is 0:
        raise Exception("Unable to get media info from '%s':\n\t%s" % (path, output[1]))

    json_info = json.loads(output[0])
    if not json_info:
        raise Exception("Unable to get media info from '%s'. No data returned." % path)

    streams = json_info["streams"]

    media_infos = []

    for stream in streams:        
        media_info = {}
        media_info["resolution"] = (int(stream["width"]), int(stream["height"]))
        media_info["fps"] = int(stream["r_frame_rate"].split("/")[0])
        media_info["frames"] = int(stream["nb_frames"])        
        media_infos.append(media_info)

    return media_infos


def extract_image_from_movie(movie_filepath, frame, output_filepath, resolution=None, force=True):
    """
    """
    media_infos = get_media_info_ffprobe(movie_filepath)
    num_frames = media_infos[0]["frames"]
    fps = media_infos[0]["fps"]
    
    if isinstance(frame, basestring):
        frame_lower = frame.lower()
        if frame_lower == "first":
            frame = 1
        elif frame_lower == "middle":
            frame = num_frames / 2
        elif frame_lower == "last":
            frame = num_frames
        else:
            try:
                frame = int(frame)
            except:
                raise Exception("Invalid frame value '%s'." % frame)


    set_point = frame / float(num_frames)

    cmd = ["ffmpeg", "-ss", str(set_point), "-i", movie_filepath, "-vframes", str(1)]

    if resolution:
        cmd.append("-s")
        cmd.append(resolution)

    if force:
        cmd.append("-y")  

    cmd.append(output_filepath)

    print " ".join(cmd)
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()

    if not p.returncode == 0:
        raise Exception(output[1])

def get_media_info(path):
    """
    """
    cmd = ["rvls", "-l", path]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()

    if not p.returncode is 0 or "error" in output[1].lower():
        raise Exception("Unable to get media info from '%s':\n\t%s" % (path, output[1]))

    pattern = re.compile("(?P<resolution>\d+ x \d+)\s*(?P<type>\S*)\s*(?P<channels>\S*)\s*"\
        "(?P<fps>\S*)\s*(?P<frames>\S*)\s*(?P<file>\S*)\s*")

    result = output[0]

    media_infos = []

    for entry in result.strip().split("\n")[1:]:
        entry = entry.strip()        
        pattern_match = pattern.match(entry).groupdict()        
        media_info = {}
        media_info["resolution"] =  tuple([ int(x) for x in pattern_match["resolution"].split(" x ") ])
        media_info["fps"] = int(pattern_match["fps"])   
        media_info["frames"] = int(pattern_match["frames"])     
        media_infos.append(media_info)

    return media_infos

def generate_movie_thumbnail(movie_filepath, output_path=None, frame=None):
    """
    """
    media_info = get_media_info_ffprobe(movie_filepath)[0]
    if frame is None:
        frame = media_info["frames"] / 2
    file_name, ext = os.path.splitext(os.path.basename(movie_filepath))

    file_name = "%s.thumb.jpg" % file_name

    if output_path is None:
        output_path = os.path.dirname(movie_filepath)
    
    output_filepath = os.path.join(output_path, file_name)    

    cmd = ["rvio", movie_filepath, "-t", str(frame), "-o", output_filepath]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()

    if not p.returncode == 0 or "error" in output[1].lower():                
        raise Exception("Unable to generate thumbnail for '%s':\n\t%s" % (output_filepath, output[1]))

    return output_filepath    



def frame_submit(entity, name, start_frame, end_frame, frames_path=None, movie_path=None, 
    upload=False, thumbnail=None, user=None, comment=None, status=None):
    """
    """
    if user is None:
        user = getpass.getuser()

    version = shotgun.create_version(entity, name, user, frames_path, movie_path, start_frame,
        end_frame, description=comment)

    log.info("Created Version: %s" % version)

    if upload:
        log.info("Uploading Movie...")
        shotgun.upload_quicktime(version["id"], upload)
        log.info("Uploading Complete.")
    
def test_submit():
    frames = "/mnt/publish/shots/010/0020/lgt/render/images/snt_010_0020_lgt_v001.%V.1-24#.exr"
    movie = "/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.%V.mov"
    upload = "/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov"

    shot = shotgun._sg.find_one("Shot", [("id", "is", 1161)], ["code"])
    print "Submitting frames for %s" % shot["code"]
    frame_submit(shot, "snt_010_0020_lgt_v004", 1, 24, frames_path=frames, movie_path=movie,
        comment="quick test", upload=upload)

#print get_media_info("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov")
#print generate_movie_thumbnail("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov")
#print get_media_info_ffprobe("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov")

print extract_image_from_movie("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov", "middle", "/mnt/publish/shots/010/0020/lgt/movies/test.jpg")


#log.addHandle(logging.StreamHandler())
#log.setLevel(logging.DEBUG)