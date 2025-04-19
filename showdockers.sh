#!/bin/bash

# 获取所有容器的ID和用户
sudo   docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}' | while read line; do
       container_id=$(echo $line | awk '{print $1}')
       container_name=$(echo $line | awk '{print $2}')
       user=$(docker inspect -f '{{.Config.User}}' $container_id)
       echo "Container ID: $container_id, Name: $container_name, User: $user"
   done


