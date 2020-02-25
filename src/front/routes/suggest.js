var express = require('express');
var router = express.Router();

router.get('/', function (req, res, next) {
    const { key } = req.query
    res.json({
        succ: true,
        data: [key + '1', key + '2', key + '3', key + '4', key + '5']
    })
});

module.exports = router;
