#!/bin/python3

from sys import argv
import json
import re

progname = argv.pop(0)
if progname.startswith("py"): # this is awesom
    progname = argv.pop(0)
if len(argv) == 0:
    print(f'{progname}: giv path to jsml')
    exit(69)

infile = argv.pop(0)
outfile = infile.removesuffix(".jsml") + ".rhdc.json"

with open(infile) as f:
    # json with comments is unsolved cs problem :faceless_ario:
    jsml: dict = json.loads(re.sub(r"""("(?:\\"|[^"])*?")|(\/\*(?:.|\s)*?\*\/|\/\/.*)""", r"\1", f.read()))

rhdc = {}

rhdc["$schema"] = "https://parallel-launcher.ca/layout/advanced-01/schema.json"

rhdc["format"] = {
    # default sm64, thats what star display thinks anyway 
    "save_type":"EEPROM","num_slots":4,"slots_start":0,"slot_size":112,"active_bit":95,"checksum_offset":54
}

rhdc["groups"] = []

def parsemacolumn(rows: list[dict]):
    global globalstarmask

    courses = []

    coursename = str()
    coursedata = []
    typ = 0
    for row in rows:
        typ = row["Type"]

        if typ == 2:
            if len(coursedata) != 0:
                courses.append({
                    "name": coursename,
                    "data": coursedata.copy(),
                })
            coursedata.clear()
            coursename = row["text"]
        elif typ == 1:
            coursedata.append({
                "offset": row["offset"],
                "mask": row["starMask"] & globalstarmask,
            })
        else:
            raise "wat"

    return courses.copy()

globalstarmask = (2 ** jsml.get("starsShown", 8)) - 1

if jsml.get("courseDescription") != None:
    courses = parsemacolumn(jsml["courseDescription"])
    rhdc["groups"].append({
        "name": "",
        "side": "left",
        "courses": courses.copy(),
    })

if jsml.get("secretDescription") != None:
    courses = parsemacolumn(jsml["secretDescription"])
    rhdc["groups"].append({
        "name": "",
        "side": "right",
        "courses": courses.copy(),
    })  

if (goldstar := jsml.get("goldStar")) != None:
    rhdc["collectedStarIcon"] = goldstar

if (darkStar := jsml.get("darkStar")) != None:
    rhdc["missingStarIcon"] = darkStar

with open(outfile, "w") as f:
    json.dump(rhdc, f)

print("ok")