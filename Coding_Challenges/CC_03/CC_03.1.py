import os

# Replicate this tree of directories and subdirectories:
#
# ├── draft_code
# |   ├── pending
# |   └── complete
# ├── includes
# ├── layouts
# |   ├── default
# |   └── post
# |       └── posted
# └── site
# 1. Using os.system or os.mkdirs replicate this simple directory tree.
# 2. Delete the directory tree without deleting your entire hard drive.

#SAMPLE DIRECTORY TREE
path = 'SAMPLE_DIRECTORY_TREE'

os.mkdir(path)
os.mkdir(path +'\draft_code')
os.mkdir(path +'\draft_code\complete')
os.mkdir(path +'\draft_code\pending')
os.mkdir(path +'\includes')
os.mkdir(path +'\layouts')
os.mkdir(path +'\layouts\default')
os.mkdir(path +'\layouts\post')
os.mkdir(path +'\layouts\post\posted')
os.mkdir(path +'\site')

# listdir = os.listdir('SAMPLE_DIRECTORY_TREE')
# print(listdir)

## DELETE DIRECTORY TREE
# rmdir(path)     #Does not work on directories that are not empty

#Use shutil instead
import shutil

shutil.rmtree(path)

