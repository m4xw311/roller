#!/usr/bin/python
import sys, getopt
import yaml
import hashlib
import os
import jinja2
from subprocess import Popen, PIPE

def main(argv):
  rollerScript = None
  operation = None
  try:
    opts, args = getopt.getopt(argv,"hs:o:",["rollerScript=","operation="])
  except getopt.GetoptError:
    print 'roller.py -s <rollerScript> -o <operation>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'roller.py -s <rollerScript> -o <operation>'
      sys.exit(0)
    elif opt in ("-s", "--rollerScript"):
      rollerScript = arg
    elif opt in ("-o", "--operation"):
      operation = arg
    else:
      print 'roller.py -s <rollerScript> -o <operation>'
      sys.exit(1)

  if rollerScript == None or operation == None:
    print 'roller.py -s <rollerScript> -o <operation>'
    sys.exit(1)

  preRequisites()

  processChangeScript(rollerScript, operation)

def preRequisites():
  if not os.path.exists("./.tmp"):
    os.makedirs("./.tmp")

def processChangeScript(rollerScript, operation, parentChange={}, parentChangeGroup={}, depth=0, data={}):
  changeScript = yaml.load(file(rollerScript,'r'))
  changeGroups=changeScript["changeGroups"]

  if operation == "deploy":
    for changeGroup in changeGroups:
      for change in changeGroup["changes"]:
        processChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript, data)
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        processChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript, data)

def processChange(change, changeGroup, operation, parentChange={}, parentChangeGroup={}, depth=0, rollerScript=None, data={}):
  if "name" in change:
    name=change["name"]

  if "name" in changeGroup:
    groupName=changeGroup["name"]

  if "target" in change:
    target=change["target"]
  elif "target" in changeGroup:
    target=changeGroup["target"]
  elif "target" in parentChange:
    target=parentChange["target"]
  elif "target" in parentChangeGroup:
    target=parentChangeGroup["target"]
  else:
    target=None

  if "deploy" in change:
    deploy=change["deploy"]
  elif "deploy" in changeGroup:
    deploy=changeGroup["deploy"]
  elif "deploy" in parentChange:
    deploy=parentChange["deploy"]
  elif "deploy" in parentChangeGroup:
    deploy=parentChangeGroup["deploy"]
  else:
    deploy=None

  if "rollback" in change:
    rollback=change["rollback"]
  elif "rollback" in changeGroup:
    rollback=changeGroup["rollback"]
  elif "rollback" in parentChange:
    rollback=parentChange["rollback"]
  elif "rollback" in parentChangeGroup:
    rollback=parentChangeGroup["rollback"]
  else:
    rollback=None

  if "capture" in change:
    capture=change["capture"]
  elif "capture" in changeGroup:
    capture=changeGroup["capture"]
  elif "capture" in parentChange:
    capture=parentChange["capture"]
  elif "capture" in parentChangeGroup:
    capture=parentChangeGroup["capture"]
  else:
    capture=None

  if "data" in parentChangeGroup:
    data.update(parentChangeGroup["data"])
  if "data" in parentChange:
    data.update(parentChange["data"])
  if "data" in changeGroup:
    data.update(changeGroup["data"])
  if "data" in change:
    data.update(change["data"])

  if "include" in change:
    includeScript=change["include"]
  elif "include" in changeGroup:
    includeScript=changeGroup["include"]
  else:
    includeScript=None

# Nested changeScripts : including changeScripts in changeScripts
# BEGIN
#      Recursive processing of nested changeScripts 
  if includeScript != None:
    processChangeScript(includeScript, operation, change, changeGroup, depth+1, data)
    return
# END

# Do nothing if a change contains no include, deploy or rollback
# BEGIN
  if deploy == None:
    if rollback == None:
      return
# END

