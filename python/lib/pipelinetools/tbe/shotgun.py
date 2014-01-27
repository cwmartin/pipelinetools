import re
import shotgun_api3 as shotgun

SHOTGUN_URL = "http://chrismartin.shotgunstudio.com"
SHOTGUN_SCRIPT_NAME = "Test Script 1"
SHOTGUN_APP_KEY = "0b5bb2d25429fa4999655ec8dc2f786ae301a606"

_sg = shotgun.Shotgun(SHOTGUN_URL, SHOTGUN_SCRIPT_NAME, SHOTGUN_APP_KEY)

def get_project(code, sg=None):
    """
    """
    sg = sg or _sg

    return sg.find("Project", [("sg_code", "is", code)], ["sg_code"])

def upload_quicktime(version_id, quicktime_path, sg=None):
    """
    """
    sg = sg or _sg
    sg.upload("Version", version_id, quicktime_path, "sg_uploaded_movie")


def create_version(entity, code, user, path_to_frames, path_to_movie, start_frame, end_frame, description=None, status=None,
    sg=None):
    """
    """
    sg = sg or _sg
    if not "project" in entity:
        _entity = sg.find_one(entity["type"], [("id", "is", entity["id"])], ["project"])
        project = _entity["project"]
    else:
        project = entity["project"]

    if isinstance(user, dict) and "id" in user:
        _user = user
    else:
        _user = sg.find_one("HumanUser", [("login", "is", user)])

    frame_count = end_frame - start_frame + 1
    frame_range = "%s-%s" % (start_frame, end_frame)
    
    data = {"project":project, "entity":entity, "user":_user,
        "code":code, "description":description, "sg_path_to_frames":path_to_frames,
        "sg_path_to_movie":path_to_movie, "sg_first_frame":start_frame, "sg_last_frame":end_frame,
        "frame_count":frame_count, "frame_range":frame_range}

    return sg.create("Version", data)


#upload_quictime(6002, "/home/christopher/dev/sintel_trailer/1080/sintel.mov")

# shot = _sg.find_one("Shot", [("id", "is", 1161)])

# print shot
# create_version(shot, "Test version version create", "christopher", "", "", description="Testing a version create from a script.")
