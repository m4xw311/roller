import sys
import yaml
import jinja2
import yamlordereddictloader
import jinja2schema
from jinja2schema import model
from termcolor import colored
def run(rollerScript):
  validateChangeScript(rollerScript, "deploy")
  validateChangeScript(rollerScript, "rollback")

def validateChangeScript(rollerScript, operation, parentChange={}, parentChangeGroup={}, depth=0, data={}):
  changeScript = yaml.load(file(rollerScript,'r'), Loader=yamlordereddictloader.Loader)
  changeGroups=changeScript["changeGroups"]

  if operation == "deploy":
    for changeGroup in changeGroups:
      for change in changeGroup["changes"]:
        validateChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript, data)
  elif operation == "rollback":
    for changeGroup in reversed(changeGroups):
      for change in reversed(changeGroup["changes"]):
        validateChange(change, changeGroup, operation, parentChange, parentChangeGroup, depth, rollerScript, data)

def validateChange(change, changeGroup, operation, parentChange={}, parentChangeGroup={}, depth=0, rollerScript=None, data={}):
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

  if "deploySuccessIf" in change:
    deploySuccessIf=change["deploySuccessIf"]
  elif "deploySuccessIf" in changeGroup:
    deploySuccessIf=changeGroup["deploySuccessIf"]
  elif "deploySuccessIf" in parentChange:
    deploySuccessIf=parentChange["deploySuccessIf"]
  elif "deploySuccessIf" in parentChangeGroup:
    deploySuccessIf=parentChangeGroup["deploySuccessIf"]
  else:
    deploySuccessIf=None

  if "rollbackSuccessIf" in change:
    rollbackSuccessIf=change["rollbackSuccessIf"]
  elif "rollbackSuccessIf" in changeGroup:
    rollbackSuccessIf=changeGroup["rollbackSuccessIf"]
  elif "rollbackSuccessIf" in parentChange:
    rollbackSuccessIf=parentChange["rollbackSuccessIf"]
  elif "rollbackSuccessIf" in parentChangeGroup:
    rollbackSuccessIf=parentChangeGroup["rollbackSuccessIf"]
  else:
    rollbackSuccessIf=None

  if "deploySkipIf" in change:
    deploySkipIf=change["deploySkipIf"]
  elif "deploySkipIf" in changeGroup:
    deploySkipIf=changeGroup["deploySkipIf"]
  elif "deploySkipIf" in parentChange:
    deploySkipIf=parentChange["deploySkipIf"]
  elif "deploySkipIf" in parentChangeGroup:
    deploySkipIf=parentChangeGroup["deploySkipIf"]
  else:
    deploySkipIf=None

  if "rollbackSkipIf" in change:
    rollbackSkipIf=change["rollbackSkipIf"]
  elif "rollbackSkipIf" in changeGroup:
    rollbackSkipIf=changeGroup["rollbackSkipIf"]
  elif "rollbackSkipIf" in parentChange:
    rollbackSkipIf=parentChange["rollbackSkipIf"]
  elif "rollbackSkipIf" in parentChangeGroup:
    rollbackSkipIf=parentChangeGroup["rollbackSkipIf"]
  else:
    rollbackSkipIf=None

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
    validateChangeScript(includeScript, operation, change, changeGroup, depth+1, data)
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
      undefinedVariables=jinja2schema.infer(captureValue)
      for key,value in undefinedVariables.iteritems():
        if dataNotDefined(key,value,data):
          print "Variable " + colored(dataNotDefined(key,value,data), 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
          sys.exit(4)
      captureData[captureKey]={ 'pre': { 'out': "<stdout>", 'err': "<stderr>", 'ret': "<return code>" } }
      data.update(captureData)
# END
  if operation == "rollback" and rollback != None and rollbackSkipIf != None:
    rollbackSkipIf=jinja2.Template("{{ " + rollbackSkipIf + " }}").render(data)
    undefinedVariables=jinja2schema.infer(rollbackSkipIf)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)
  elif operation == "deploy" and deploy !=None and deploySkipIf != None :
    deploySkipIf=jinja2.Template("{{ " + deploySkipIf + " }}").render(data)
    undefinedVariables=jinja2schema.infer(deploySkipIf)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)

# For situations where the value of a variable would contain a jinja2 reference to another variable
# BEGIN
#      Rendering jinja2 repeatedly until no change observed on further rendering
  if operation == "deploy" and deploy !=None:
    deploy=jinja2.Template(deploy).render(data)
    prev=""
    while prev!=deploy:
      prev=deploy
      deploy=jinja2.Template(deploy).render(data)
    undefinedVariables=jinja2schema.infer(deploy)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)
  if operation == "rollback" and rollback != None:
    rollback=jinja2.Template(rollback).render(data)
    prev=""
    while prev!=rollback:
      prev=rollback
      rollback=jinja2.Template(rollback).render(data)
    undefinedVariables=jinja2schema.infer(rollback)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)
      else:
        print value
# END

# For executing the change
# BEGIN
#      Generating the execution script for the change, granting execute on it and executing it
  deployData={}
  rollbackData={}
  if operation == "rollback" and rollback != None:
    rollbackData['rollback']={ 'out': "<stdout>", 'err': "<stderr>", 'ret': "<return code>" }
    data.update(rollbackData)
  elif operation == "deploy" and deploy !=None:
    deployData['deploy']={ 'out': "<stdout>", 'err': "<stderr>", 'ret': "<return code>" }
    data.update(deployData)
# END

# Execute capture after change
# BEGIN
  if capture != None:
    for captureKey, captureValue in capture.iteritems():
      captureValue=jinja2.Template(captureValue).render(data)
      undefinedVariables=jinja2schema.infer(captureValue)
      for key,value in undefinedVariables.iteritems():
        if dataNotDefined(key,value,data):
          print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
          sys.exit(4)
      captureData[captureKey].update({ 'post': { 'out': "<stdout>", 'err': "<stderr>", 'ret': "<return code>" } })
      data.update(captureData)
# END
  if operation == "rollback" and rollback != None and rollbackSuccessIf != None:
    rollbackSuccessIf=jinja2.Template("{{ " + rollbackSuccessIf + " }}").render(data)
    undefinedVariables=jinja2schema.infer(rollbackSuccessIf)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)
  elif operation == "deploy" and deploy !=None and deploySuccessIf != None:
    deploySuccessIf=jinja2.Template("{{ " + deploySuccessIf + " }}").render(data) 
    undefinedVariables=jinja2schema.infer(deploySuccessIf)
    for key,value in undefinedVariables.iteritems():
      if dataNotDefined(key,value,data):
        print "Variable " + colored(key, 'red', attrs=['bold']) + " not defined for " + colored(captureValue, 'cyan', attrs=['bold']) + " in " + colored(name + " : " + groupName + " : " + rollerScript, 'green', attrs=['bold'])
        sys.exit(4)

def dataNotDefined(key,value,data, prev=""):
  if key not in data:
    return prev + key
  elif type(value) == model.Scalar:
    return False
  else:
    for k, v in value.iteritems(): 
      return dataNotDefined(k, v, data[key], prev + key + ".")
