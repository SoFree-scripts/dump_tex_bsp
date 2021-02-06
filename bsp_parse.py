import struct
import sys
import io
import os
import json

# Dont Print to console?
SILENT=False
# Write to a file?
LOGGING=False
# Show helpful warnings about broken map fields?
DEBUG=False
# Check if the file is in FTP?
EXISTSCHECK=False
EXISTSPATH=""

# if ignore_defaults_tex.txt exist, it wont' show these
# if ignore_defaults_sound.txt exist, it wont' show these

EXPORT_TEXTURES = []
EXPORT_SOUNDS = []
EXPORT_ENTS = ""

EXPORT_SOUNDS_MISSING = []
EXPORT_SOUNDS_EXIST = []


# def get_tex():
#     return EXPORT_TEXTURES
# def get_snd():
#     return EXPORT_SOUNDS
# def get_ent():
#     return EXPORT_ENTS

def search_for_open_bracket(startindex,thelist):
    # search up
    for x in range(startindex,-1,-1):
        if thelist[x][0] == "{":
            return x
    return None

def search_for_closed_bracket(startindex,thelist):

    # search down
    for x in range(startindex,len(thelist)):
        if thelist[x][0] == "}":
            return x
    return None

def grab_lump(lump_num,a_sof_map):
    bsp_header_size = 8
    lump_header_size = 8
    lump_offset = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num)[0]
    lump_size = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num + 4)[0]
    # print(f"offset = {lump_offset}\nsize = {lump_size}")
    
    mview = memoryview(a_sof_map)
    return (mview[lump_offset:lump_offset+lump_size],lump_size)

# get the entity_table text file out of bsp file
def dump_textures(a_sof_map):
    
    has_defaults = False
    if os.path.isfile("ignore_defaults_tex.txt"):
        with open("ignore_defaults_tex.txt",'r') as f:
            def_sounds = json.load(f)
        has_defaults = True

    alltex,lump_size = grab_lump(5,a_sof_map)

    # print(alltex[40:60].tobytes())
    # print(alltex[116:140].tobytes())

    SURFACE_HEADER_LEN = 76
    TEXNAME_OFFSET = 40
    textures = []
    index = 0
    while index < lump_size:
        name = (struct.unpack_from('32s',alltex,index+TEXNAME_OFFSET)[0].decode('latin-1').rstrip("\x00") + ".m32").lower()
        if has_defaults:
            if name not in def_sounds:
                textures.append ( name )
        else:
            textures.append ( name )
        index += SURFACE_HEADER_LEN

    textures = sorted(set(textures))
    # for tex in textures: 
    #     print(f"texname : {tex}")
    return textures


def classExists(inlines,classname):
    found_intermission = -1
    line_number = 0
    for index,line in enumerate(inlines):
        # remove newline
        search = inlines[index].split("\n")[0]
        # separate and remove spaces
        search = search.split('"')
        if len(search) % 2 == 0:
            # even is bad
            continue
        search = [ s for s in search if " " not in s if s]
        if len(search) > 1:
            if search[0].lower() == "classname" and search[1] == f"{classname}":
                return True
    return False


def grabField(inlines,classname,fieldname):
    found_intermission = -1
    line_number = 0
    for index,line in enumerate(inlines):
        # remove newline
        search = inlines[index].split("\n")[0]

        search = search.split('"')
        if len(search) % 2 == 0:
            # even is bad
            continue
        # [1] and [3]
        # remove spaces

        search = [ s for s in search if " " not in s if s ]
        
        if len(search) > 1:
            if search[0].lower() == "classname" and search[1] == f"{classname}":
                found_intermission = index
                # print(f"debug:found {classname}")
                break

    if found_intermission != -1:
        # found the above
        start_line = search_for_open_bracket(found_intermission,inlines)
        end_line = search_for_closed_bracket(found_intermission,inlines)
        # error
        if start_line is None or end_line is None:
            print("error parsing entity table")
            sys.exit(1)
        targetname = ""
        # search for targetname
        for line in inlines[start_line+1:end_line]:
            # remove newline
            splitted = line.split("\n")[0]
            # separate and remove spaces
            splitted = splitted.split('"')
            if len(splitted) % 2 == 0:
                # even is bad
                continue
            splitted = [ s for s in [s.strip(' ') for s in splitted] if s ]
            if len(splitted) > 1:
                if splitted[0].lower() == f"{fieldname}":
                    targetname = splitted[1]
                    break
        if len(targetname) > 0:
            # print(type(targetname))
            # print(targetname)
            return targetname.lower()
    return None

