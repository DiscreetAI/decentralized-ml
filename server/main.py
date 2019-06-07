from flask import Flask, request
import os
import json
import shutil
import random
from subprocess import PIPE, Popen, check_output, call
import time
import stat
import pwd
import grp
import sys

application = Flask(__name__)

COMMAND = "jupyter notebook --no-browser --port {port} &"
COMMAND2 = "npx kill-port {port}"
SRC = "base.ipynb"
BASE_URL = "localhost:{port}"
CLOUD_URL = "https://ec2-13-57-39-123.us-west-1.compute.amazonaws.com:{port}"

@application.route('/')
def landing():
    return "This is the homepage of the Explora server!"

@application.route('/notebook', methods = ["POST", "GET"])
def notebook():
    print("Received /notebook request!")
    repo_name = request.get_json().get("repo_name")
    if not os.path.isdir('notebooks'):
        os.system("mkdir notebooks")
        print("Made notebooks folder!")
    print(os.listdir("notebooks"))
    with open('mappings.json') as f:
        mappings = json.load(f)
    if repo_name not in mappings:
        print("Repo name not in mappings, creating a new Notebook:")
        dst = os.path.join("notebooks", repo_name)
        if not os.path.isdir(dst):
            os.system("mkdir " + dst)
        shutil.copyfile(SRC, os.path.join(dst, repo_name + ".ipynb"))
        print("Made directories and new Notebook!")
        new_port = random.randint(8000,9999)
        while new_port in mappings.values():
            new_port = random.randint(8000, 9999)
        print("Got new port!")
        os.chdir(dst)
        os.system(COMMAND.format(port=new_port))
        print("Started notebook!")
        url = CLOUD_URL.format(port=new_port)
        os.chdir("../..")
        print("Got URL!")
        mappings[repo_name] = new_port
        with open('mappings.json', 'w') as f:
            json.dump(mappings, f)
    print("Sending url!")
    return CLOUD_URL.format(port=mappings[repo_name]) + "\n"

@application.route('/delete', methods = ["POST", "GET"])
def delete():
    print("Received /delete request!")
    repo_name = request.get_json().get("repo_name")
    with open('mappings.json') as f:
        mappings = json.load(f)
    if repo_name not in mappings:
        print("Notebook not found!")
        return "No Notebook found!\n"
    port = mappings.get(repo_name)
    os.system(COMMAND2.format(port=port))
    repo_folder = os.path.join("notebooks", repo_name)
    shutil.rmtree(repo_folder)
    mappings.pop(repo_name)
    with open('mappings.json', 'w') as f:
        json.dump(mappings, f)
    print("Deletion successful!")
    return "Deletion successful!\n"


if __name__ == '__main__':
    from twisted.python import log
    log.startLogging(sys.stdout)
    application.run(host="0.0.0.0")