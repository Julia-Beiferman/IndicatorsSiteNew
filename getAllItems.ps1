$Token = "k3ll5f2ggf6zwpddqtfyryxbxt6jedrwfmcmrrsbqr4m52p5s34q"
$encoded_token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$Token"))
$ado_headers = @{Authorization="Basic $encoded_token"}

$wiqlbase = "https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/wiql?api-version=6.0"
$queryTag = "Errata"

$query = @{
    query = "Select [System.Id], [System.Title], [System.State] 
    From WorkItems 
    Where 
    [System.WorkItemType] <> ''
    AND [System.Description] Contains '\\datagroveaz.amr.corp.intel.com\sttd\HDMT\TesterIntegration\HISV\SRCLoopingData'"
}

$queryJson = $query | ConvertTo-Json

$reg = Invoke-RestMethod -Method 'Post' -Uri "$wiqlbase" -Headers $ado_headers -Body $queryJson -ContentType "application/json"
$read = $reg | ConvertTo-Json

#Get work items batch

$batchURL = "https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/workitemsbatch?api-version=6.0"
$queryBatch =  @{
    ids= @($reg.workItems.id)
    fields = @("System.Id", "System.Title", "TOS.Type", "TOS.Found_In_Release")
}

$queryBatchJson = $queryBatch | ConvertTo-Json
#Write-Output $queryBatchJson

$qured = Invoke-RestMethod -Method 'Post' -Uri "$batchURL" -Headers $ado_headers -Body $queryBatchJson -ContentType "application/json"
Write-Output $qured.value | ConvertTo-Json