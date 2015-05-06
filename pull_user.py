import json
from askfm import *

if(len(sys.argv)==0):
    print("Usage: pull_user.py <username>")
    exit(0)

username = sys.argv[1]
user = getUser(username)

print(json.dumps(user,sort_keys=True))
