from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import json
import os

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
	container1 = client.V1Container(name='hpc-worker', image=queuesDict[queueName]['image'], resources=containerResources, env_from=containerEnv, command=containerCommand, volume_mounts=[mount], args=containerArgs)
	containers.append(container1)
	claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=homePVC, read_only=False)
	volume = client.V1Volume(name=homeName, persistent_volume_claim=claim)
	defaultDomain = os.environ['NET_SERVICE'] + '.' + os.environ['KUBERNETES_NAMESPACE'] + '.' + os.environ['KUBERNETES_DOMAIN']
	dnsSearch = client.V1PodDNSConfig(searches=[defaultDomain])
	pod_spec = client.V1PodSpec(containers=containers, volumes=[volume], subdomain=os.environ['NET_SERVICE'], dns_config=dnsSearch)
	print(str(pod_spec))
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
			return True
	return False
		

if __name__ == '__main__':

	config.load_incluster_config()
	c = client.CoreV1Api()
	queues = getQueues(c, os.environ['KUBERNETES_NAMESPACE'], os.environ['OAR_SERVER_HOSTNAME'])
	schedulerEnv = getEnvFromVariables(c, os.environ['OAR_SERVER_HOSTNAME'], os.environ['ALMIGHTY_CONTAINER'], os.environ['KUBERNETES_NAMESPACE'])
	addPod(c, "default", queues, os.environ['KUBERNETES_NAMESPACE'], schedulerEnv, os.environ['HOME_PVC'], os.environ['HOME_MOUNT_NAME'], os.environ['HOME_MOUNT_PATH'], ["/bin/bash"], ["/start-node.sh"])
