# CHSC : Containerized HPC Schedulers in the Cloud

This project implements a Kubernetes controller to run containerized HPC schedulers in the Cloud with autoscaling features. It requires a Kubernetes cluster. This repository contains the code of the controller with all Kubernetes manifests to instantiate containerized HPC schedulers. It should be noticed that for the moment only OAR HPC scheduler is supported. However, we demonstrated that each of the major HPC schedulers (SLURM, OpenPBS and OAR) can grow or shrink dynamically [here](https://link.springer.com/chapter/10.1007/978-3-031-12597-3_13).

### 1. Get your Kubernetes cluster

We supply a functional Kubernetes cluster [here](https://drive.google.com/file/d/1JoVi-pmArjVjWMGiwOzfoW77hcQ3mq5H/view?usp=sharing). Here is the MD5 fingerprint :

```bash
ngreneche@DESKTOP-KSGVO8B:/mnt/d/Offline$ md5sum chsc.ova
9bf5dcbd55dd3e764629abe7879e3b1a  chsc.ova
```

This file is an OVA image that contains our experimentation platform. We use the VirtualBox hypervisor throughout the document, and you can import the OVA file straight to VirtualBox. The machine hosting VirtualBox must be able to run virtual machines that use six vcpus in total. After deploying the OVA image, you get four virtual machines:
 * CHSC-Lab-admin: host the Kubernetes API-Server ;
 * CHSC-Lab-frontal: gateway to connect to the testbed ;
 * CHSC-Lab-node[1,2]: cloud nodes that host our containerized HPC infrastructure.

The virtual machine "CHSC-Lab-frontal" has two network interfaces, one configured as NAT and one as an internal network where all the other virtual machines are plugged. Other virtual machines use "Lab-frontal" as a gateway to access the internet. We also run an internal local domain named "lab.local", such that "CHSC-Lab-frontal" embed a DNS server that redirects all DNS resolution out of "lab.local" to Google public DNS 8.8.8.8. The hosting machine must also reach Github and Docker Hub servers.

Kubernetes installation is based on the basic procedure supplied by Google [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/). We wrote an Ansible deployment based on this procedure. You can find it [here](https://github.com/Nyk0/k8s-ansible).

We defined a port redirection on "CHSC-Lab-frontal" to reach the node from the localhost of your computer on port 2424. Default login/password is root/azerty for all virtual machines. To connect to the "CHSC-Lab-frontal node", type:

```bash
nico@DESKTOP-KSGVO8B:~$ ssh -p 2424 root@localhost
```

Go to the "admin" node :

```bash
root@frontal:~# ssh admin
```

And check that the Kubernetes cluster is running :

```
root@admin:~#  kubectl get nodes
NAME    STATUS   ROLES                  AGE   VERSION
admin   Ready    control-plane,master   48m   v1.22.3
node1   Ready    <none>                 46m   v1.22.3
node2   Ready    <none>                 46m   v1.22.3
```

### 2. Install CHSC requirements

First, clone the repository :

```bash
root@admin:~# git clone https://github.com/Nyk0/chsc.git
```

Then go to "chsc" directory :

```bash
root@admin:~# cd chsc/
```

Create the "oar" Kubernetes namespace and set it as your default namespace :

```bash
root@admin:~/chsc# kubectl create namespace oar
namespace/oar created
```

```bash
root@admin:~/chsc# kubectl config set-context --current --namespace=oar
Context "kubernetes-admin@kubernetes" modified.
```

Set the RBAC policy :

```bash
root@admin:~/chsc# kubectl apply -f misc/rbac/rbac.yaml
clusterrole.rbac.authorization.k8s.io/pods-list-oar created
clusterrolebinding.rbac.authorization.k8s.io/pods-list-oar created
```

Create the PhysicalVolume and the PhysicalVolumeClaim that maps the supplied NFS server that contains user's home directory :

```bash
root@admin:~/chsc# kubectl apply -f misc/nfs/pv-nfs.yaml
persistentvolume/pv-nfs-home created
```

```bash
root@admin:~/chsc# kubectl apply -f misc/nfs/pvc-nfs.yaml
persistentvolumeclaim/pvc-nfs-home created
```

### 3. Instantiate the containerized OAR scheduler

Go to the "oar" directory and run the YAML manifest :

```bash
root@admin:~/chsc# cd oar
```

```bash
root@admin:~/chsc/oar# kubectl apply -f oar.yaml
configmap/oarconf created
service/nodes created
pod/hpc-scheduler created
pod/db-server created
pod/controller created
```

Containerized OAR cluster is creating :

```bash
root@admin:~/chsc/oar# kubectl get pods
NAME            READY   STATUS              RESTARTS   AGE
controller      0/1     ContainerCreating   0          11s
db-server       0/1     ContainerCreating   0          11s
hpc-scheduler   0/1     ContainerCreating   0          11s
```

Wait few seconds for the Pods to be in "Running" state :

```bash
root@admin:~/chsc/oar# kubectl get pods
NAME            READY   STATUS    RESTARTS   AGE
controller      1/1     Running   0          52s
db-server       1/1     Running   0          52s
hpc-scheduler   1/1     Running   0          52s
```

You have three Pods :
 * "controller" runs the controller that enables autoscaling of the containerized OAR scheduler. It will create or remove containerized compute nodes depending on the jobs pending in the queue ;
 * "db-server" is used by containerized OAR to store all its information ;
 * "hpc-scheduler" contains Almighty, the server part of OAR.

No containerized compute nodes are created for the moment.

### 4. Submitting the first job

Open a bash sesssion in "hpc-scheduler" Pod :

```bash
root@admin:~/chsc/oar# kubectl exec -ti hpc-scheduler -- /bin/bash
```
Switch to a regular user :

```bash
root@hpc-scheduler:/# su - nico
```

```bash
nico@hpc-scheduler:~$ id
uid=1000(nico) gid=1000(nico) groups=1000(nico)
```

Check containerized compute nodes status :

```bash
nico@hpc-scheduler:~$ oarnodes -s
hpc-node-0
    1 : Absent (standby)
    2 : Absent (standby)
hpc-node-1
    3 : Absent (standby)
    4 : Absent (standby)
hpc-node-2
    5 : Absent (standby)
    6 : Absent (standby)
```

Nodes are pre-provisioned in an "Absent" state. Go to "oar" directory :

```bash
nico@hpc-scheduler:~$ cd oar/
```

We submit the first job :

```bash
nico@hpc-scheduler:~/oar$ oarsub -S ./infinite.oar
[ADMISSION RULE] Set default walltime to 7200.
[ADMISSION RULE] Modify resource description with type constraints
OAR_JOB_ID=1
```

Immediately after the submission, we check the queue status :

```bash
nico@hpc-scheduler:~/oar$ oarstat
Job id    S User     Duration   System message
--------- - -------- ---------- ------------------------------------------------
1         W nico        0:00:00 No enough matching resources (no_matching_slot)
```

Our job is pending, waiting for resources to appear.

### 5. Autoscaling up (horizontal scaling)

Let's switch to another screen and get Pods status :

```bash
root@admin:~# kubectl get pods
NAME            READY   STATUS    RESTARTS   AGE
controller      1/1     Running   0          4m28s
db-server       1/1     Running   0          4m28s
hpc-node-0      1/1     Running   0          36s
hpc-scheduler   1/1     Running   0          4m28s
```

A new node appeared. Go back to previous screen on the regular user session in "hpc-scheduler" Pod and check containerized compute nodes status :

```bash
nico@hpc-scheduler:~/oar$ oarnodes -s
hpc-node-0
    1 : Alive
    2 : Alive
hpc-node-1
    3 : Absent (standby)
    4 : Absent (standby)
hpc-node-2
    5 : Absent (standby)
    6 : Absent (standby)
```

The containerized compute node "hpc-node-0" switched from "Absent" to "Alive" state. We check the state of our first job :

```bash
nico@hpc-scheduler:~/oar$ oarstat
Job id    S User     Duration   System message
--------- - -------- ---------- ------------------------------------------------
1         R nico        0:00:57 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
```

The job is running on the new Pod created by the controller. The Pod "hpc-node-0" was dynamically created according to pending job in the queue and the job has been scheduled on the newcomer Pods by OAR scheduler.

### 6. Autoscaling down

We submit a second job :

```bash
nico@hpc-scheduler:~/oar$ oarsub -S ./infinite.oar
[ADMISSION RULE] Set default walltime to 7200.
[ADMISSION RULE] Modify resource description with type constraints
OAR_JOB_ID=2
```

And check the queue immediately after :

```bash
nico@hpc-scheduler:~/oar$ oarstat
Job id    S User     Duration   System message
--------- - -------- ---------- ------------------------------------------------
1         R nico        0:14:36 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
2         W nico        0:00:00 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
```

The previous job is always running and the second is pending, waiting for resources to appear. Let's switch to another terminal to check Pods status :

```bash
root@admin:~# kubectl get pods
NAME            READY   STATUS    RESTARTS   AGE
controller      1/1     Running   0          19m
db-server       1/1     Running   0          19m
hpc-node-0      1/1     Running   0          15m
hpc-node-1      1/1     Running   0          43s
hpc-scheduler   1/1     Running   0          19m
```

A new Pod "hpc-node-1" appeared. Now, go back to user session :

```bash
nico@hpc-scheduler:~/oar$ oarstat
Job id    S User     Duration   System message
--------- - -------- ---------- ------------------------------------------------
1         R nico        0:15:37 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
2         R nico        0:00:47 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
```

The second job is running on "hpc-node-1". Let's delete the first job :

```bash
nico@hpc-scheduler:~/oar$ oardel 1
Deleting the job = 1 ...REGISTERED.
The job(s) [ 1 ] will be deleted in the near future.
```

Few seconds later, the job disappeared from the queue :

```bash
nico@hpc-scheduler:~/oar$ oarstat
Job id    S User     Duration   System message
--------- - -------- ---------- ------------------------------------------------
2         R nico        0:01:38 R=2,W=2:0:0,J=B,N=oarsub (Karma=0.000,quota_ok)
```

On the other terminal we can check the state of Pods :

```bash
root@admin:~# kubectl get pods
NAME            READY   STATUS        RESTARTS   AGE
controller      1/1     Running       0          20m
db-server       1/1     Running       0          20m
hpc-node-0      1/1     Terminating   0          17m
hpc-node-1      1/1     Running       0          2m7s
hpc-scheduler   1/1     Running       0          20m
```

The Pod "hpc-node-0" is terminating. Few seconds it vanished :

```bash
root@admin:~# kubectl get pods
NAME            READY   STATUS    RESTARTS   AGE
controller      1/1     Running   0          21m
db-server       1/1     Running   0          21m
hpc-node-1      1/1     Running   0          2m28s
hpc-scheduler   1/1     Running   0          21m
```

We go back to user session to check the state of compute nodes :

```bash
nico@hpc-scheduler:~/oar$ oarnodes -s
hpc-node-0
    1 : Absent (standby)
    2 : Absent (standby)
hpc-node-1
    3 : Alive
    4 : Alive
hpc-node-2
    5 : Absent (standby)
    6 : Absent (standby)
```

The containerized compute node "hpc-node-0" switched from "Alive" to "Absent" state.
