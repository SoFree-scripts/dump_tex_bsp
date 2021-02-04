import struct
import sys
import io

LOGGING=True

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
    
    alltex,lump_size = grab_lump(5,a_sof_map)

    # print(alltex[40:60].tobytes())
    # print(alltex[116:140].tobytes())

    SURFACE_HEADER_LEN = 76
    TEXNAME_OFFSET = 40
    textures = []
    index = 0
    while index < lump_size:
        textures.append ( (struct.unpack_from('32s',alltex,index+TEXNAME_OFFSET)[0].decode('latin-1').rstrip("\x00") + ".m32").lower() )
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
        search = search.split(" ")
        search = [ s for s in search if s ]
        if len(search) > 1:
            if search[0].lower() == "\"classname\"" and search[1] == f"\"{classname}\"":
                return True
    return False


def grabField(inlines,classname,fieldname):
    found_intermission = -1
    line_number = 0
    for index,line in enumerate(inlines):
        # remove newline
        search = inlines[index].split("\n")[0]
        # separate and remove spaces
        search = search.split(" ")
        search = [ s for s in search if s ]

        if len(search) > 1:
            if search[0].lower() == "\"classname\"" and search[1] == f"\"{classname}\"":
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
            space_splitted = line.split("\n")[0]
            # separate and remove spaces
            space_splitted = space_splitted.split(" ")
            search = [ s for s in space_splitted if s ]
            if len(search) > 1:
                if search[0] == f"\"{fieldname}\"":
                    targetname = search[1]
                    break
        if len(targetname) > 0:
            # print(type(targetname))
            # print(targetname)
            return targetname.replace("\"","").lower()
    return None

REQUIRES_WAV = 2
OPTIONAL_WAV = 1
WAVLESS = 0
fieldFindSet = (("trigger_useable","targetname",REQUIRES_WAV),
                ("target_speaker","noise",OPTIONAL_WAV),
                ("worldspawn","startmusic",OPTIONAL_WAV),
                ("worldspawn","sounds",OPTIONAL_WAV)
               )
# get the exact classname data from entity text buffer
def find_sounds(entlist,a_sof_map):

    soundList = []
    for clss,fld,wavReq in fieldFindSet:
        n = grabField(entlist,clss,fld)
        if n is None:
            continue
        # make sure we get a string ending in .wav
        if wavReq == WAVLESS:
            if n.endswith(".wav"):
                print(f"WARNING: mapname:{inbsp} has non-functioning sound field {classname} @{fieldname}, remove .wav extension")
            else:
                if '.' in n:
                    n = n.split(".")[0]
                n += ".wav"
        elif wavReq == OPTIONAL_WAV:
            if n.endswith(".wav"):
                pass
            else:
                if '.' in n:
                    n = n.split(".")[0]
                n += ".wav"
        elif wavReq == REQUIRES_WAV:
            if n.endswith(".wav"):
                pass
            else:
                print(f"WARNING: mapname:{inbsp} has non-functioning sound field {classname} @{fieldname}, append .wav extension")
                if '.' in n:
                    n = n.split(".")[0]
                n += ".wav"
        soundList.append(n)

    # print(soundList)
    return sorted(set(soundList))


# print(sys.argv[1])
inbsp = sys.argv[1]

# sof uses stricmp for keyname
with open(inbsp,"rb") as sof_map:
    data = sof_map.read()
    if struct.unpack_from('4s',data,0)[0] != b"IBSP":
        print("map is corrupt")
        sys.exit(1)

    entlist,lump_size = grab_lump(0,data)
    if LOGGING:
        with open("entlist.txt","wb") as f:
            f.write(entlist)

    stringfile = io.StringIO(entlist.tobytes().decode("latin-1"))
    entlist_lines = stringfile.readlines()
    stringfile.close()
    if classExists(entlist_lines,"ambient_generic"):
        print(f"WARNING: mapname:{inbsp} has non-functioning sound field in classname ambient_generic is not valid for sof1.")
    # print( type(data))
    print("__TEXTURES__")
    all_textures = dump_textures(data)
    if len(all_textures) == 0:
        print(" [NULL]")
    else:
        for t in all_textures:
            print(" " + t)
        
        if LOGGING:
            with open("tex.txt","w") as f:
                for each in all_textures:
                    f.write(each + "\n")

    print()
    print("__SOUNDS__")
    all_sounds = find_sounds(entlist_lines,data)
    if len(all_sounds) == 0:
        print(" [NULL]")
    else:
        for s in all_sounds:
            # print(type(s))
            print(" " + s)
        if LOGGING:
            with open("sounds.txt","w") as f:
                for snd in all_sounds:
                    f.write(snd + "\n")
