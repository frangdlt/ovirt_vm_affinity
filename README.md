# ovirt_vm_affinity repository

Simple ovirt_vm_affinity Ansible module that allows creating and removing VM affinity
rules in oVirt/RHEV 3.x .
 
## REQUIREMENTS

ovirt-engine-sdk-python needs to exist on the target node so that would typically be your engine host.

An oVirt/Red Hat Enterprise Virtualization manager 3.x (this module is **not** suitable for using in RHV 4.x)

## BASIC TESTING

```
ansible-playbook -i your-rhev-manager, test_affinity_groups.yml
```

Sample playbook snippet:

```
  - name: ensure affinity group does not exist
    ovirt_vm_affinity:
      url: https://rhevm.example.com/ovirt-engine/api
      user: admin@internal
      password: unix1234
      cluster: "Default"
      name: "mygroup1"
      state: absent

  - name: create affinity group
    ovirt_vm_affinity:
      url: https://rhevm.example.com/ovirt-engine/api
      user: admin@internal
      password: unix1234
      cluster: "Default"
      name: "mygroup1"
      state: present
      positive: false
      enforcing: true
      members: "vm1,vm2"
```
