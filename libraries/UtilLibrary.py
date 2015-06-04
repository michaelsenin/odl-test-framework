__author__ = "Basheeruddin Ahmed"
__copyright__ = "Copyright(c) 2014, Cisco Systems, Inc."
__license__ = "New-style BSD"
__email__ = "syedbahm@cisco.com"


import requests
from SSHLibrary import SSHLibrary

import robot

global _cache

#
#Helps in making GET REST calls
#

def get(url, userId=None, password=None):

    headers = {}
    headers['Accept']= 'application/xml'

    # Send the GET request
    session = _cache.switch("CLUSTERING_GET")
    resp = session.get(url,headers=headers)

    # Read the response
    return resp

#
#Helps in making POST REST calls without outputs
#
def nonprintpost(url, userId, password,data):

    headers = {}
    headers['Content-Type'] = 'application/json'
    #headers['Accept']= 'application/xml'

    session = _cache.switch("CLUSTERING_POST")
    resp = session.post(url,data.encode('utf-8'),headers=headers)


    return resp

#
#Helps in making POST REST calls
#
def post(url, userId, password,data):
    print("post request with url "+url)
    print("post request with data "+data)
    headers = {}
    headers['Content-Type'] = 'application/json'
    #headers['Accept']= 'application/xml'
    session = _cache.switch("CLUSTERING_POST")
    resp = session.post(url,data.encode('utf-8'),headers=headers)

    #print (resp.raise_for_status())
    print (resp.headers)

    return resp

#
#Helps in making DELET REST calls
#
def delete(url,userId,password):
    print("delete all resources belonging to url"+url)
    session = _cache.switch("CLUSTERING_DELETE")
    resp=session.delete(url)


# use username and password of controller server for ssh and need
# karaf distribution location like /root/Documents/dist
#
def execute_ssh_command(ip, username, password, command):
    print "executing ssh command"
    lib = SSHLibrary()
    lib.open_connection(ip)
    lib.login(username=username,password=password)
    print "login done"
    lib.execute_command(command)
    print "command executed : " + command
    lib.close_connection()

def startcontroller(ip,username,password,karafhome):
    execute_ssh_command(ip, username, password, karafhome+"/bin/start")

def stopcontroller(ip,username,password,karafhome):
    execute_ssh_command(ip, username, password, karafhome+"/bin/stop")

def clean_journal(ip, username, password, karafHome):
    execute_ssh_command(ip, username, password, "rm -rf " + karafHome + "/journal")

def kill_controller(ip, username, password, karafHome):
    execute_ssh_command(ip, username, password, "ps axf | grep karaf | grep -v grep | awk '{print \"kill -9 \" $1}' | sh")