def grabFields(inlines,classname,fieldname):
    fields = []
    line_number = 0
    next_bracket = 0
    for index,line in enumerate(inlines):

        if index < next_bracket:
            # efficiency
            continue
        else:
            # reset cos now searching for classname
            # this is an open bracket
            next_bracket = 0

        # remove newline
        search = inlines[index].split("\n")[0]
        search = search.split('"')
        if len(search) % 2 == 0:
            # even is bad
            continue


        # [1] and [3]
        # remove spaces and empty
        
        # print(search)
        search = [ s for s in [s.strip(' ') for s in search] if s ]
        
        if len(search) > 1:
            if search[0].lower() == "classname":
                if search[1] == f"{classname}":

                    start_line = search_for_open_bracket(index,inlines)
                    end_line = search_for_closed_bracket(index,inlines)
                    if start_line is None or end_line is None:
                        print("error parsing entity table")
                        sys.exit(1)
                    value = ""
                    # search for fieldname
                    for line in inlines[start_line+1:end_line]:
                        # remove newline
                        splitted = line.split("\n")[0]
                        # separate and remove spaces
                        splitted = splitted.split('"')
                        if len(splitted) % 2 == 0:
                            # even is bad
                            # bad line
                            continue
                        splitted = [ s for s in [s.strip(' ') for s in splitted] if s ]

                        # print(splitted)
                        if len(splitted) > 1:
                            if splitted[0].lower() == f"{fieldname}":
                                # we found it

                                value = splitted[1]
                                fields.append( value.lower() )
                                # stop searching within this { }
                                break
                else:
                    # its a classname not interested in - skip
                    next_bracket = search_for_open_bracket(index,inlines)
                    if next_bracket is None:
                        # reached end
                        break
    # print(fields)
    return fields

REQUIRES_WAV = 2
OPTIONAL_WAV = 1
WAVLESS = 0
fieldFindSet = (("trigger_useable","targetname",REQUIRES_WAV),
                ("target_speaker","noise",OPTIONAL_WAV)
               )
