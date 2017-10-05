#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime
from ovirtsdk.api import API
from ovirtsdk.xml import params
from time import sleep

DOCUMENTATION = '''
module: ovirt_vm_affinity
short_description: Creates affinity groups in a RHV/oVirt cluster.
description:
    - Longer description of the module
version_added: "0.1"
author: "Fran Garcia, @frangdlt"
notes:
    - Details at https://github.com/frangdlt/ovirt_vm_affinity
requirements:
    - ovirt sdk'''

EXAMPLES = '''
- name: Create Ovirt affinity group
  ovirt_vm_affinity:
   url: https://127.0.0.1/ovirt-engine/api
   user: admin@internal
   password: unix1234
   cluster: my_cluster
   name: my_group
   description: my_group_description
   state: present
   positive: true  # polarity . affinity=true ; antiaffinity=false
   enforcing: true
   members: "vm1,vm2"
'''

changed=False
module=""

def affinity_group_exists(api, cluster, name):
    c = api.clusters.get(name=cluster)
    ag = c.affinitygroups.get(name=name)
    return not ag is None 

def delete_affinity_group(api, cluster, name):
    global changed
    if affinity_group_exists(api, cluster, name):
      c = api.clusters.get(name=cluster)
      ag = c.affinitygroups.get(name=name)
      ag.delete()
      changed=True

def create_affinity_group(api, cluster, name, description, positive, enforcing, members):
    global changed
    global module
    positive = positive in ["True", 'true']
    enforcing = enforcing in ["True", 'true']
    c = api.clusters.get(name=cluster)
    ag = c.affinitygroups.add(params.AffinityGroup(name=name, positive=positive, enforcing=enforcing))
    if members is None:
      module.fail_json(msg='members is not initialized')
    for name in members:
      vm = api.vms.get(name=name)
      if vm is None:
        module.fail_json(msg='cannot find vm: %s' % (name))
      ag.vms.add(vm)
    changed = True

def main():
    global module
    argument_spec = {
        "url": {"default": 'https://127.0.0.1/ovirt-engine/api', "required": False, "type": "str"},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "cluster":  {"required": True, "type": "str"},
        "name": {"required": True, "type": "str"},
        "description": { "default": '', "required": False, "type": "str"},
        "state": {"required": True, "type": "str"},
        "positive": { "default": 'true', "required": False, "type": "str"},
        "enforcing": { "default": 'true', "required": False, "type": "str"},
        "members": { "default": '', "required": False, "type": "str"}
    }
    module = AnsibleModule(argument_spec=argument_spec)
    url = module.params['url']
    user = module.params['user']
    password = module.params['password']
    name = module.params['name']
    cluster = module.params['cluster']
    description = module.params['description']
    state = module.params['state']
    members = module.params['members']

    api = API(url=url, username=user, password=password, insecure=True)

    if name == '' or cluster == '' or state not in ["present", "absent"]:
      module.fail_json(msg='name, cluster or state parameters are missing or invalid')
   
    if state == "absent":
      delete_affinity_group(api, cluster, name)

    if state == "present":
      positive = module.params['positive']
      enforcing = module.params['enforcing']
      vms = module.params['members'].split(',')
      if module.params['members'] == '' or len(vms) == 0:
        module.fail_json(msg='vm parameter is required and should be populated')
      delete_affinity_group(api, cluster, name) 
      create_affinity_group(api, cluster, name, description, positive, enforcing, vms)

    module.exit_json(changed=changed, skipped=False, meta="")

if __name__ == '__main__':
    main()
