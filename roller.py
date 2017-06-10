#!/usr/bin/python
import sys, getopt
import yaml
import hashlib
import os
import jinja2

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

def processChangeScript(rollerScript, operation, parentChange={}, parentChangeGroup={}, depth=0):
  changeScript = yaml.load(file(rollerScript,'r'))
  changeGroups=changeScript["changeGroups"]

  if operation == "deploy":
    for changeGroup in changeGroups:
      for change in changeGroup["changes"]:
        processChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript)
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        processChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript)

def processChange(change, changeGroup, operation, parentChange={}, parentChangeGroup={}, depth=0, rollerScript=None):
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

  data={}
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

  if includeScript != None:
    processChangeScript(includeScript, operation, change, changeGroup, depth+1)
    return

  if deploy == None:
    if rollback == None:
      return

  deploy=jinja2.Template(deploy).render(data)
  rollback=jinja2.Template(rollback).render(data)

  sys.stdout.write("{")
  sys.stdout.write("name:\"" + name + "\", ")
  sys.stdout.write("group:\"" + groupName + "\", ")
  sys.stdout.write("script:\"" + rollerScript + "\", ")
  sys.stdout.write("depth:" + str(depth))

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

  sys.stdout.write("}\n")

if __name__ == "__main__":
  main(sys.argv[1:])
