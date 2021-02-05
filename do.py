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
                ("target_speaker","noise",OPTIONAL_WAV),
                ("worldspawn","startmusic",OPTIONAL_WAV),
                ("worldspawn","sounds",OPTIONAL_WAV)
               )
# get the exact classname data from entity text buffer
def find_sounds(entlist,a_sof_map):

    soundList = []
    for clss,fld,wavReq in fieldFindSet:
        fields = grabFields(entlist,clss,fld)
        if not fields:
            continue
        fields = list(set(fields))
        for fidx,f in enumerate(fields):
            # make sure we get a string ending in .wav
            if wavReq == WAVLESS:
                if f.endswith(".wav"):
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
                    print(f"WARNING: mapname:{inbsp} has non-functioning sound field \"{f}\" {clss} @{fld}, append .wav extension")
                    if '.' in f:
                        fields[fidx] = f.split(".")[0]
                    fields[fidx] += ".wav"
        soundList.extend(fields)

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
