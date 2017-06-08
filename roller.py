#!/usr/bin/python
import sys, getopt
import yaml

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
        target=changeGroup["target"] if "target" not in change else change["target"]
        deploy=changeGroup["deploy"] if "deploy" not in change else change["deploy"]
        print target + "<<EOF"
        print deploy
        print "EOF"
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        target=changeGroup["target"] if "target" not in change else change["target"]
        rollback=changeGroup["rollback"] if "rollback" not in change else change["rollback"]
        print target + "<<EOF"
        print change["rollback"]
        print "EOF"

if __name__ == "__main__":
  main(sys.argv[1:])
