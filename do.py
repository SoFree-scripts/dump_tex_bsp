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
        textures.append ( struct.unpack_from('32s',alltex,index+TEXNAME_OFFSET)[0].decode('latin-1').rstrip("\x00") )
        index += SURFACE_HEADER_LEN

    textures = list(set(textures))
    # for tex in textures: 
    #     print(f"texname : {tex}")
    return textures

# get the exact classname data from entity text buffer
def find_sounds(a_sof_map):

    entlist,lump_size = grab_lump(0,a_sof_map)
    if LOGGING:
        with open("entlist.txt","wb") as f:
            f.write(entlist)
    soundList = []
    stringfile = io.StringIO(entlist.tobytes().decode("latin-1"))
    lines = stringfile.readlines()
    stringfile.close()

    found_intermission = -1
    line_number = 0
    for index,line in enumerate(lines):
        lines[index].strip()
        if line.startswith('"classname" "trigger_speaker"'):
            found_intermission = index
            print("found trigger_speaker")
            break

    if found_intermission != -1:
        # found the above
        start_line = search_for_open_bracket(found_intermission,lines)
        end_line = search_for_closed_bracket(found_intermission,lines)
        # error
        if start_line is None or end_line is None:
            print("error parsing entity table")
            sys.exit(1)
        targetname = ""
        # search for targetname
        for line in lines[start_line+1:end_line]:
            splitted_line = line.split('"')[3]
            num_of_splits = len(splitted_line)
            space_splitted = splitted_line.split()
            len_space = len(space_splitted)
            if line.startswith('"targetname"'):
                if len_space >= 1:
                    targetname = space_splitted[0]
                else:
                    print("error parsing entity table")
                    sys.exit(1)
        if len(targetname) > 0:
            soundList+=targetname

    found_intermission = -1
    for index,line in enumerate(lines):
        # print line
        if line.startswith('"classname" "trigger_useable"'):
            found_intermission = index
            print("found trigger_useable")
            break

    if found_intermission != -1:
        # found the above
        start_line = search_for_open_bracket(found_intermission,lines)
        end_line = search_for_closed_bracket(found_intermission,lines)
        # error
        if start_line is None or end_line is None:
            print("error parsing entity table")
            sys.exit(1)
        targetname = ""
        # search for targetname
        for line in lines[start_line+1:end_line]:
            splitted_line = line.split('"')[3]
            num_of_splits = len(splitted_line)
            space_splitted = splitted_line.split()
            len_space = len(space_splitted)
            if line.startswith('"targetname"'):
                if len_space >= 1:
                    targetname = space_splitted[0]
                else:
                    print("error parsing entity table")
                    sys.exit(1)
        if len(targetname) > 0:
            soundList+=targetname

    if len(soundList) == 0:
        print("no sound data in this entlist")
    return soundList


print(sys.argv[1])
inbsp = sys.argv[1]

with open(inbsp,"rb") as sof_map:
    data = sof_map.read()
    # print( type(data))
    all_textures = dump_textures(data)
    print(all_textures)
    if LOGGING:
        with open("tex.txt","w") as f:
            for each in all_textures:
                f.write(each + "\n")

    all_sounds = find_sounds(data)
    print("sounds...")
    print(all_sounds)
    if LOGGING:
        with open("sounds.txt","w") as f:
            for snd in all_sounds:
                f.write(snd + "\n")
