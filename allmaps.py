import sys
import os
import shutil
import bsp_parse

resource_dir = "d:/sof_ftp/base"


"""
# Dont Print to console?
bsp_parse.SILENT=True
# Write to a file?
bsp_parse.LOGGING=False
# Show helpful warnings about broken map fields?
bsp_parse.DEBUG=False
# Check if the file is in FTP?
bsp_parse.EXISTSCHECK=False
bsp_parse.EXISTSPATH=""

# if ignore_defaults_tex.txt exist, it wont' show DEFAULT SOF TEXTURES
# if ignore_defaults_sound.txt exist, it wont' show DEFAULT SOF SOUNDS
"""
bsp_parse.EXISTSCHECK=True
bsp_parse.EXISTSPATH=resource_dir

mapdir = os.path.join(resource_dir,"maps/dm")

try:
	shutil.rmtree("bspdata")
except:
	pass

try:
	os.makedirs("bspdata/sound/")
except:
	pass
try:
	os.makedirs("bspdata/textures")
except:
	pass
try:
	os.makedirs("bspdata/entlists")
except:
	pass

try:
	os.makedirs("bspdata/sound_exist")
except:
	pass

try:
	os.makedirs("bspdata/sound_missing")
except:
	pass

for root, dirs, files in os.walk(mapdir):
	for f in files:
		mapname,extension = os.path.splitext(f)
		if extension != ".bsp":
			continue
		full_path = os.path.join(root,f)
		fpath_rel = os.path.relpath(full_path,mapdir).replace("\\","/")
		# ret = os.system('python do.py ' + "\"" + full_path + "\"")
		ret = bsp_parse.processBSP(full_path)
		if ret == 0:
			texs = bsp_parse.EXPORT_TEXTURES
			if texs:
				with open("bspdata/textures/" + mapname + ".txt","w",encoding="latin-1") as ff:
					for t in texs:
						ff.write(f"{t}\n")

			snds = bsp_parse.EXPORT_SOUNDS
			if snds:
				with open("bspdata/sound/" + mapname + ".txt","w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")

			ents = bsp_parse.EXPORT_ENTS
			if ents:
				with open("bspdata/entlists/" + mapname + ".txt","w",encoding="latin-1") as ff:
					ff.write(ents)
					
			snds = bsp_parse.EXPORT_SOUNDS_MISSING
			if snds:
				with open("bspdata/sound_missing/" + mapname + ".txt","w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")

			snds = bsp_parse.EXPORT_SOUNDS_EXIST
			if snds:
				with open("bspdata/sound_exist/" + mapname + ".txt","w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")