const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const modSchema = new Schema({

    module_name: String,
    assocSRC: Schema.Types.ObjectId,
    deltaTime: Number,
    module_data: [ {
        module_execution: String,
        module_name:      String,
        data: {
            runtime:        String,
            errors:         Array
        }
    } ],
    summary_data: {
        name: String,
        total: Number,
        failing: Number,
        last_completion: String          
    }
}, {timestamps: true});

var collectionName = 'Modules';
var run = mongoose.model('Module', modSchema, collectionName)

module.exports = run;