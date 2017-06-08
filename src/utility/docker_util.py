# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com

#https://docker-py.readthedocs.io/en/stable
#yum install docker

import docker

class DockerOperation():
    
    def __init__(self, base_url, version='1.24', timeout=3):
        self.client = docker.DockerClient(base_url=base_url, version=version, timeout=timeout,)
        
    def get_image_list(self, name=None, filters=None):
        return self.client.images.list(name, filters=filters)
    
    def pull_image(self, name, auth_config={}):
        try:
            image = self.client.images.get(name)
            print 'Found image %s in local, need not pull from remote. Image info:%s' %(name, image)
        except:
            print 'Pull image %s from remote with auth_config %s.' %(name, auth_config)
            image = self.client.images.pull(name, auth_config=auth_config)
            #print 'Pull image %s from remote with auth_config %s, succeed. Image info:%s' %(name, auth_config, image)
    
    def get_container_list(self, all=True, before=None, filters=None, limit=-1, since=None):
        return self.client.containers.list(all, before, filters, limit, since)
    
    def get_container_list_by_status(self, status='running'):
        if status not in ['restarting', 'running','paused', 'exited', ]:
            return []
        
        return self.client.containers.list(all=False, filters={'status':status})
    
    def get_container_by_id(self, cid):
        return self.client.containers.get(cid)
    
    def get_container_by_name(self, name):
        return self.client.containers.get(name)
    
    def exist_container(self, name):
        try:
            return True if self.get_container_by_name(name) is not None else False
        except:
            return False
    
    def create_container(self, docker_image, command=None, detach=True, container_name=None, ports={}, volumes={}, cpu_shares=1024, mem_limit='1g', auth_config={}, extra_hosts={}, environment={}, **kwargs):
        self.pull_image(docker_image, auth_config=auth_config)
        
        # cpu_shares: CPU shares (relative weight). 1024 is 1 core CPU
        # mem_limit(str or int) : Memory limit. Accepts float values or a string with a units identification char (100000b, 1000k, 128m, 1g). If a string is specified without a units character, bytes are assumed as an intended unit.
        # environment: {env1:value_env1, env2:value_env2}
        # extra_hosts: {}
        return self.client.containers.run(docker_image, command=command, detach=detach, name=container_name, ports=ports, volumes=volumes, cpu_shares=cpu_shares, mem_limit=mem_limit, extra_hosts=extra_hosts, environment=environment, **kwargs)
    
    def delete_container(self, container):
        container.remove()
    
    def start_container(self, container):
        container.start()
    
    def restart_container(self, container):
        container.restart()
    
    def stop_container(self, container):
        container.stop()
    
    def pause_container(self, container):
        container.pause()
    
    def run_cmd_in_container(self, container, cmd):
        container.exec_run(cmd)
        
    def update_container(self, container, **kwargs):
        container.update(kwargs)


if __name__ == '__main__':
    docker_operation = DockerOperation('http://52.221.182.216:6732')
    
    docker_image='tomcat:8.0'
    container_name = 'tomcat-123456'
    container_ports={'8080/tcp': 8090} #8080 is container ip, 8090 is node ip which can be access by user
    container_volumes={'/root/test/logs': {'bind': '/root/tomcat/logs', 'mode': 'rw'},}
    auth_config = {}
    
    if docker_operation.exist_container(container_name):
        container = docker_operation.get_container_by_name(container_name)
        docker_operation.stop_container(container)
        docker_operation.delete_container(container)
    
    try:
        container = docker_operation.create_container(docker_image, container_name=container_name, ports=container_ports, volumes=container_volumes, cpu_shares=512, mem_limit='2g', auth_config=auth_config)
        print container.id, container.name, container.status, container.attrs
    except:
        import traceback
        traceback.print_exc()
    
    docker_operation.start_container(container)
    print container.id, container.name, container.status, container.attrs
    
    container = docker_operation.get_container_by_name(container_name)
    docker_operation.stop_container(container)
    docker_operation.delete_container(container)