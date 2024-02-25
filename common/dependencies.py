from dependency_injector import containers, providers
from common.hdfs.client import HDFSClient
from common.messaging.clients.rabbit.connection import RabbitConnection


class DependenciesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    rabbit_connection = providers.Singleton(RabbitConnection, connection_url=config.rabbit.connection_url)
    hdfs_client = providers.Singleton(HDFSClient, connection_url=config.hdfs.connection_url)
