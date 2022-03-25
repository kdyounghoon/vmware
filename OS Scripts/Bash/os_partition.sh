###########Lix-DiskPartition##############

#!/bin/bash



## diskinfos parameters must be contain the mountpoint and disk size information

## ex) orahome=100,tibadm=200(mountpoint=disksize,...)



diskinfos=$1



array_diskinfos=$(echo $diskinfos | tr "," "\n")



for diskinfo in $array_diskinfos

do

	input_mountpoint_tmp=""

	input_disksize=""

	

	input_mountpoint_tmp=$(echo $diskinfo | cut -f1 -d=)

	input_disksize=$(echo $diskinfo | cut -f2 -d=)



	if [[ $input_mountpoint_tmp == "" ]]

	then

		mkdir "/data"

		input_mountpoint="/data"

	else

		if [[ $input_mountpoint_tmp == /* ]]

		then

			input_mountpoint=$input_mountpoint_tmp

		else

			input_mountpoint="/"$input_mountpoint_tmp

		fi

		mkdir $input_mountpoint

	fi



	if [[ $input_mountpoint != "/" ]]

	then

		chmod -R 777 $input_mountpoint

	fi



	lsblk -io KNAME | grep sd | cut -c 1-3 | sort | uniq > /tmp/all_devices.txt

	blkid | grep sd | cut -c 6-8 | sort | uniq > /tmp/ex_devices.txt

	diff /tmp/all_devices.txt /tmp/ex_devices.txt | grep sd | cut -c 3-5 | sort | uniq > /tmp/new_devices.txt

	

	lsblk -io KNAME,SIZE | grep $input_disksize | cut -c 1-3 | sort > /tmp/size_matched_devices.txt

	size_matched_new_devices=$(grep -wFf /tmp/new_devices.txt /tmp/size_matched_devices.txt)

	

	size_matched_new_device=$(echo $size_matched_new_devices | cut -f1 -d' ')



	new_fs="/dev/"$size_matched_new_device

	

	parted -s $new_fs mklabel gpt mkpart primary 1 100%

	mkfs -F -t ext4 $new_fs"1"

		

	mount $new_fs"1" $input_mountpoint

	/usr/bin/cp -f /etc/fstab /etc/fstab.org



	echo "$new_fs"1"	  $input_mountpoint	 ext4 	   defaults,nofail	 0       2" >> /etc/fstab



	df -h

	file -s $new_fs"1"

done



rm -rf /tmp/all_devices.txt

rm -rf /tmp/ex_devices.txt

rm -rf /tmp/new_devices.txt

rm -rf /tmp/size_matched_devices.txt







###########Lix-OSParam##############



os_param_list=$1



array_os_param_list=$(echo $os_param_list | tr "," "\n")



for os_param in $array_os_param_list

do

	key=$(echo $os_param | cut -f1 -d=)

	value=$(echo $os_param | cut -f2 -d=)

		

	if [[ $key == *os_local_user* ]] 

	then

		value_user=$(echo $value | cut -f1 -d_)

		value_home=$(echo $value | cut -f2 -d_)

		

		account_check=$(cat /etc/passwd | grep $value_user)

		echo "$account_check"



		if [ -n $account_check ]

		then

			if [ $value_home == */home* ] || [ -z $value_home ] || [ $value_user == $value_home ]

			then

				echo "home directory is under /home folder or home directory is no defined"

				useradd $value_user; echo "$value_user:Password" | chpasswd

				echo "User added $value_user"



				homedir=/home/$value_user



				if [ -d $homedir ]

				then 

					echo "home directory is exist"

					chown -R $value_user:$value_user $value_home

					cp /etc/skel/.* $homepath

				fi

				

			else

				echo "creating home directory"

				useradd $value_user -d $value_home/$value_user; echo "$value_user:Password" | chpasswd

				

				homedir=$value_home/$value_user



				if [ -d $homedir ]

				then

					echo "home directory is exist"

					chown -R $value_user:$value_user $value_home

					cp /etc/skel/.* $homepath

				fi

				

				chown -R $value_user $value_home

				echo "User added $value_user"

			fi

			

			chage -d 0 $value_user

		fi



		echo "$value_user is exist"

	fi

	

	if [[ $key == *os_user_shell* ]]

	then

		value_user=$(echo $value | cut -f1 -d_)

		value_shell=$(echo $value | cut -f2 -d_)

		

		shell="/bin/"$value_shell

		usermod --shell $shell $value_user

	fi

	

	if [[ $key == *os_kernel_param* ]] ## nofile, nproc, stack

	then

		value_param=$(echo $value | cut -f1 -d_)

		value_user=$(echo $value | cut -f2 -d_)

		value_type=$(echo $value | cut -f3 -d_)

		value_data=$(echo $value | cut -f4 -d_)

		

		if [[ $value_param == *nofile* ]]

		then

			sed -i '/^# End of file/i '$value_user'\t\t'$value_type'\tnofile\t\t'$value_data /etc/security/limits.conf

			

		elif [[ $value_param == *nproc* ]]

		then

			sed -i '/^# End of file/i '$value_user'\t\t'$value_type'\tnproc\t\t'$value_data /etc/security/limits.conf

			

		elif [[ $value_param == *stack* ]]

		then

			sed -i '/^# End of file/i '$value_user'\t\t'$value_type'\tstack\t\t'$value_data /etc/security/limits.conf

		

		else

			echo "There is no matched param name"

		fi

	fi

done







#################Windows-Disk Part################

## diskinfos parameters must be contain the mountpoint and disk size information

## ex) q=100,m=200(driverletter=disksize,...)

## Do not accept defined (A, B, Z) drive from portal



Param (

	[string]

	[Parameter(Position=0)]

	$DiskInfos

	)



Function DiskFormat {

	Write-Output "Initializing Disk"

	Initialize-Disk $Disk.Number -PartitionStyle GPT -confirm:$false

				

	Write-Output "Partitioning Disk"

	New-Partition -DiskNumber $Disk.Number -AssignDriveLetter -UseMaximumSize | Format-Volume -FileSystem NTFS -NewFileSystemLabel "Local Disk" -confirm:$False

	}



Function DiskFormat_DriveLetter {

	Write-Output "Initializing Disk: $DriveLetter - $DiskSize"

	Initialize-Disk $Disk.Number -PartitionStyle GPT -confirm:$false

				

	Write-Output "Partitioning Disk: $DriveLetter - $DiskSize"

	New-Partition -DiskNumber $Disk.Number -DriveLetter $DriveLetter -UseMaximumSize | Format-Volume -FileSystem NTFS -NewFileSystemLabel "Local Disk" -confirm:$False

	}



If($DiskInfos -eq "") {

	$Disks = Get-Disk | Where-Object {$_.PartitionStyle -eq "RAW"}



	Foreach($Disk in $Disks) {

		DiskFormat

		}

	}

Else {

	$Array_DiskInfo = $DiskInfos.split(",")



	Foreach($DiskInfo in $Array_DiskInfo) {

		$DriveLetter = ($DiskInfo.Split("="))[0]

		$DiskSize = ($DiskInfo.Split("="))[1]

		$DiskSizeinGB = $DiskSize + "GB"



		$Disks = Get-Disk | Where-Object {$_.PartitionStyle -eq "RAW" -and $_.Size -eq $DiskSizeinGB}

		$Disk = $Disks[0]



		If($DriveLetter -ne "") {

			DiskFormat_DriveLetter

			}	

		Else {

			DiskFormat

			}

		}

	}





######Win-OS Param###############



Param (

	[string]

	[Parameter(Position=0)]

	$OS_Param_list

	)



Write-Output "Start OS Param script"



$Array_OS_Param_list = $OS_Param_list.split(",")



Foreach($os_param in $Array_OS_Param_list) {

	

	Write-Output "$os_param"

	

	$Key = ($os_param.Split("="))[0]

	$Value = ($os_param.Split("="))[1]

	

	Write-Output "Key - $Key"

	Write-Output "Value - $Value"

	

	$Password = ConvertTo-SecureString "Password" -AsPlainText -Force

	

	If($Key -like "os_local_user*") {

		Write-Output "Creating user - $value"

		New-LocalUser -Name $Value -Password $Password

		

		$Command = "cmd.exe /C net user $Value /logonpasswordchg:yes"

		

		Invoke-Expression -Command:$Command

		

		Add-LocalGroupMember -Group "Administrators" -Member $value

		

		}

	

	If($Key -like "os_ad_user*") {

		Write-Output "Adding $value into Local Administrators group"

		Add-LocalGroupMember -Group "Administrators" -Member $value

		}

}






