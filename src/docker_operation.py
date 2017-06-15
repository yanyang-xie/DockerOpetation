# -*- coding=utf-8 -*-
# author: yanyang.xie@thistech.com
import sys, os

from utility import common_util
from utility.docker_util import DockerOperation
from __builtin__ import int

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], ".."))

task_name, docker_server_url, image_name, container_name, container_cpu, container_memory = ('','','','', 1024, '1g')
auth_config, container_ports, container_volumes, container_hosts, container_env = {},{},{},{},{}
operator = ''
timeout = 120

def create():
    if docker_operation.exist_container(container_name):
        raise Exception('Container named %s is existed, not create any more' %(container_name))
    
    container = docker_operation.create_container(image_name, command=container_cmd, container_name=container_name, ports=container_ports, volumes=container_volumes, cpu_shares=container_cpu, mem_limit=container_memory, extra_hosts=container_hosts, environment=container_env, auth_config=auth_config)
    print container.id, container.name, container.status
    return container

def update():
    docker_operation.delete_image(image_name)
    
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

def restart():
    stop()
    start()

def read_config():
    if len(sys.argv) < 4:
        print sys.argv
        print 'Missing required parameters. task, conf folder and operation'
        exit(1)
    
    global task_name, operator, timeout
    config_folder, task_name, operator = sys.argv[1], sys.argv[2], sys.argv[3]
    
    if len(sys.argv) > 4:
        timeout = int(sys.argv[4])
    
    if config_folder.find('/') > 0:
        config_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + config_folder
    else:
        config_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + config_folder + os.sep + 'config.properties'
    print 'task:{}, config file:{}'.format(task_name, config_file)
    
    conf = common_util.load_properties(config_file)
    task_conf = {}
    for key, value in conf.items():
        if key.find(task_name + '.') == 0:
            task_conf[key.replace(task_name + '.', '')] = value
    
    return task_conf

def validate_config(task_conf):
    if operator not in ['start', 'stop', 'create', 'delete', 'update', 'restart']:
        print "unsupported operator [%s]. start/stop/create/delete/update" %(operator)
        exit(1)
    
    global docker_server_url, image_name, image_repository_username, image_repository_password, auth_config
    global container_name, container_ports, container_volumes, container_cpu, container_memory, container_cmd
    global container_hosts, container_env
    #auth_config, container_ports, container_volumes, container_hosts, container_env = {},{},{},{},{}
    
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
    
    #{'8080/tcp': 8090,}. format: ip:hostPort:containerPort
    container_ports_string = common_util.get_config_value_by_key(task_conf, 'container.ports.map')
    container_ports = _convert_to_dict(container_ports_string)
    container_ports = {'%s/tcp' %(value): int(key) for key, value in container_ports.items()}
        
    container_volumes_string = common_util.get_config_value_by_key(task_conf, 'container.volumes.map')
    container_volumes = _convert_to_dict(container_volumes_string)
    container_volumes = { key: {'bind': value, 'mode': 'rw'}  for key, value in container_volumes.items()}
    
    #{env1:value_env1, env2:value_env2}
    container_env_string = common_util.get_config_value_by_key(task_conf, 'container.env.map')
    container_env = _convert_to_dict(container_env_string)
    
    #{env1:value_env1, env2:value_env2}
    container_hosts_string = common_util.get_config_value_by_key(task_conf, 'container.hosts.map')
    container_hosts = _convert_to_dict(container_hosts_string)

def _convert_to_dict(t_string, dict_sep=',', key_value_sep=':'):
    if t_string is None:
        return {}
    
    t_dict = {}
    for sub_string in t_string.split(dict_sep):
        if sub_string.find(key_value_sep) < 1:
            print 'Not found key_value_sep %s, ignore it' %(key_value_sep)
            continue
        
        sub_string = sub_string.strip()
        sub_string_list = sub_string.split(key_value_sep)
        t_dict[sub_string_list[0]] = sub_string_list[1]
    
    return t_dict

if __name__ == '__main__':
    task_conf = read_config()
    validate_config(task_conf)
    print 'Task conf for [%s]: %s | %s | %s | %s | %s | %s | %s | %s | %s | %s' %(task_name, image_name, container_name, container_cpu, container_memory, container_ports, container_volumes, container_hosts, container_env, docker_server_url, auth_config)
    
    docker_operation = DockerOperation(docker_server_url, timeout=timeout)
    eval('%s()' %operator)
    print 'Finished to %s container' %(operator)