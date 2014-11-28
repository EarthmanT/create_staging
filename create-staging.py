#!/usr/bin/python

import subprocess, json

dry_run = True
desc = "\"python created this ami\""
path_to_which = "/usr/bin/which" #INSERT THE PATH TO YOUR WHICH COMMAND
cmd_for_which = "aws" #INSERT THE COMMAND YOU NEED TO RUN

#This takes any number of arguments, and returns an array with the types of the arguments in order.
def argument_types(*arg):
  types = []
  args = locals()
  for a,r in args.items():
    for g in r:
      types.append(type(g).__name__)
  return types

# This gets the output of any command.
def get_cmd_output(cmd):
  types = argument_types(cmd)
  if types[0] != 'list':
    return "Variable cmd is not of correct type list in get_cmd_output()"
    exit(1)
  try:
    run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
  except OSError:
    print "Input Error: Command not entered as an array."
    exit(1)    
  out, err = run.communicate()
  output = out.rstrip() + err.rstrip()
  return output
  exit(0)

# This returns AWS Command Credentials and Configuration in an array
def aws_configure_get(cmd,profile,data):
  types = argument_types(cmd,profile,data)
  if types[0] != 'list':
    return "Variable cmd is not of correct type list in aws_configure_get()"
    exit(1)
  elif types[1] != 'str'
    return "Variable profile is not of correct type str in aws_configure_get()"
    exit(1)
  elif types[2] != 'list':
    return "Variable data is not of correct type list in aws_configure_get()"
    exit(1)
  out_array = []
  for e in data:
    e = profile + "." + e
    cmd.append(e)
    output = get_cmd_output(cmd)
    cmd.pop()
    output = output.rstrip()
    out_array.append(output)
  return out_array
  exit(0)

# This retrieves the ID, Name, IPs, and DNS Names of all Running instances.
def get_instances(cmd,profile,region):
  types = argument_types(cmd,profile,region)
  if types[0] != 'list':
    return "Variable cmd is not of correct type list in aws_configure_get()"
    exit(1)
  elif types[1] != 'str':
    return "Variable profile is not of correct type str in aws_configure_get()"
    exit(1)
  elif types[2] != 'str':
    return "Variable data is not of correct type str in aws_configure_get()"
    exit(1)
  args = ['--profile',profile,'--region',region]
  for arg in args:
    cmd.append(arg)
  blob = get_cmd_output(cmd)
  data = json.loads(blob)
  instances = []
  for x in range(len(data['Reservations'])):
    instance_data = []
    for n in range(len(data['Reservations'][x]['Instances'])):
      id = json.dumps(data['Reservations'][x]['Instances'][n]['InstanceId']).replace("\"","")
      name = json.dumps(data['Reservations'][x]['Instances'][n]['Tags'][0]['Value']).replace("\"","")
      pubdns = json.dumps(data['Reservations'][x]['Instances'][n]['PublicDnsName']).replace("\"","")
      pubip = json.dumps(data['Reservations'][x]['Instances'][n]['PublicIpAddress']).replace("\"","")
      privdns = json.dumps(data['Reservations'][x]['Instances'][n]['PrivateDnsName']).replace("\"","")
      privip = json.dumps(data['Reservations'][x]['Instances'][n]['PrivateIpAddress']).replace("\"","")
      instance_data.append(id)
      instance_data.append(name)
      instance_data.append(pubdns)
      instance_data.append(pubip)
      instance_data.append(privdns)
      instance_data.append(privip)      
    instances.append(instance_data)
  return instances
  exit(0)

#Get the ID of the live instance that you want to use as a ami image
def get_instance_id(choices):
  id = []
  name = []
  print "Choose the id of the instance you would like to use as a base image for your AMI (ex. type just the number 1 or 2):"
  print "    ID\t\tNAME\t"
  c = 0
  ichoice = 0
  schoice = "s"
  for x in choices:
    c = c + 1
    id.append(x[0])
    name.append(x[1])
    print "("+str(c)+")", x[0], x[1]
    id.pop()
    name.pop()
  while True:
    ichoice = int(raw_input("Enter the number of your choice: "))
    schoice = raw_input("You entered " + str(ichoice) + ". Is that right? (y or n)")
    if schoice == 'n':
      continue
    else:
      break
  output = choices[ichoice - 1][0]
  return output
  exit(0)

# Creates the AMI Image and returns the image id or an error string
def create_image(cmd,id,desc,profile,region):
  if dry_run:
    args = ['--dry-run','--instance-id', id, '--name', "ami-" + id, '--description', desc, '--profile', profile, '--region', region]
  else:
    args = ['--instance-id', id, '--name', "ami-" + id, '--description', desc, '--profile', profile, '--region', region]
  for arg in args:
    cmd.append(arg)
  if dry_run:
    data = get_cmd_output(cmd)
    data = json.loads(json_string)
    output = data['ImageId']
  else:
    output = get_cmd_output(cmd)
  return output

# Create the instance from ami the machine
def create_instance(cmd,amiid,key,group,profile,region):
  if dry_run:
    args =  ['--dry-run', '--image-id', imageid, '--key-name', key, '--security-groups', group]
  else:
    args =  ['--image-id', amiid, '--key-name', key, '--security-groups', group]
  for arg in args:
    cmd.append(arg)
  output = get_cmd_output(cmd)
  return cmd

# A very long way to do something simple, but we use the get_cmd_output() method in other places, so...
command = path_to_which, cmd_for_which
path_to_aws = get_cmd_output(command)

aws_profile_name = "yaelww" #DEFAULT or NAMED PROFILE
aws_cmd_array = [path_to_aws, 'configure', 'get']
aws_configure_data_array = ['aws_access_key_id','aws_secret_access_key','region']

key,secret,region = aws_configure_get(aws_cmd_array,aws_profile_name,aws_configure_data_array)

aws_cmd_array = [path_to_aws, 'ec2', 'describe-instances']
instances = get_instances(aws_cmd_array,aws_profile_name,region)

aws_cmd_array = [path_to_aws, 'ec2', 'create-image']
ami_id = create_image(aws_cmd_array,instance_id,desc,aws_profile_name,region)

#need error checking in create_image

aws_cmd_array = [path_to_aws, 'ec2', 'run-instances']
create_instance(aws_cmd_array,ami_id,key,group,profile,region) #get keyfile path, get optional arguement method directions