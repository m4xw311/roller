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

  changeScript = yaml.load(file(rollerScript,'r'))
  changeGroups=changeScript["changeGroups"]

  if operation == "deploy":
    for changeGroup in changeGroups:
      for change in changeGroup["changes"]:
        generateChange(change, changeGroup, operation)
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        generateChange(change, changeGroup, operation)


def generateChange(change, changeGroup, operation):
  target=changeGroup["target"] if "target" not in change else change["target"]
  deploy=changeGroup["deploy"] if "deploy" not in change else change["deploy"]
  rollback=changeGroup["rollback"] if "rollback" not in change else change["rollback"]
  print hashlib.sha512(deploy).hexdigest()
  print hashlib.sha512(rollback).hexdigest()
  print target + "<<EOF"
  if operation == "rollback":
    print change["rollback"]
  elif operation == "deploy":
    print change["deploy"]
  print "EOF"

if __name__ == "__main__":
  main(sys.argv[1:])
