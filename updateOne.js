const mongoose = require('mongoose');
const Run = require('./models/Run');
const Module = require('./models/Module')
var async = require('async');
var bodyParser = require('body-parser');
const { PowerShell }  = require('node-powershell');

//connect to mongodb
const dbURL = 'mongodb://localhost:27017/SRC';
mongoose.connect(dbURL, {useNewUrlParser: true, useUnifiedTopology: true});

var updateDoc = {
    name: 'sdf',
    ww: 'fds',
    suite: 'suitfdse',
    iteration: {
       Calibration:      [1,1],
       Diagnostics:      [123132,12313],
       ChannelCard:      [233,233],
       DPS:              [],
       SysVal:           [],
       HalInit:          []
    },
    comments:            'fdsf',
 };

 

const sumList = ['CH4HBI10004', 'CH4HBI10007', 'CH4HBI10017', 'CH4HBI10027', 'CH4HBI10107'];

const users = async(index) =>{ 
   var query = {"name": index};
   const result = await Run.find(query).sort({'ww': -1}).collation({locale: 'en_US', numericOrdering: true})
   return result[0]
}


const mapLoop = async _ => {
   console.log('Start')
 
   const promises = sumList.map(async fruit => {
     const numFruit = await users(fruit)
     return numFruit
   })
 
   const numFruits = await Promise.all(promises)
   console.log(numFruits)
 
   console.log('End')
 }



const poshInstance = async () => {
   const ps = new PowerShell({
      executionPolicy: 'Bypass',
      noProfile: true
   })

   const command = PowerShell.command`$Token = "k3ll5f2ggf6zwpddqtfyryxbxt6jedrwfmcmrrsbqr4m52p5s34q"
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
   Write-Output $qured.value | ConvertTo-Json`
   const output = await ps.invoke(command)
   ps.dispose()
   var myJson = JSON.parse(output.raw)
   return myJson

}

(async () => 
{
   var myJson = await poshInstance()
   console.log(myJson.url)
})();
