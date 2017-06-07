This is an attempt to make my life easier.
It allows you to configure Docker containers in configuration files and run them with ./docker_operation.sh

docker_operation.py will parse the configuration file and use docker library to create and start the container specified. Arguments in configuration file can be specified with docker commandline like arguments.

Supports
- image
- ports
- volumes
- cmd

example:
- sh docker_operation.sh -f demo -t tomcat -c delete,create
- python docker_opertion demo tomcat create

Options for docker_operation.sh
- -f configuration folder
- -t operation task name: tomcat.container.name=tomcat-123456
- -c command: /create/delete/update/start/stop/restart/

Setup your system

  vi /etc/sysconfig/docker
  OPTIONS="-H tcp://0.0.0.0:6732 -H unix://var/run/docker.sock"
