# Simple script to compare current commit with pypi commit id
import os
import subprocess
import requests
import json
import sys

TEST_PYPI_URL = "https://test.pypi.org/pypi/openfl-nightly/json"
PYPI_URL = "https://pypi.org/pypi/openfl-nightly/json"

def get_pypi_commit_id(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        commit_id = data['info']['project_urls']['Source Code']
        commit_id = commit_id.split("/")[-1]
        print(f"Commit ID from PyPI: {commit_id}")
        return commit_id.split('/')[-1]
    else:
        print("Failed to fetch data from PyPI")
        return None

def get_current_commit_id():
# get commit_id from environment variable
    commit_id = os.getenv('commit_id')
    if commit_id:
        return commit_id
    else:
        print("Environment variable 'commit_id' not set")
        return None
    
    
if __name__ == "__main__":
    pypi_commit_id = get_pypi_commit_id(TEST_PYPI_URL)
    current_commit_id = get_current_commit_id()

    if pypi_commit_id and current_commit_id:
        if pypi_commit_id == current_commit_id:
            print("Commit IDs match, No need to proceed with workflow")
            # Set commit_id to None in the environment variable
            os.setenv['commit_id'] = None
        else:
            print("Commit IDs do not match")

    else:
        print("Could not retrieve commit IDs")
        sys.exit(1)