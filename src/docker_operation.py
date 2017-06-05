# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com
import sys, os

from utility import common_util
from utility.docker_util import DockerOperation


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], ".."))

task_name, docker_server_url, image_name, container_name, container_cpu, container_memory = ('','','','', 1024, '1g')
container_ports, container_volumes = ({},{})
operator = ''

def read_config():
    if len(sys.argv) < 4:
        print sys.argv
        print 'Missing required parameters. task, conf folder and operation'
        exit(1)
    
    global task_name, operator
    config_folder, task_name, operator = sys.argv[1], sys.argv[2], sys.argv[3]
    config_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + config_folder + os.sep + 'config.properties'
    print 'task:{}, config file:{}'.format(task_name, config_file)
    
    conf = common_util.load_properties(config_file)
    task_conf = {}
    for key, value in conf.items():
        if key.find(task_name + '.') == 0:
            task_conf[key.replace(task_name + '.', '')] = value
    
    return task_conf

def validate_config(task_conf):
    if operator not in ['start', 'stop', 'create', 'delete', 'update']:
        print "unsupported operator [%s]. start/stop/create/delete/update" %(operator)
        exit(1)
    
    global docker_server_url, image_name, image_repository_username, image_repository_password, auth_config
    global container_name, container_ports, container_volumes, container_cpu, container_memory, container_cmd
    auth_config, container_ports, container_volumes = {},{}, {}
    
    if not task_conf.has_key('docker.server.url') or common_util.get_config_value_by_key(task_conf, 'docker.server.url')=='':
        print 'Docker server must be provided'
        exit(1)
    else:
        docker_server_url = common_util.get_config_value_by_key(task_conf, 'docker.server.url')
    
    if not task_conf.has_key('docker.server.url'):
        print 'Image and container name must be provided'
        exit(1)
    
    if not task_conf.has_key('image.name') or not task_conf.has_key('container.name'):
        print 'Image and container name must be provided'
        exit(1)
    
    image_name = common_util.get_config_value_by_key(task_conf, 'image.name')
    image_repository_username = common_util.get_config_value_by_key(task_conf, 'image.repository.username')
    image_repository_password = common_util.get_config_value_by_key(task_conf, 'image.repository.password')
    
    container_name = common_util.get_config_value_by_key(task_conf, 'container.name')
    container_cpu = int(common_util.get_config_value_by_key(task_conf, 'container.cpu', 1024))
    container_memory = common_util.get_config_value_by_key(task_conf, 'container.memory', '1g')
    
    #The command to run in the container
    container_cmd = common_util.get_config_value_by_key(task_conf, 'container.cmd', None)
    
    if image_repository_username is not None and image_repository_password is not None:
        auth_config = {'username': image_repository_username, 'password': image_repository_password}
    
    #{'8080/tcp': 8090,}
    container_ports_string = common_util.get_config_value_by_key(task_conf, 'container.ports.map')
    if container_ports_string is not None:
        for container_ports_map in container_ports_string.split(','):
            port_list = container_ports_map.split(':')
            container_ports['%s/tcp' %(port_list[0])] = int(port_list[1])
        
    container_volumes_string = common_util.get_config_value_by_key(task_conf, 'container.volumes.map')
    if container_volumes_string is not None:
        for container_volumes_map in container_volumes_string.split(','):
            volumes_list = container_volumes_map.split(':')
            container_volumes[volumes_list[0]] = {'bind': '%s' %(volumes_list[1]), 'mode': 'rw'}

def create():
    if docker_operation.exist_container(container_name):
        raise Exception('A container named %s is existed, not create')
    
    container = docker_operation.create_container(image_name, command=container_cmd, container_name=container_name, ports=container_ports, volumes=container_volumes, cpu_shares=container_cpu, mem_limit=container_memory, auth_config=auth_config)
    print container.id, container.name, container.status, container.attrs
    return container

def update():
    delete()
    create()

def delete():
    if docker_operation.exist_container(container_name):
        container = docker_operation.get_container_by_name(container_name)
        docker_operation.stop_container(container)
        docker_operation.delete_container(container)
    else:
        print 'Not found container %s' %(container_name)

def start():
    if docker_operation.exist_container(container_name):
        container = docker_operation.get_container_by_name(container_name)
        docker_operation.start_container(container)
    else:
        raise Exception('Not found container %s' %(container_name))

def stop():
    if docker_operation.exist_container(container_name):
        container = docker_operation.get_container_by_name(container_name)
        docker_operation.stop_container(container)
    else:
        raise Exception('Not found container %s' %(container_name))

if __name__ == '__main__':
    task_conf = read_config()
    validate_config(task_conf)
    print 'Task conf for [%s]: %s | %s | %s | %s | %s | %s | %s | %s' %(task_name, image_name, container_name, container_cpu, container_memory, container_ports, container_volumes, docker_server_url, auth_config)
    
    docker_operation = DockerOperation(docker_server_url)
    eval('%s()' %operator)
    print 'Finished to %s container' %(operator)