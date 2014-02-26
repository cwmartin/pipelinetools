"""
"""

import os
import subprocess
import json
import logging

log = logging.getLogger(__name__)

def get_media_info(path, stream=None):
    """
    Use ffprobe to get media info from a media source.
    @param path The full path to the media source.
    @param stream If Given a stream index.
    @returns A dict of media info. If stream is specified, a single dict is return, else a list
    of dicts.
    """    
    cmd = ["ffprobe", "-show_streams", "-print_format", "json", path]    
    log.debug("Getting media info..."))
    log.debug("Running command %s" % " ".join(cmd))
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

    if stream:
        return media_infos[stream]
    return media_infos

def extract_image_from_movie(movie_filepath, frame, output_filepath, resolution=None, force=True):
    """
    Extract a single image from a movie.
    @param movie_filepath The path to the movie.
    @param frame The frame number of the image to extract. This can be a number or one 
    of "first", "middle", "last".
    @param output_filepath The path to the output the image to.
    @resolution If given, the output resolution. If None, the movie resolution is used.
    @param force If True, overwrite any exitsting image at output_filepath.
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
                raise ValueError("Invalid frame value '%s'." % frame)


    set_point = frame / float(num_frames)

    cmd = ["ffmpeg", "-ss", str(set_point), "-i", movie_filepath, "-vframes", str(1)]

    log.debug("Extracting image from movie...")
    log.debug("Running command: %s" % " ".join(cmd))

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
