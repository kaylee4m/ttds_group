var express = require('express');
var router = express.Router();
const execSync = require('child_process').execSync;

router.get('/', function (req, res, next) {
    const { key, pageNum, category, startYear, endYear } = req.query
    let output = execSync('cd /home/ubuntu/ttds_group/src && python search.py --cfg config_server.yaml')
    output = output.toString()
    res.json({
        succ: true,
        data: {
            list: new Array(10).fill({
                title: 'Deep learning',
                author: 'Y LeCun',
                content: 'Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.Without knowledge,all is in vain.',
                cited: 1999
            }),
            speed: 0.07,
            total: 30008,
            output
        }
    })
});

module.exports = router;
