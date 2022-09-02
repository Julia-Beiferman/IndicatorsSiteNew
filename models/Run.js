const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const runSchema = new Schema({
    name: String,
    ww: String,
    tos: {
        version:        String,
        major   :       String,
        minor   :       String,
        patch   :       String,

        build:          String,
    },
    suite: String,
    summary: {
        Calibration:      Array,
        Diagnostics:      Array,
        ChannelCard:      Array,
        DPS:              Array,
        SysVal:           Array,
        HalInit:          Array
    },
    comments:             Array,
    datagrove:            String,
    date:                 Date,
    ados:                 Array,
    tester_hw_config: {
        config_string:    String,
        hw_config_xml:    String
    },
    RunSeed:	          String,
    RunFlow:		      String,
    RunType: 	          String,
    start_time:           String,
    end_time:             String

}, {timestamps: true});

var collectionName = 'VerboseRuns';
var run = mongoose.model('VerboseRun', runSchema, collectionName)

module.exports = run;