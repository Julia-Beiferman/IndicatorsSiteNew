$Token = "5h6mmjsesx6wfalwiagfl6vesyptbp4a4gu6g7ng72oiau56c6va"
$encoded_token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$Token"))
$ado_headers = @{Authorization="Basic $encoded_token"}

Write-Output $encoded_token

$wiqlbase = "https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/wiql?api-version=6.0"
$queryTag = "Errata"

#gets a list of ids based on query
$query = @{
    query = "Select [System.Id], [System.Title], [System.State] 
    From WorkItems 
    Where 
    [System.WorkItemType] <> ''
    AND [System.Description] Contains '\\datagroveaz.amr.corp.intel.com\sttd\HDMT\TesterIntegration\HISV\SRCLoopingData\CH4HDMTISV02\2022_07_08_15_48_22_Run'
    AND [System.Description] Contains 'DPS'"
}

$queryJson = $query | ConvertTo-Json

$reg = Invoke-RestMethod -Method 'Post' -Uri "$wiqlbase" -Headers $ado_headers -Body $queryJson -ContentType "application/json"
Write-Output $reg.workItems.id

#Get work items batch
#shows all the info about a word item given a list of ids 
$batchURL = "https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/workitemsbatch?api-version=6.0"
$queryBatch =  @{
    ids= @($reg.workItems.id)
    fields = @("System.Id", "System.Title", "TOS.Type", "TOS.Found_In_Release")
}

$queryBatchJson = $queryBatch | ConvertTo-Json
Write-Output $queryBatchJson


$qured = Invoke-RestMethod -Method 'Post' -Uri "$batchURL" -Headers $ado_headers -Body $queryBatchJson -ContentType "application/json"
Write-Output $qured.value | ConvertTo-Json
Write-Output $reg.workItems.id