import sys
import os
import json

resource_dir = sys.argv[1]
texdir = os.path.join(resource_dir,"textures")
with open("ignore_defaults_tex.txt","w") as file:
	filelist = []
	for root, dirs, files in os.walk(texdir):
		for f in files:
			full_path = os.path.join(root,f)
			fpath_rel = os.path.relpath(full_path,texdir).replace("\\","/")
			filelist.append(fpath_rel)

	j = json.dumps(filelist)
	file.write(j)

sounddir = os.path.join(resource_dir,"sound")
with open("ignore_defaults_sound.txt","w") as file:
	filelist = []
	for root, dirs, files in os.walk(sounddir):
		for f in files:
			full_path = os.path.join(root,f)
			fpath_rel = os.path.relpath(full_path,sounddir).replace("\\","/")

			filelist.append(fpath_rel)

	j = json.dumps(filelist)
	file.write(j)

"""
ghouldir = os.path.join(resource_dir,"ghoul")
with open("ignore_defaults_sound.txt","w") as file:

	filelist = []
	for root, dirs, files in os.walk(ghouldir):
		# print(f"root: {root}")
		# f.write()
		for f in files:
			full_path = os.path.join(root,f)
			# path relative to 'root' directory passed to function eg. "textures/sprite.m32"
			fpath_rel = os.path.relpath(full_path,ghouldir).replace("\\","/")
			# print(f"tex = {fpath_rel}")
			# file.write(fpath_rel + "\n")
			filelist.append(fpath_rel)

	j = json.dumps(filelist)
	file.write(j)
"""