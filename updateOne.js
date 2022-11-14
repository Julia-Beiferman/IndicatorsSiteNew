const mongoose = require('mongoose');
const Run = require('./models/Run');
const Module = require('./models/Module')
var async = require('async');
var bodyParser = require('body-parser');
const { PowerShell } = require('node-powershell');
//const { fetch } = require('node-fetch');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
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


const fetch = require('node-fetch');

// Example POST method implementation:
async function postData() {
  const url = 'https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/wiql?api-version=6.0';
  let data = `{"query": "Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.WorkItemType] <> '' AND [System.Description] Contains 'datagroveaz.amr.corp.intel.com'"}`
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Authorization": "Basic " + "OmEyZ3pzcHo0ZTNwNGg0YTdtbmR6c3E2em43Z2N4c2ZzZ2F3MnZhdmxua2J6eHIzaXFjcXE=",
      "Content-Type": "application/json"
    },
    body: data // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}

async function getData(ids) {
  
  
  const url = 'https://dev.azure.com/ATTD/HDMT_Prod/_apis/wit/workitemsbatch?api-version=6.0';
  let data = `{
    "ids": [` + ids + `],
    fields: ["System.Id", "System.Title", "TOS.Type", "TOS.Found_In_Release"]
  }`

  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Authorization": "Basic " + "OmEyZ3pzcHo0ZTNwNGg0YTdtbmR6c3E2em43Z2N4c2ZzZ2F3MnZhdmxua2J6eHIzaXFjcXE=",
      "Content-Type": "application/json"
    },
    body: data // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}

postData()
  .then((data) => {
    let ids = []
    data.workItems.forEach(item => {
      ids.push(item.id)
    })
    getData(ids)
      .then((out) => {
        console.log(out.value)
      })
    
  });