# get the exact classname data from entity text buffer
def find_sounds(entlist,inbsp):
    global EXPORT_SOUNDS_MISSING, EXPORT_SOUNDS_EXIST
    has_defaults = False
    if os.path.isfile("ignore_defaults_sound.txt"):
        with open("ignore_defaults_sound.txt",'r') as f:
            def_sounds = json.load(f)
        has_defaults = True

    soundList = []
    EXPORT_SOUNDS_MISSING = []
    EXPORT_SOUNDS_MISSING_EXIST = []

    for clss,fld,wavReq in fieldFindSet:
        fields = grabFields(entlist,clss,fld)
        if not fields:
            continue
        fields = list(set(fields))
        deleteme = []
        for fidx,f in enumerate(fields):

            if has_defaults:
                if f in def_sounds:
                    deleteme.append(fidx)

            # make sure we get a string ending in .wav
            if wavReq == WAVLESS:
                if f.endswith(".wav"):
                    if DEBUG:
                        print(f"WARNING: mapname:{inbsp} has non-functioning sound field \"{f}\" {clss} @{fld}, remove .wav extension")
                else:
                    if '.' in f:
                        fields[fidx] = f.split(".")[0]
                    fields[fidx] += ".wav"
            elif wavReq == OPTIONAL_WAV:
                if f.endswith(".wav"):
                    pass
                else:
                    if '.' in f:
                        fields[fidx] = f.split(".")[0]
                    fields[fidx] += ".wav"
            elif wavReq == REQUIRES_WAV:
                if f.endswith(".wav"):
                    pass
                else:
                    deleteme.append(fidx)
                    if DEBUG == True:
                        print(f"WARNING: mapname:{inbsp} has non-functioning sound field \"{f}\" {clss} @{fld}, append .wav extension")
                        # if '.' in f:
                        #     fields[fidx] = f.split(".")[0]
                        # fields[fidx] += ".wav"

        for d in sorted(deleteme,reverse=True):
            del fields[d]

        rsrcDir = os.path.join(EXISTSPATH,"sound")
        for fidx,f in enumerate(fields):
            if EXISTSCHECK:
                if os.path.isfile(os.path.normcase(os.path.join(rsrcDir,fields[fidx].lstrip('/'))) ):
                    # fields[fidx] += "     E"
                    EXPORT_SOUNDS_EXIST.append(f)
                else:
                    # fields[fidx] += "     X"
                    EXPORT_SOUNDS_MISSING.append(f)
            soundList.append(f)

        # soundList.extend(fields)

    # print(soundList)
    EXPORT_SOUNDS_EXIST = sorted(set(EXPORT_SOUNDS_EXIST))
    EXPORT_SOUNDS_MISSING = sorted(set(EXPORT_SOUNDS_MISSING))
    return sorted(set(soundList))



def processBSP(inbsp):
    global EXPORT_TEXTURES, EXPORT_SOUNDS, EXPORT_ENTS
    # print(sys.argv[1])
    # inbsp = sys.argv[1]
    # sof uses stricmp for keyname
    inbsp = os.path.normcase(inbsp)
    with open(inbsp,"rb") as sof_map:
        data = sof_map.read()
    if struct.unpack_from('4s',data,0)[0] != b"IBSP":
        print("map is corrupt")
        # sys.exit(1)
        return 1

    entlist,lump_size = grab_lump(0,data)
    entlistb = entlist.tobytes().rstrip(b"\x00")
    if LOGGING:
        with open("entlist.txt","wb") as f:
            f.write(entlistb)
    EXPORT_ENTS = entlistb.decode("latin-1")

    stringfile = io.StringIO(entlistb.decode("latin-1"))
    entlist_lines = stringfile.readlines()
    stringfile.close()
    if DEBUG:
        if classExists(entlist_lines,"ambient_generic"):
            print(f"WARNING: mapname:{inbsp} has non-functioning sound field in classname ambient_generic is not valid for sof1.")
        
    bspversion = struct.unpack_from('<i',data,4)[0]
    print(f"Parsing map: {inbsp}")
    if DEBUG:
        if bspversion != 46:
            print(f"WARNING: bspversion is not 46, its {bspversion}, are you sure this is valid sof map?")
    # print( type(data))
    if not SILENT:
        print("__TEXTURES__")
    all_textures = dump_textures(data)
    EXPORT_TEXTURES = all_textures
    if len(all_textures) == 0:
        if not SILENT:
            print(" [NULL]")
    else:
        if not SILENT:
            for t in all_textures:
                print(" " + t)
        if LOGGING:
            with open("textures.txt","w") as f:
                for each in all_textures:
                    f.write(each + "\n")

    if not SILENT:
        print("__SOUNDS__")
    all_sounds = find_sounds(entlist_lines,inbsp)
    EXPORT_SOUNDS = all_sounds
    if len(all_sounds) == 0:
        if not SILENT:
            print(" [NULL]")
    else:
        if not SILENT:
            for s in all_sounds:
                # print(type(s))
                print(" " + s)
        
        if LOGGING:
            with open("sounds.txt","w") as f:
                for snd in all_sounds:
                    f.write(snd + "\n")

    return 0
