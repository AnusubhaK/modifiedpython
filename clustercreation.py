import requests
import json
import ruamel.yaml
import sys
import base64
import time

from jinja2 import Environment, FileSystemLoader
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
file_loader = FileSystemLoader('/prd/API/templates')
env = Environment(extensions=['jinja2.ext.loopcontrols'],loader=file_loader,trim_blocks=True)

#clspass = sys.argv[1]
tca = "10.41.3.8"
#tcapass = sys.argv[3]
#folder = sys.argv[4]
#net = sys.argv[5]
#RP = sys.argv[6]
#wkcls = sys.argv[7]
#mgtid = sys.argv[7]
#tcp = sys.argv[8]
web_pass = sys.argv[1]
nf = sys.argv[2]
#filecls= sys.argv[11]
'''
message_bytes = clspass.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
clspass_en = base64_bytes.decode('ascii')

######## Fetch Session ID #############
url = "https://"+tca+"/hybridity/api/sessions"
data = {
  "username": "administrator@vsphere.local",
  "password": tcapass
}
response = requests.post(url, json=data, verify=False)
out=response.headers["x-hm-authorization"]
headers_tca={'x-hm-authorization': out}
########################################
'''
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
for i in range(len(data2['items'])):
    if (data2['items'][i]['nfName']) == nf:
        nf_id=(data2['items'][i]['assetId'])

url2="https://tele-asset-api.herokuapp.com/jenkinsapi/assets/"+str(nf_id)
cluster2 = requests.get(url2, headers=headers, verify=False)
#output2 = json.loads(cluster2.text)
web_input = cluster2.json()
print(web_input)
for i in range(len(web_input['categories'])):
    if (web_input['categories'][i].get('categoryName')) == "capacity":
        cap_idx=i
        print(cap_idx)
        for p in range(len(web_input['categories'][i]['fields'])):
            if (web_input['categories'][i]['fields'][p].get('fieldName')) == "Cluster Instance Name":
                ins_idx=p
                for n in range(len(web_input['categories'][i]['fields'][p]['children'])):
                    if (web_input['categories'][i]['fields'][p]['children'][n].get('fieldValue')) == "Workload" or (web_input['categories'][i]['fields'][p]['children'][n].get('fieldValue')) == "Management":
                        wrk_cls_idx=n
                        for m in range(len(web_input['categories'][i]['fields'][p]['children'][n]['children'])):
                            if (web_input['categories'][i]['fields'][p]['children'][n]['children'][m].get('fieldValue')) == "Master":
                                mas_idx=m
                            elif (web_input['categories'][i]['fields'][p]['children'][n]['children'][m].get('fieldValue')) == "Worker":
                                wrk_idx=m
#print(cap_idx,ins_idx,wrk_cls_idx,mas_idx,wrk_idx)
for i in range(len(web_input['categories'])):
    if (web_input['categories'][i].get('categoryName')) == "platform":
        plat_idx=i
for i in range(len(web_input['categories'])):
    if (web_input['categories'][i].get('categoryName')) == "dependency":
        dep_idx=i
