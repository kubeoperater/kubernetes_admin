#!/usr/bin/env bash
VOLUME_ROOTPATH=$1
VOLUME_NAMESPACE=$2
VOLUME_NAME=$3
SSH_PASSWORD='rootpassword'
GFS_HOSTLIST=$(gluster pool list | grep -v "UUID" | grep Connected | awk '{print $2}')
for VOLUME_HOST in $GFS_HOSTLIST;do
    [ $VOLUME_HOST != 'localhost' ] && sshpass -p $SSH_PASSWORD ssh -o "StrictHostKeyChecking=no" root@$VOLUME_HOST "mkdir -p $1/$2/$3 | bash -s $VOLUME_ROOTPATH $VOLUME_NAMESPACE $VOLUME_NAME" || mkdir -p $VOLUME_ROOTPATH/$VOLUME_NAMESPACE/$VOLUME_NAME
    [ $? == 0 ] && echo $VOLUME_HOST || exit 2
done