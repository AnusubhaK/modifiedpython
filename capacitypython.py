import requests
import json
import ruamel.yaml
import sys
import time
import base64

from jinja2 import Environment, FileSystemLoader
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
file_loader = FileSystemLoader('/prd/API/templates')
env = Environment(extensions=['jinja2.ext.loopcontrols'],loader=file_loader,trim_blocks=True)

web_pass = sys.argv[1]
nf = sys.argv[2]

message_bytes = clspass.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
clspass_en = base64_bytes.decode('ascii')

######## Fetch from WebForm #############
url = "https://tele-asset-api.herokuapp.com/login"
headers={'Content-Type': 'application/json'}
data = {
    "usernameOrEmail": "admin",
    "password": web_pass
}

response = requests.post(url, json=data, headers=headers, verify=False)
token = response.json()['accessToken']
token = "Bearer "+ token
headers={'Authorization': token, 'accept': 'application/json'}

url3="https://tele-asset-api.herokuapp.com/jenkinsapi/assets"
cluster3 = requests.get(url3, headers=headers, verify=False)
data2 = cluster3.json()
with open("/tmp/Anu/A.json", "w") as outfile:
    json_object = json.dumps(data2, indent = 4)
    outfile.write(json_object)
for i in range(len(data2['items'])):
    if (data2['items'][i]['nfName']) == nf:
        nf_id=(data2['items'][i]['assetId'])

url2="https://tele-asset-api.herokuapp.com/jenkinsapi/assets/"+str(nf_id)
cluster2 = requests.get(url2, headers=headers, verify=False)
web_input = cluster2.json()
with open("/tmp/Anu/B.json", "w") as outfile:
    json_object = json.dumps(web_input, indent = 4)
    outfile.write(json_object)

print("Script processing complete...")