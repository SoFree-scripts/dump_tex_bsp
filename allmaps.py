import sys
import os
import shutil
import bsp_parse




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
resource_dir = "d:\\sof_ftp\\base"
bsp_parse.EXISTSCHECK=True
bsp_parse.EXISTSPATH=resource_dir

mapdir = os.path.join(resource_dir,"maps")

try:
	shutil.rmtree("bspdata")
except:
	pass

for root, dirs, files in os.walk(mapdir):
	tail = os.path.split(root)[1]
	for d in dirs:
		try:
			os.makedirs("bspdata/" + d + "/sound/")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/textures")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/entlists")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/sound_exist")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/sound_missing")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/textures_exist")
		except:
			pass
		try:
			os.makedirs("bspdata/" + d + "/textures_missing")
		except:
			pass
	for f in files:
		mapname,extension = os.path.splitext(f)
		if extension != ".bsp":
			continue
		full_path = os.path.join(root,f)
		ret = bsp_parse.processBSP(full_path)
		if ret == 0:
			texs = bsp_parse.EXPORT_TEXTURES
			if texs:
				writefile=os.path.join("bspdata",tail,"textures",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for t in texs:
						ff.write(f"{t}\n")

			snds = bsp_parse.EXPORT_SOUNDS
			if snds:
				writefile=os.path.join("bspdata",tail,"sound",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")

			ents = bsp_parse.EXPORT_ENTS
			if ents:
				writefile=os.path.join("bspdata",tail,"entlists",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					ff.write(ents)
					
			snds = bsp_parse.EXPORT_SOUNDS_MISSING
			if snds:
				writefile=os.path.join("bspdata",tail,"sound_missing",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")

			snds = bsp_parse.EXPORT_SOUNDS_EXIST
			if snds:
				writefile=os.path.join("bspdata",tail,"sound_exist",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for s in snds:
						ff.write(f"{s}\n")

			texs = bsp_parse.EXPORT_TEXTURES_MISSING
			if texs:
				writefile=os.path.join("bspdata",tail,"textures_missing",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for t in texs:
						ff.write(f"{t}\n")

			texs = bsp_parse.EXPORT_TEXTURES_EXIST
			if texs:
				writefile=os.path.join("bspdata",tail,"textures_exist",mapname + ".txt")
				with open(writefile,"w",encoding="latin-1") as ff:
					for t in texs:
						ff.write(f"{t}\n")