 

function AzureConnect()

{

    $connectionName = "AzureRunAsConnection"

    try

    {

        $servicePrincipalConnection = Get-AutomationConnection -Name $connectionName     

        Add-AzureRmAccount `

            -ServicePrincipal `

            -TenantId $servicePrincipalConnection.TenantId `

            -ApplicationId $servicePrincipalConnection.ApplicationId `

            -CertificateThumbprint $servicePrincipalConnection.CertificateThumbprint 

    }

    catch {

        if (!$servicePrincipalConnection)

        {

            $ErrorMessage = "Connection $connectionName not found."

            throw $ErrorMessage

        } else {

            Write-Error -Message $_.Exception

            throw $_.Exception

        }

    }

}

 

Function IsBetweenDates([Datetime]$stop,[Datetime]$start,[string]$VMCurrentStatus,[datetime]$CurrentUKTime)

{

 

 #$CurrentUKTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [System.TimeZoneInfo]::FindSystemTimeZoneById("GMT Standard Time"))

 

#  [datetime] $CurrentUKTime = "09 March 2019 19:05:00"

        

 #  Write-Output "`nCurrent Time is $CurrentTime"

 #  Write-Output "`nStop Time of VM is: $Stop"

 #  Write-Output "`nStart Time of VM is: $Start"

 

    #$e = get-date "$($stop.Day)/$($Stop.Month)/$($d.Year)"

    #$s = get-date "$($start.Day)/$($start.Month)/$($d.Year)"

    

 

    if (($CurrentUKTime -ge $stop) -and ($CurrentUKTime -le $start))

    {

 

         Write-host "`nCurrentTime $CurrentUKTime is Inside of the shutdown date schedule $start`n " 

         return $true       

     

    }

    else

    {

        Write-Host "`nCurrentTime $CurrentUKTime is Outside of the shutdown date schedule $start`n " 

        return $false

    

    }

}

 

function newDayCheck ($daySchedules,$VMCurrentStatus,[datetime]$CurrentUKTime)

{

#$CurrentUKTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [System.TimeZoneInfo]::FindSystemTimeZoneById("GMT Standard Time"))  

#[datetime] $CurrentUKTime = "09 March 2019 19:05:00"

   

$day = $daySchedules | Where-Object {$_ -match $CurrentUKTime.DayOfWeek}

 

$Weekday = $day.split(':')[0]

$StopTime = $day.split(':')[1]

$StartTime = $day.split(':')[2]

 

Write-Host $daySchedules

Write-Host $day

write-host "Current Day: $weekday"

write-host "Start hour: $StartTime"

write-host "Stop hour: $StopTime"

Write-Host "Current Time: $($CurrentUKTime)"

 

  if($day -ne $null)

  {

       

       Write-Host "`nCurrent Day is in schedule`n"

 

      if($StartTime -ne '24' -and ($CurrentUKTime.Hour -eq $StartTime))

       {

        $DesiredState = "VM Running"

        Write-Host "`nDesired State is : ""$DesiredState""`n"

        return $DesiredState

       }

       elseif($StopTime -ne '24' -and ($CurrentUKTime.Hour -eq $StopTime))

       {

        $DesiredState = "VM Deallocated"

        Write-Host "`nDesired State is - ""$DesiredState""`n"

        return $DesiredState

       }

       else

       {       

        $DesiredState = $VMCurrentStatus

        Write-Host "`nDesired State is Current State which is: ""$DesiredState""`n"

        return $DesiredState

       }  

  }

  else

  {

    write-host "`nCurrent day is not in the schedule. Keep the current VM State`n"

    $DesiredState = "VM Running"

    return $DesiredState

  }




 } #end of newDayCheck

 

# Main Script Code

###################

 

# connect to azure

AzureConnect

 

#cls

 

#$VMList = @(Get-AzureRmResource | where {$_.ResourceType -like "Microsoft.*/virtualMachines" -and $_.Tags.Keys -contains "AutoShutdownSchedule" -and $_.Tags.keys -contains "SuspendSchedule" -and $_.ResourceGroupName -eq "azsu-rg-devtest-mib-001" } | sort Name)

 

$VMList = @(Get-AzureRmResource | where {$_.ResourceType -like "Microsoft.*/virtualMachines" -and $_.Tags.Keys -contains "AutoShutdownSchedule" -and $_.Tags.keys -contains "SuspendSchedule" } | sort Name)

 

#$VMList = @(Get-AzureRmResource | where {$_.ResourceType -like "Microsoft.*/virtualMachines" -and $_.Tags.Keys -contains "AutoShutdownSchedule" -and $_.Tags.keys -contains "SuspendSchedule" -and $_.Name -eq "azsu-d-db-161" } | sort Name)

 

