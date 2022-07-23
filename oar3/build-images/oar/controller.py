from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import json

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
	print(str(containers))
	claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=homePVC, read_only=False)
	volume = client.V1Volume(name=homeName, persistent_volume_claim=claim)
	pod_spec = client.V1PodSpec(containers=containers, volumes=[volume])
	pod_metadata = client.V1ObjectMeta(name=podName, namespace=k8sNamespace)
	pod_body = client.V1Pod(api_version='v1', kind='Pod', metadata=pod_metadata, spec=pod_spec)
	k8sConnect.create_namespaced_pod(namespace='oar', body=pod_body)
	#time.sleep(60)
	#pod_logs = v1.read_namespaced_pod_log(name='my-pod', namespace='oar')
	#v1.delete_namespaced_pod(namespace='oar', name='my-pod')

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
	queues = getQueues(c, "oar", "hpc-scheduler")
	schedulerEnv = getEnvFromVariables(c, "hpc-scheduler", "oar-server", "oar")
	addPod(c, "default", queues, "oar", schedulerEnv, "pvc-nfs-home", "home", "/home", ["/bin/bash"], ["/start-node.sh"])
