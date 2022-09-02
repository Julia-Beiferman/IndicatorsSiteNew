$Token = "k3ll5f2ggf6zwpddqtfyryxbxt6jedrwfmcmrrsbqr4m52p5s34q"
$encoded_token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$Token"))
$ado_headers = @{Authorization="Basic $encoded_token"}
$item_id = "194081"
$ado_base = "https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/workitems/" + $item_id + "?api-version=6.0"
$prs = Invoke-RestMethod -Uri "$ado_base" -Method GET -Headers $ado_headers
$myjson = $prs | ConvertTo-Json
Write-Output $myjson