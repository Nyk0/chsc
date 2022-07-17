from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import json

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

def createPod(k8sConnect, queueName, queuesDict, k8sNamespace, podName):

	containerResources = client.V1ResourceRequirements(requests={"cpu" : queuesDict[queueName]['cpuspernode']}, limits={"cpu" : queuesDict[queueName]['cpuspernode']})
	containers = []
	container1 = client.V1Container(name='hpc-worker', image=queuesDict[queueName]['image'], resources=containerResources)
	containers.append(container1)
	pod_spec = client.V1PodSpec(containers=containers)
	pod_metadata = client.V1ObjectMeta(name=podName, namespace=k8sNamespace)
	pod_body = client.V1Pod(api_version='v1', kind='Pod', metadata=pod_metadata, spec=pod_spec)
	k8sConnect.create_namespaced_pod(namespace='oar', body=pod_body)
	#time.sleep(60)
	#pod_logs = v1.read_namespaced_pod_log(name='my-pod', namespace='oar')
	#v1.delete_namespaced_pod(namespace='oar', name='my-pod')

def addPod(k8sConnect, queueName, queuesDict, k8sNamespace):

	i = 0
	while i < int(queuesDict[queueName]['nodes']):
		podName = queuesDict[queueName]['hostnamebase'] + "-" + str(i)
		try:
			podInfos = k8sConnect.read_namespaced_pod(name=podName, namespace=k8sNamespace)
			print("pod found")
			i += 1 
		except ApiException as e:
			print("pod not found")
			createPod(k8sConnect, queueName, queuesDict, k8sNamespace, podName)
			return True
	return False
		

if __name__ == '__main__':

	config.load_incluster_config()
	c = client.CoreV1Api()
	queues = getQueues(c, "oar", "hpc-scheduler")
	addPod(c, "default", queues, "oar")
