const express = require('express');
const mongoose = require('mongoose');
const Run = require('./models/Run');
const Module = require('./models/Module');
var bodyParser = require('body-parser');
const { PowerShell }  = require('node-powershell');
const fs = require('fs');

const app = express();

//connect to mongodb
const dbURL = 'mongodb://localhost:27017/SRC';
mongoose.connect(dbURL, {useNewUrlParser: true, useUnifiedTopology: true})
    .then((result) => app.listen(8081))
    .catch((err) => console.log(err));

app.set('view engine', 'ejs');
console.log('Running on 127.0.0.1:8081');

//middleware
app.use(express.static('public'));
app.use(express.static("views"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use((req, res, next) => {
  res.locals.path = req.path;
  next();
});
// create application/json parser
var jsonParser = bodyParser.json()
 
// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })

//routes
app.get('/', function(req, res){
   res.redirect('/runs')
 })

app.get('/runs', function(req, res){

   Run.find()
   .then((result) => 
      Run.find().distinct('suite')
      .then((suiteDist) =>  
         Run.find().distinct('tos.formatted')
         .then((tosDist) =>
         res.render('runReports', {data: result, tosDist: tosDist, suiteDist: suiteDist})))
   ); 
 })


app.get('/runs/:id', function(req, res){
   Run.findById()
   .then((result) => res.render('runReports', {data: result, tosDist: tosDist, suiteDist: suiteDist}))
   .catch((err) => console.log(err)); 
})

 app.post('/runs', jsonParser, function(req, res){

   var updateDoc = {
      $set: 
      {
      name: req.body.name,
      ww: req.body.ww,
      suite: req.body.suite,
      iteration: {
         Calibration:      req.body.Calibration,
         Diagnostics:      req.body.Diagnostics,
         ChannelCard:      req.body.ChannelCard,
         DPS:              req.body.DPS,
         SysVal:           req.body.SysVal,
         HalInit:          req.body.HalInit
      },
      comments:            req.body.comment,
      },
   };

   const filter = { _id: req.body.id };

   Run.updateOne(filter, updateDoc, function (err, docs) {
      if (err){
          console.log(err)
      }
      else{
          console.log("Updated Docs : ", docs);
      }
   });

   Run.find()
   .then((result) => res.render('runReports', {data: result, tosDist: tosDist, suiteDist: suiteDist}))
   .catch((err) => console.log(err));
 })

 app.post('/runs/addcomment', jsonParser, function(req, res){

   var addComment = {
      $set: {
         comments:   req.body.comment
      }
   }

   const filter = { _id: req.body.id };

   Run.updateOne(filter, addComment, function (err, docs) {
      if (err){
          console.log(err)
      }
      else{
          console.log("Updated Docs : ", docs);
      }
   });

   res.redirect('/runs');
   
 })

app.post('/runs/deleteRun', jsonParser, function(req, res){

   const filter = { _id: req.body.id };

   Run.deleteOne(filter, function (err, docs) {
      if (err){
          console.log(err)
      }
      else{
          console.log("Deleted Docs : ", docs);
      }
   });

})


 app.get('/summary/:version', function(req, res){
   var sumList = [];
   const hbi = ['CH4HBI10004', 'CH4HBI10007', 'CH4HBI10017', 'CH4HBI10027', 'CH4HBI10107'];
   const gen2 = ['CH4HDMTISV01', 'CH4HDMTISV02', 'CH4HDMTISV05'];
   const gen2e = ['CH4HDMTISV06', 'CH4HDMTISV07', 'CH4HDMTISV08'];
   const gen25 = ['CH4HDMTISV01', 'CH4HDMTISV02', 'CH4HDMTISV05'];
   const gen3 = ['CH4HDMTISV01', 'CH4HDMTISV02', 'CH4HDMTISV05'];

   switch(req.params.version){
      case 'HBI':
         sumList = hbi;
         break;
      case 'Gen2':
         sumList = gen2;
         break;
      case 'Gen2E':
         sumList = gen2e;
         break;
      case 'Gen2.5':
         sumList = gen25;
         break;
      case 'Gen3':
         sumList = gen3;
         break;

   }

   const latestTest = async(index) =>{ 
      var query = {"name": index};
      const result = await Run.find(query).sort({'ww': -1}).collation({locale: 'en_US', numericOrdering: true})
      return result[0]
   }
   
   
   const mapLoop = async _ => {    
      const promises = sumList.map(async tester => {
        const latestRun = await latestTest(tester)
        return latestRun
      })
    
      const mostRecent = await Promise.all(promises)
      res.render('summary', {data: mostRecent, version: req.params.version})

   }
   
   mapLoop()

})

var failReport = []
app.get('/failReport/:id', function(req, res){
   var module = []
   var src = []
           
   //show both collections

   Module.find({"assocSRC": req.params.id})
   .then((module => {
      Run.findById(req.params.id)
      .then(data => {
         res.render('failReport', {dat: data, module: module})})
      .catch((err) => console.log(err))
   }))
   .catch((err) => console.log(err));
   

})

let ejsOptions = {
   async: true
}

app.get('/errata', function(req, res){

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
      Run.find().distinct('tos.formatted')
      .then((tosDist) => res.render('errata', {tosDist: tosDist, tickets: myJson}))
      .catch((err) => console.log(err)); 
   })();
   
})

app.get('/contact', function(req, res){
   Run.find()
  res.render('contact');
})

app.get('/analytics', function(req, res){ //option to add tester name as a parameter

   Run.find({name: 'CH4HDMTISV01' })
   .then((result) => res.render('analytics', {data: result, testerName: 'CH4HDMTISV01'}))
   .catch((err) => console.log(err)); 
})

app.get('/analytics/:testername', function(req, res){ //option to add tester name as a parameter

   Run.find({name: req.params.testername })
   .then((result) => res.render('analytics', {data: result, testerName: req.params.testername}))
   .catch((err) => console.log(err)); 
})
