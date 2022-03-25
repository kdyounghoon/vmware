#!/bin/bash

#selinux disable (Optional)
sed -i 's/=enforcing/=disabled/g' /etc/selinux/config

#Timezone Setting (Optional)
cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime

#Install necessary pacakges (Optional)
yum install -y net-tools bind-utils traceroute tcpdump python3 python3-pip

#Remove firewalld/NetworkManager (Recommended)
systemctl disable firewalld
systemctl stop firewalld
systemctl disable NetworkManager
systemctl stop NetworkManager
systemctl disable packagekit --now
echo "enabled=0" >> /etc/yum/pluginconf.d/refresh-packagekit.conf
yum remove -y PackageKit*
#yum remove -y firewalld NetworkManager

#Install Cloud-init 
yum install -y cloud-init

#Change cloud-config settings
cat << EOF >> /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
network: {config: disabled}
EOF

sed -i 's/disable_root/#disable_root/g' /etc/cloud/cloud.cfg
sed -i 's/ssh_pwauth/#ssh_pwauth/g' /etc/cloud/cloud.cfg
sed -i 's/disable_vmware_customization/#disable_vmware_customization/g' /etc/cloud/cloud.cfg
echo "disable_root: 1" >> /etc/cloud/cloud.cfg
echo "ssh_pwauth: 0" >> /etc/cloud/cloud.cfg

#Disable cloud-init related services
systemctl disable cloud-init-local cloud-init cloud-config cloud-final

#Create a service to start cloud init after vmtools starts and get IP. Chnage 'ens192' to your primary interface name. 
cat << 'EOF' >> /usr/bin/vra-init
#!/bin/bash
TICK=1
while true;
do
        IP=`ifconfig ens192 | grep -m 1 inet | awk '{print $2}'`
        GW_ADDR=`ip route | grep default | awk '{print $3}'`
        DNS_ADDR=`cat /etc/resolv.conf | grep nameserver | awk '{print $2}'`
        echo "IP Address for ens 192 is $IP"
        echo "GD_ADDR is $GW_ADDR"
        echo "DNS_ADDR is $DNS_ADDR"
        if [ $IP ] && [ $GW_ADDR ] && [ $DNS_ADDR ]; then
                echo "IP, GW_ADDR, DNS_ADDR network ready" >> /tmp/vra-init.log
                break
        fi
        echo "wait network status" >> /tmp/vra-init.log
        sleep $TICK
done
/usr/bin/cloud-init init --local
/usr/bin/cloud-init init
/usr/bin/cloud-init modules --mode=config
/usr/bin/cloud-init modules --mode=final
EOF

chmod 755 /usr/bin/vra-init

cat << 'EOF' >> /lib/systemd/system/vra-init.service
[Unit]
Description=vRealize Automation Init Service
After=vmtoolsd.service
[Service]
Type=oneshot
ExecStart=/usr/bin/vra-init
RemainAfterExit=yes
TimeoutSec=0
KillMode=process
TasksMax=infinity
StandardOutput=journal+console
[Install]
WantedBy=multi-user.target
EOF

chmod 755 /lib/systemd/system/vra-init.service
systemctl enable vra-init

