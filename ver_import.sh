#! /bin/sh

cifs="//10.10.1.100/version"
mount_path=/mnt/versions
mount_path_iso=/mnt/vserver
cifs_user=ver
cifs_passwd=111111
iso_path=
version=
system=


error()
{
    echo "$@" 1>&2
    usage_and_exit 1
}

exception()
{
    echo "$@" 1>&2
    exit 1
}

usage()
{
    cat <<EOF
Usage:
      $PROGRAM --ver version of vServer
      $PROGRAM --pth path to iso 
      $PROGRAM --sys the system name to install 
EOF
}

usage_and_exit()
{
    usage
    exit $1
}

while test $# -gt 0
do
    case $1 in
    --ver)
       version=$2 
       shift
       ;;
    --pth)
       iso_path=$2 
       shift
       ;;
    --sys)
       system=$2 
       shift
       ;;
    -*)
       usage_and_exit 1
       ;;
    *)
       break
       ;;
    esac
    shift
done

mount_version()
{
    echo "*** Mounting cifs..."
    if ! [ -e "$mount_path" ]
    then
        mkdir $mount_path
    else
        mount.cifs $cifs $mount_path  -o user=$cifs_user,passwd=$cifs_passwd || exception
    fi

    echo "*** Done"
}

mount_iso()
{
    echo "*** Mounting iso..."
    if ! [ -e "$mount_path_iso" ]
    then
        mkdir $mount_path_iso
    fi
    mount -t auto -o loop $mount_path/$iso_path $mount_path_iso || exception

    echo "*** Done"
}


cobbler_import()
{   
    echo "*** Running cobbler import......"
    cobbler import --path=$mount_path_iso  --name=$version --arch=x86_64
    cobbler distro edit --name=$version-x86_64  --initrd=/var/www/cobbler/ks_mirror/$version-x86_64/isolinux/initrd.img
    cobbler distro edit --name=$version-x86_64  --kernel=/var/www/cobbler/ks_mirror/$version-x86_64/isolinux/vmlinuz
    cobbler sync
    echo "*** Done"
}

cobbler_edit_system()
{
    echo "*** Editing system ......"
    cobbler system edit --name=$system --profile=${version}-x86_64 --netboot-enabled=true
    cobbler sync
    echo "*** Done"
}

tear_down()
{
    echo '*** Tear down: Umounting...'
    umount $mount_path_iso
    umount $mount_path
    echo '*** Done'
}

if ! [ -n "$version" ] || ! [ -n "$iso_path" ] || ! [ -n "$system" ]
then
    error
fi

if [ "$?" == "0" ];then
    mount_version
else
    echo "Error"
    exit 1
fi

if [ "$?" == "0" ];then
    mount_iso
else
    echo "Error"
    exit 1
fi

if [ "$?" == "0" ];then
    cobbler_import
else
    echo "Error"
    exit 1
fi

if [ "$?" == "0" ];then
    cobbler_edit_system
else
    echo "Error"
    exit 1
fi

if [ "$?" == "0" ];then
    tear_down
else
    echo "Error"
    exit 1
fi

