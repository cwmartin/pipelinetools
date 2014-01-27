import shotgun
import getpass
import subprocess
import re
import os
import logging

log = logging.getLogger(__name__)

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
        media_info = pattern.match(entry).groupdict()
        media_info["resolution"] = [ int(x) for x in media_info["resolution"].split(" x ") ]
        media_info["fps"] = int(media_info["fps"])   
        media_info["frames"] = int(media_info["frames"])     
        media_infos.append(media_info)

    return media_infos

def generate_movie_thumbnail(movie_filepath, output_path=None, frame=None):
    """
    """
    media_info = get_media_info(movie_filepath)[0]
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

    print "Created Version", version

    if upload:
        print "Uploading Movie..."
        shotgun.upload_quicktime(version["id"], upload)
        print "Uploading Complete."
    
def test_submit():
    frames = "/mnt/publish/shots/010/0020/lgt/render/images/snt_010_0020_lgt_v001.%V.1-24#.exr"
    movie = "/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.%V.mov"
    upload = "/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov"

    shot = shotgun._sg.find_one("Shot", [("id", "is", 1161)], ["code"])
    print "Submitting frames for %s" % shot["code"]
    frame_submit(shot, "snt_010_0020_lgt_v004", 1, 24, frames_path=frames, movie_path=movie,
        comment="quick test", upload=upload)

#print get_media_info("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov")
print generate_movie_thumbnail("/mnt/publish/shots/010/0020/lgt/movies/snt_010_0020_lgt_v001.left.mov")
