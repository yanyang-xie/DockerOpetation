# DockerOpetation

python docker_opertion demo tomcat create
sh docker_operation.sh -f demo -t tomcat -c delete,create

--------------------------
# CentOS7 开放端口
yum install firewalld systemd -y
systemctl restart firewalld

开放端口
firewall-cmd --zone=public —add-port=80/tcp --permanent

---------------------------
# Docker Server开放rest api
vi /etc/sysconfig/docker

OPTIONS='--selinux-enabled --log-driver=journald --signature-verification=false --dns=114.114.114.114 -H tcp://0.0.0.0:6732 -H unix:///var/run/docker.sock'
