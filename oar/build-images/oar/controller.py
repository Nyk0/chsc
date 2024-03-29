from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import json
import os
import subprocess
import threading

def getEnvFromVariables(k8sConnect, k8sSchedPodName, k8sSchedPodContainerName, k8sNamespace):

	k8sConnect.read_namespaced_pod(name=k8sSchedPodName, namespace=k8sNamespace)
	podInfos = k8sConnect.read_namespaced_pod(name=k8sSchedPodName, namespace=k8sNamespace)
	i = 0
	while i < len(podInfos.spec.containers):
		if podInfos.spec.containers[i].name == k8sSchedPodContainerName:
			return podInfos.spec.containers[i].env_from
		else:
			i += 1
	return False

def getQueues(k8sConnect, k8sNamespace, k8sSchedPodName):

	fctQueues = dict()
	podInfos = k8sConnect.read_namespaced_pod(name=k8sSchedPodName, namespace=k8sNamespace)
	podAnnotations = ((json.loads(podInfos.metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']))["metadata"]["annotations"])
	for key in podAnnotations:
		name = key.split("/")[0]
		attr = key.split("/")[1]
		if name not in fctQueues.keys():
			fctQueues[name] = dict()
		fctQueues[name][attr] = podAnnotations[key]
	return fctQueues

def createPod(k8sConnect, queueName, queuesDict, k8sNamespace, podName, containerEnv, homePVC, homeName, homePath , containerCommand, containerArgs):

	containerResources = client.V1ResourceRequirements(requests={"cpu" : queuesDict[queueName]['cpuspernode']}, limits={"cpu" : queuesDict[queueName]['cpuspernode']})
	containers = []
	mount = client.V1VolumeMount(name=homeName, mount_path=homePath, read_only=False)
	capChroot = client.V1Capabilities(add=["SYS_CHROOT"])
	security = client.V1SecurityContext(capabilities=capChroot)
	#execAction = client.V1ExecAction(command=['/bin/bash', '/register.sh'])
	#lifeCycleHandler = client.V1LifecycleHandler(_exec=execAction)
	#lifeCycle = client.V1Lifecycle(post_start=lifeCycleHandler)
	#container1 = client.V1Container(name='hpc-worker', image=queuesDict[queueName]['image'], resources=containerResources, env_from=containerEnv, command=containerCommand, volume_mounts=[mount], args=containerArgs, security_context=security, lifecycle=lifeCycle)
	container1 = client.V1Container(name='hpc-worker', image=queuesDict[queueName]['image'], resources=containerResources, env_from=containerEnv, command=containerCommand, volume_mounts=[mount], args=containerArgs, security_context=security)
	containers.append(container1)
	claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=homePVC, read_only=False)
	volume = client.V1Volume(name=homeName, persistent_volume_claim=claim)
	defaultDomain = os.environ['NET_SERVICE'] + '.' + os.environ['KUBERNETES_NAMESPACE'] + '.' + os.environ['KUBERNETES_DOMAIN']
	dnsSearch = client.V1PodDNSConfig(searches=[defaultDomain])
	pod_spec = client.V1PodSpec(containers=containers, hostname=podName, volumes=[volume], subdomain=os.environ['NET_SERVICE'], dns_config=dnsSearch)
	pod_metadata = client.V1ObjectMeta(name=podName, namespace=k8sNamespace, labels={'role': 'worker', 'net': 'headless'})
	pod_body = client.V1Pod(api_version='v1', kind='Pod', metadata=pod_metadata, spec=pod_spec)
	k8sConnect.create_namespaced_pod(namespace='oar', body=pod_body)

def addPod(k8sConnect, queueName, queuesDict, k8sNamespace, containerEnv, homePVC, homeName, homePath, containerCommand, containerArgs):

	i = 0
	while i < int(queuesDict[queueName]['nodes']):
		podName = queuesDict[queueName]['hostnamebase'] + "-" + str(i)
		try:
			podInfos = k8sConnect.read_namespaced_pod(name=podName, namespace=k8sNamespace)
			i += 1 
		except ApiException as e:
			createPod(k8sConnect, queueName, queuesDict, k8sNamespace, podName, containerEnv, homePVC, homeName, homePath, containerCommand, containerArgs)
			return podName
	return False
		
def checkForNodeAlive(nodeName):

	oarnodesOut = subprocess.run(['oarnodes', '-J'], stdout=subprocess.PIPE).stdout.decode('utf-8')
	nodes = json.loads(oarnodesOut)
	#print(str(nodes))
	for key in nodes:
		if nodes[key]['network_address'] == nodeName and nodes[key]['state'] == "Absent":
			#print(nodes[key]['network_address'] + " => " + nodes[key]['state'])
			return False
	return True

def removePods(k8sConnect):
	timeIdle = {}
	while True:
		print(str(timeIdle))
		oarnodesOut = subprocess.run(['oarnodes', '-J'], stdout=subprocess.PIPE).stdout.decode('utf-8')
		nodes = json.loads(oarnodesOut)
		for key in nodes:
			if nodes[key]['state'] == "Alive":
				if 'jobs' not in nodes[key]:
					print("idle node " + nodes[key]['network_address'])
					if nodes[key]['network_address'] not in timeIdle:
						timeIdle[nodes[key]['network_address']] = 1
					else:
						if timeIdle[nodes[key]['network_address']] == 30:
							print("Destroy " + nodes[key]['network_address'])
							cmd = ['/usr/sbin/oarnodesetting', '-h', nodes[key]['network_address'], '-s', 'Absent']
							subprocess.Popen(cmd).wait()
							timeIdle.pop(nodes[key]['network_address'], None)
							k8sConnect.delete_namespaced_pod(nodes[key]['network_address'], os.environ['KUBERNETES_NAMESPACE'])
						else:
							timeIdle[nodes[key]['network_address']] += 1
				else:
					print("working node " + nodes[key]['network_address'])
					timeIdle.pop(nodes[key]['network_address'], None)
		time.sleep(1)

if __name__ == '__main__':

	config.load_incluster_config()
	c = client.CoreV1Api()

	queues = getQueues(c, os.environ['KUBERNETES_NAMESPACE'], os.environ['OAR_SERVER_HOSTNAME'])
	schedulerEnv = getEnvFromVariables(c, os.environ['OAR_SERVER_HOSTNAME'], os.environ['ALMIGHTY_CONTAINER'], os.environ['KUBERNETES_NAMESPACE'])

	acknowlegedJobs = []
	cmd = ['/bin/bash', '/create-resources.sh', queues['default']['nodes'], queues['default']['cpuspernode'], queues['default']['hostnamebase']]
	subprocess.Popen(cmd).wait()

	newpid = os.fork()
	if newpid == 0:
		removePods(c)
	else:
		while(True):

			oarstatOut = subprocess.run(['oarstat', '-f', '-J'], stdout=subprocess.PIPE).stdout.decode('utf-8')
			try:
				jobs = json.loads(oarstatOut)
			except json.decoder.JSONDecodeError:
				#print("No jobs running")
				jobs = {}
			allJobs = []
			for key in jobs :
				allJobs.append(jobs[key]['Job_Id'])
			#print("all : " + str(allJobs))
			for key in jobs :
				if jobs[key]['state'] == "Waiting" and jobs[key]['Job_Id'] not in acknowlegedJobs:
					acknowlegedJobs.append(jobs[key]['Job_Id'])
					print("ack : " + str(acknowlegedJobs))
					addedNode = addPod(c, "default", queues, os.environ['KUBERNETES_NAMESPACE'], schedulerEnv, os.environ['HOME_PVC'], os.environ['HOME_MOUNT_NAME'], os.environ['HOME_MOUNT_PATH'], ["/bin/bash"], ["/start-node.sh"])
					#addedNode = addPod(c, "default", queues, os.environ['KUBERNETES_NAMESPACE'], schedulerEnv, os.environ['HOME_PVC'], os.environ['HOME_MOUNT_NAME'], os.environ['HOME_MOUNT_PATH'], ["/bin/bash", "-c", "--"], ["while true; do sleep 30; done;"])
					while(checkForNodeAlive(addedNode) is False):
						time.sleep(1)
			time.sleep(1)