foreach ($VM in $VMList)

{

$VMCurrentStatus = (Get-AzureRmVM -ResourceGroupName $VM.ResourceGroupName -Name $VM.Name -Status).Statuses[1].DisplayStatus

$DesiredState = $VMCurrentStatus

 

#$VMCurrentStatus = "VM running"

#$VMCurrentStatus = "VM Deallocated"

 

Write-Output "***************************************************************"

Write-Output "`n`nCurrent state of the VM $($VM.Name) is $($VMCurrentStatus)"

 

$tags = $VM.Tags

 

#$tags = @{ "AutoShutdownSchedule" = "07 March 2019 11:00:00=>07 March 2019 12:00:00;Monday:24:24,Tuesday:24:24,Wednesday:24:24,Thursday:24:24,Friday:24:24,Saturday:24:24,Sunday:24:24"}

#$tags = @{ "AutoShutdownSchedule" = "08 March 2019 11:00:00=>11 March 2019 13:00:00;Monday:11:14,Tuesday:18:09,Wednesday:18:09,Thursday:18:09,Friday:18:09,Saturday:24:24,Sunday:24:24" ; "SuspendSchedule" = "No"}

#$tags = @{ "AutoShutdownSchedule" = ";Saturday:08:18,Sunday:20:23" ; "SuspendSchedule" = "No"}

 

Write-Output "`nAutoShutSchedule tag Value is : $($tags.AutoShutdownSchedule)"

$scheduler = $($tags.AutoShutdownSchedule)

#Write-Output "`n$scheduler"

#$dateRangeSchedules = $tags.AutoShutdownSchedule.Split(';')[0]

#$dateRangeSchedules = $dateRangeSchedules.Split(',')

#$daySchedules = ($tags.AutoShutdownSchedule.Split(';')[0]).split(',')

$CurrentUKTime = [System.TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [System.TimeZoneInfo]::FindSystemTimeZoneById("GMT Standard Time"))

if ($scheduler.Contains(';'))

{

    $shutdownschedule,$dailyschedule = ($tags.AutoShutdownSchedule.Split(';'))

    $daySchedules = $dailyschedule.split(',')

    Write-Output "DaySchedule = $($daySchedules) :: `n Shutdown = $($shutdownschedule) :: `n"

}

else {

    $daySchedules = ($tags.AutoShutdownSchedule.Split(';')[0]).split(',')

    Write-Output "DaySchedule = $($daySchedules) :: `n "

}

 

#[datetime] $CurrentUKTime = "20 March 2019 09:05:00"

 

$day = $daySchedules | Where-Object {$_ -match $CurrentUKTime.DayOfWeek}

Write-Output "Day = $($day) `n "

 

    if ($tags.SuspendSchedule -eq "No")

    { 

 

        if($daySchedules -ne $null -and $day -ne $null)

        {   

            #$day = $daySchedules | Where-Object {$_ -match $CurrentUKTime.DayOfWeek}

            $Weekday = $day.split(':')[0]

            $StopTime = $day.split(':')[1]

            $StartTime = $day.split(':')[2]

            $IsDay = newDayCheck $daySchedules $VMCurrentStatus $CurrentUKTime

            $DesiredState = $IsDay

            Write-Output "`nDay: $Weekday :: Stop at: $StopTime :: Start at: $StartTime `n"

        }

        else

        {

         Write-Output "`nCurrentTime $CurrentUKTime is outside of the shutdown date schedule $StopDateAndTime & $StartDateAndTime`n " 

         $DesiredState = "VM Running"

        }

 

    

        # Apply the desired State to the VM

        Write-Output "`nCurrent State is: ""$VMCurrentStatus""`nDesiredState is: ""$DesiredState""`n"

        if($DesiredState -eq "VM deallocated" -and $VMCurrentStatus -ne "VM deallocated")

        {

            Write-Output "Shutdown the VM $($VM.Name) ...."

            Stop-AzureRmVM -Name $VM.Name -ResourceGroupName $VM.ResourceGroupName -Force -AsJob

        }

        elseif($DesiredState -eq "VM Running" -and $VMCurrentStatus -ne "VM Running")

        {

            Write-Output "Power on the VM $($VM.Name) ...."

            Start-AzureRmVM -Name $VM.Name -ResourceGroupName $VM.ResourceGroupName -AsJob

  

        }

        else

        {

            Write-Output "Keep the VM's Current State"

        }

    } # End of if ($tags.SuspendSchedule -eq "No")

    else

        {

            Write-Output "Auto Shutdown Schedule Suspended, Keeping the VM's Current State"

        }

}

Write-Output "***************************************************************"

Write-Output "Listing the Background Jobs if any"

Get-Job

 