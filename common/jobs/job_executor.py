import uuid
from kubernetes import client, config


class JobExecutor:
    def __init__(self):
        # config.load_kube_config()
        config.load_incluster_config()

    def create_job(self, name, image, command, args):
        job_id = str(uuid.uuid4())
        pod_id = job_id

        metadata = client.V1ObjectMeta(name=name, labels={"job_name": job_id})
        print("T"*10, args)

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy='Never',
            args=[*args],
            command=[*command],
        )

        pod_name = "job_" + pod_id
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )

        client.BatchV1Api().create_namespaced_job(namespace='default', body=job)