#print(plat_idx,dep_idx)
'''
############Save Cluster Name into Jenkins Variable###############
for n in range(len(web_input['categories'][cap_idx]['fields'])):
    if web_input['categories'][cap_idx]['fields'][n]['fieldName'] == 'Cluster Instance Name':
        cluster_name = web_input['categories'][cap_idx]['fields'][n]['fieldValue']
#print(cluster_name)
filename = "/tmp/"+str(filecls)
file3 = open(filename, 'w')
file3.write(cluster_name)
file3.close()

#########################################
######Template Creation##########
url1="https://"+tca+"/hybridity/api/infra/cluster-templates"

template = env.get_template('template_web.yaml')
output = template.render(data=web_input, cap_idx=cap_idx, ins_idx=ins_idx, wrk_cls_idx=wrk_cls_idx, mas_idx=mas_idx, wrk_idx=wrk_idx, plat_idx=plat_idx, dep_idx=dep_idx)
file1 = open('/prd/API/input_yaml.yaml', 'w')
file1.write(output)
file1.close()
in_file = '/prd/API/input_yaml.yaml'
out_file = '/prd/API/output.json'

yaml = ruamel.yaml.YAML(typ='safe')
with open(in_file) as fpi:
    data = yaml.load(fpi)
with open(out_file, 'w') as fpo:
    json.dump(data, fpo, indent=2)
file = open('/prd/API/output.json')
data1 = json.load(file)
cluster = requests.post(url1, json=data1, headers=headers_tca, verify=False)
if cluster:
    output=cluster.json()
    template_id=output['id']
    print ("Cluster Template Creation....... Success.")
    print(" Template ID is ",template_id)
else:
    print('"Cluster Template Creation Failed!!!!!!!')
    print(cluster.text)
################################
###### Fetch Datastore & Cluster from Capacity Report ####################
file = open('/prd/TEF/capacityfinalreport/refout.json')
data1 = json.load(file)
CLS = data1['WorkerNodeAllocation'][0]['ClusterName']
DS = data1['WorkerNodeAllocation'][0]['Datastore']


##########################################################################
'''
###### Fetch kubeconfig file from Management Cluster #######
url5="https://"+tca+"/hybridity/api/infra/k8s/clusters/"+mgtid
cluster = requests.get(url5, headers=headers_tca, verify=False)
output=cluster.json()
STAT = output['kubeConfig']
out=base64.b64decode(STAT)
file2 = open('/tmp/config', 'wb')
file2.write(out)
file2.close()

'''

##########################################################################
######Cluster Creation##########
url1="https://"+tca+"/hybridity/api/infra/k8s/clusters"
template = env.get_template('cluster_web.yaml')
output = template.render(data=web_input, DS=DS, CLS=CLS, clspass=clspass_en, clusterTempId=template_id, folder=folder, net=net, RP=RP, mgtid=mgtid, tcp=tcp, cap_idx=cap_idx, ins_idx=ins_idx, wrk_cls_idx=wrk_cls_idx, mas_idx=mas_idx, wrk_idx=wrk_idx, plat_idx=plat_idx)
file1 = open('input_yaml.yaml', 'w')
file1.write(output)
file1.close()
in_file = 'input_yaml.yaml'
out_file = 'output.json'

yaml = ruamel.yaml.YAML(typ='safe')
with open(in_file) as fpi:
    data = yaml.load(fpi)
with open(out_file, 'w') as fpo:
    json.dump(data, fpo, indent=2)
file = open('/prd/API/output.json')
data1 = json.load(file)
cluster = requests.post(url1, json=data1, headers=headers_tca, verify=False)
if cluster:
    output=cluster.json()
    print ("Cluster Creation is initiated Successfully")
    #print(output)
    clusterid=output['id']
else:
    print('"Cluster Creation Failed!!!!!!!')
    print(cluster.text)
###############################

url2="https://"+tca+"/hybridity/api/infra/k8s/clusters/"+clusterid
timeout = time.time() + 60*45  # 45 minutes from now
n = 45
while True:
    cluster = requests.get(url2, headers=headers_tca, verify=False)
    output=cluster.json()
    STAT = output['status']
    ACTCNT = output['activeTasksCount']

    if STAT == "ACTIVE":
        print ("Cluster is Ready")
        break
    elif time.time() > timeout:
        print ("Cluster is taking time...Please check")
        break

    elif STAT == "NOT ACTIVE" and ACTCNT > 0:
        print ("Cluster deployment is in progress....Will wait for "+str(n)+" minutes")
        time.sleep(300)
        n = n - 5
    elif STAT != "ACTIVE" or STAT != "NOT ACTIVE" or (STAT == "NOT ACTIVE" and ACTCNT == 0):
        print ("Cluster Creation Failed...Please check")
        break

##########################################################################
###### Fetch kubeconfig file from Management Cluster #######
if (web_input['categories'][cap_idx]['fields'][ins_idx]['children'][wrk_cls_idx].get('fieldValue')) == "Management":
    mgtid = clusterid
url5="https://"+tca+"/hybridity/api/infra/k8s/clusters/"+mgtid
cluster = requests.get(url5, headers=headers_tca, verify=False)
output=cluster.json()
STAT = output['kubeConfig']
out=base64.b64decode(STAT)
file2 = open('/tmp/config', 'wb')
file2.write(out)
file2.close()
'''
