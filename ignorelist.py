import sys
import os

resource_dir = sys.argv[1]


resource_dir = os.path.join(resource_dir,"textures")
with open("ignore_defaults.txt","w") as file:

	for root, dirs, files in os.walk(resource_dir):
		# print(f"root: {root}")
		# f.write()
		for f in files:
			full_path = os.path.join(root,f)
			# path relative to 'root' directory passed to function eg. "textures/sprite.m32"
			fpath_rel = os.path.relpath(full_path,resource_dir).replace("\\","/")
			# print(f"tex = {fpath_rel}")
			file.write(fpath_rel + "\n")
