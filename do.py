import struct
import sys

# get the entity_table text file out of bsp file
def dump_textures(a_sof_map):
    bsp_header_size = 8
    lump_header_size = 8
    lump_num = 5
    lump_offset = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num)[0]
    lump_size = struct.unpack_from('<i',a_sof_map,bsp_header_size+lump_header_size*lump_num + 4)[0]
    print(f"offset = {lump_offset}\nsize = {lump_size}")
 

    mview = memoryview(a_sof_map)
    alltex = mview[lump_offset:lump_offset+lump_size]

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
    for tex in textures: 
        print(f"texname : {tex}")
    return textures


print(sys.argv[1])
inbsp = sys.argv[1]
with open(inbsp,"rb") as sof_map:
    data = sof_map.read()
    # print( type(data))
    all_textures = dump_textures(data)
    
    with open("tex.txt","w") as f:
        for each in all_textures:
            # print(type(each))
            # print(len(each))
            f.write(each + "\n")