# Execute capture before change
# BEGIN
  captureData={}
  if capture != None:
    for captureKey, captureValue in capture.iteritems():
      captureFile=open("./.tmp/"+hashlib.sha512(captureValue).hexdigest(),"w")
      captureFile.write("#!/bin/bash\n")
      captureFile.write(target + "<<" + hashlib.sha512(captureValue).hexdigest() + "\n")
      captureFile.write(captureValue + "\n")
      captureFile.write(hashlib.sha512(captureValue).hexdigest())
      captureFile.close()
      os.system("chmod a+x ./.tmp/"+hashlib.sha512(captureValue).hexdigest())
      process = Popen("./.tmp/"+hashlib.sha512(captureValue).hexdigest(), stdout=PIPE, stderr=PIPE)
      captureOutput, captureError = process.communicate()
      captureData[captureKey]={ 'pre': { 'out': captureOutput, 'err':captureError }}
    data.update(captureData)
# END

# For situations where the value of a variable would contain a jinja2 reference to another variable
# BEGIN
#      Rendering jinja2 repeatedly until no change observed on further rendering
  deploy=jinja2.Template(deploy).render(data)
  prev=""
  while prev!=deploy:
    prev=deploy
    deploy=jinja2.Template(deploy).render(data)
    
  rollback=jinja2.Template(rollback).render(data)
  prev=""
  while prev!=rollback:
    prev=rollback
    rollback=jinja2.Template(rollback).render(data)
# END

# For executing the change
# BEGIN
#      Generating the execution script for the change, granting execute on it and executing it
  if operation == "rollback" and rollback != None:
    changeFile=open("./.tmp/"+hashlib.sha512(rollback).hexdigest(),"w")
    changeFile.write("#!/bin/bash\n")
    changeFile.write(target + "<<" + hashlib.sha512(rollback).hexdigest() + "\n")
    changeFile.write(rollback + "\n")
    changeFile.write(hashlib.sha512(rollback).hexdigest())
    changeFile.close()
    os.system("chmod a+x ./.tmp/"+hashlib.sha512(rollback).hexdigest())
    os.system("./.tmp/"+hashlib.sha512(rollback).hexdigest())
  elif operation == "deploy" and deploy !=None:
    changeFile=open("./.tmp/"+hashlib.sha512(rollback).hexdigest(),"w")
    changeFile.write("#!/bin/bash\n")
    changeFile.write(target + "<<" + hashlib.sha512(deploy).hexdigest() + "\n")
    changeFile.write(deploy + "\n")
    changeFile.write(hashlib.sha512(deploy).hexdigest())
    changeFile.close()
    os.system("chmod a+x ./.tmp/"+hashlib.sha512(rollback).hexdigest())
    os.system("./.tmp/"+hashlib.sha512(rollback).hexdigest())
# END

# Execute capture after change
# BEGIN
  captureData={}
  if capture != None:
    for captureKey, captureValue in capture.iteritems():
      captureFile=open("./.tmp/"+hashlib.sha512(captureValue).hexdigest(),"w")
      captureFile.write("#!/bin/bash\n")
      captureFile.write(target + "<<" + hashlib.sha512(captureValue).hexdigest() + "\n")
      captureFile.write(captureValue + "\n")
      captureFile.write(hashlib.sha512(captureValue).hexdigest())
      captureFile.close()
      os.system("chmod a+x ./.tmp/"+hashlib.sha512(captureValue).hexdigest())
      process = Popen("./.tmp/"+hashlib.sha512(captureValue).hexdigest(), stdout=PIPE, stderr=PIPE)
      captureOutput, captureError = process.communicate()
      captureData[captureKey]={ 'post': { 'out': captureOutput, 'err':captureError }}
    data.update(captureData)
# END

# For providing execution log
# BEGIN
#      Displaying key information about each change being executed in json format
  sys.stdout.write("{")
  sys.stdout.write("name:\"" + name + "\", ")
  sys.stdout.write("group:\"" + groupName + "\", ")
  sys.stdout.write("script:\"" + rollerScript + "\", ")
  sys.stdout.write("depth:" + str(depth) + "," )
  sys.stdout.write("operation:" + operation)
  sys.stdout.write("}\n")
# END

if __name__ == "__main__":
  main(sys.argv[1:])
