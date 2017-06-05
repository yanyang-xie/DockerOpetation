# DockerOpetation

python docker_opertion demo tomcat create
sh docker_operation.sh -f demo -t tomcat -c delete,create

------------------------------------
-f configuration folder
-t operation task name: tomcat.container.name=tomcat-123456
-c command: start/stop/update/delete/create

------------------------------------
Docker Rest API
vi /etc/sysconfig/docker
OPTIONS="-H tcp://0.0.0.0:6732 -H unix://var/run/docker.sock"

systemctl restart docker.service


