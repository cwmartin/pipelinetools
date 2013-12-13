import re
import shotgun_api3 as shotgun

SHOTGUN_URL = "http://chrismartin.shotgunstudio.com"
SHOTGUN_SCRIPT_NAME = "Test Script 1"
SHOTGUN_APP_KEY = "0b5bb2d25429fa4999655ec8dc2f786ae301a606"
PROJECT_NAME = "RnD"

#SHOTGUN_URL = "http://toonboxent.shotgunstudio.com"
#SHOTGUN_SCRIPT_NAME = "testing"
#SHOTGUN_APP_KEY = "cc7c038a621d8e1a13217fa98a122843c89a09b4"
#PROJECT_NAME = "DEV:Spark"

sg = shotgun.Shotgun(SHOTGUN_URL, SHOTGUN_SCRIPT_NAME, SHOTGUN_APP_KEY)

def get_project(name):
    return sg.find_one("Project", [["name", "is", name]])

re_pattern = "spk_([a-z]{1})_(.*)"
match = re.compile(re_pattern)

project = get_project(PROJECT_NAME)    

asset_type_incr = {"c":0, "p":0, "s":0, "v":0}
asset_type_value = {"c":"chr", "p":"prp", "s":"set", "v":"vhl"}
if project:
    
    #for i in range(10, 200, 10):
    #    sequence_code = "spk_%03i" % i
    #    data = {"project":project, "code":sequence_code}
    #    result = sg.create("Sequence", data)

    new_assets = {}

    f = open("/home/christopher/dev/spk_assets.txt", "r")
    for line in f.readlines():
        line = line.strip()

        match = re.match(re_pattern, line)
        if match:
            asset_letter = match.groups()[0]
            asset_name = match.groups()[1]

            asset_type_incr[asset_letter] += 1

            incr = asset_type_incr[asset_letter]

            code = "spk_%s_%04ia" % (asset_type_value[asset_letter], incr)

            code, asset_name, asset_type_value[asset_letter]

            new_assets[asset_name] = code

    print "spark" in new_assets.keys()

    found = sg.find("Asset", filters=[["project", "is", project], ["sg_name", "in", new_assets.keys()]],
                            fields=["code", "sg_name"])


    print found



        







    



