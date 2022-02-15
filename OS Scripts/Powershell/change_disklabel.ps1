$vm = Get-VM -Name harbor
$devices = $VM.ExtensionData.Config.Hardware.Device 

Foreach ($device in $devices){
	if($device.gettype().Name -eq "VirtualDisk"){
		if($device.DeviceInfo.Label.Contains("Hard")){ 
			Write-Host $device.DeviceInfo.Label
			$spec = New-Object VMware.Vim.VirtualMachineConfigSpec
			$dev = New-Object VMware.Vim.VirtualDeviceConfigSpec
			$dev.device = $device
                        $description = New-Object VMware.Vim.Description
                        $description.label = "test1"
			$description.summary = "test2"
			$dev.device.DeviceInfo
                        $dev.device.DeviceInfo = $description
			$dev.operation = [VMware.Vim.VirtualDeviceConfigSpecOperation]::edit
			$spec.deviceChange += $dev
			#$vm.ExtensionData.ReconfigVM_Task($spec) 
					
		}
		

	}
	
}
