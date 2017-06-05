#!/bin/sh

# cmds is operation list which is defined in docker_operation.py
cmds=""
config_folder=""
task_name=""
sleep_time=5

operation_file="`(cd "$(dirname "$0")"; pwd)`/docker_operation.py"
if [ ! -f $operation_file ]; then
    echo "Not found the operation script ${operation_file}"
    exit 1
fi

function read_opt() {
	config_folder=""
	sleep_time="1s"
	cmds=""
	
	while getopts :f:s:c:t: opt; do
	    case $opt in
	        f) config_folder="$OPTARG" ;;
	        s) sleep_time="$OPTARG" ;;
	        c) cmds="$OPTARG" ;;
	        t) task_name="$OPTARG" ;;
	        \?) echo "Invalid param" ;;
	    esac
	done
	
	echo "Configuration folder: $config_folder"
	echo "Task name: $task_name"
	echo "Command execution time gap:$sleep_time"
	echo "Command list:$cmds"
}

function operation(){
	OLD_IFS="$IFS"
	IFS=","
	cmd_list=($cmds)
	IFS="$OLD_IFS"
	for cmd in ${cmd_list[@]}
	do
	{
		echo "python ${operation_file} $config_folder $task_name $cmd "
        python ${operation_file} $config_folder $task_name $cmd
        
        if [[ $? != 0 ]];then
   	    	echo "Operation $cmd failed. ${ret}"
   	    	exit 1
   	    fi
   	    
   	    #echo "sleep ${sleep_time} before next operation cmd"
   	    sleep $sleep_time
	}
	done
	wait
    echo "Finish to do operation: $cmds"
}

read_opt $@
operation