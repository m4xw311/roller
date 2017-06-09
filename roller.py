#!/usr/bin/python
import sys, getopt
import yaml
import hashlib

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

  processChangeScript(rollerScript, operation)

def processChangeScript(rollerScript, operation):
  changeScript = yaml.load(file(rollerScript,'r'))
  changeGroups=changeScript["changeGroups"]

  if operation == "deploy":
    for changeGroup in changeGroups:
      for change in changeGroup["changes"]:
        processChange(change, changeGroup, operation)
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        processChange(change, changeGroup, operation)

def processChange(change, changeGroup, operation):
  if "target" in change:
    target=change["target"]
  elif "target" in changeGroup:
    target=changeGroup["target"]
  else:
    target=None
  if "deploy" in change:
    deploy=change["deploy"]
  elif "deploy" in changeGroup:
    deploy=changeGroup["deploy"]
  else:
    deploy=None
  if "rollback" in change:
    rollback=change["rollback"]
  elif "rollback" in changeGroup:
    rollback=changeGroup["rollback"]
  else:
    rollback=None
  if deploy == None:
    if rollback == None:
      return
    else:
      print hashlib.sha512(rollback).hexdigest()
  else:
    print hashlib.sha512(deploy).hexdigest()
  if operation == "rollback" and rollback != None:
    print target + "<<EOF"
    print change["rollback"]
    print "EOF"
  elif operation == "deploy" and deploy !=None:
    print target + "<<EOF"
    print change["deploy"]
    print "EOF"

if __name__ == "__main__":
  main(sys.argv[1:])
