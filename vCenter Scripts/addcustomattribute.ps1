#Connect-VIServer -Server 192.168.30.178 -u administrator@vsphere.local -Password VMware1!
$VMS = Get-VM
$VMS_NO_AT
foreach ($VM in $VMS){
	$VMNotes = $VM | Select-Object -ExpandProperty Notes
	if ($VMNotes.Contains("-")){
		Write-Host $VMNotes
		$AT1 = $VMNotes.split("-")[0]
                $AT2 = $VMNotes.split("-")[1]
                $AT3 = $VMNotes.split("-")[2]
		$VM | Set-Annotation -CustomAttribute "AT1" -Value $AT1
		$VM | Get-Annotation
	} else { 
		$VMS_NO_AT += $VM
	}

}

$VMS_NO_AT
