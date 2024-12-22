const express = require('express');
const router = express.Router();
const ranking = require('../lib/ranking_2');

// 검색 API: GET /:keywords
router.get('/:keywords', (req, res) => {
    console.log('Search request received:', req.params.keywords);
    try {
        ranking.search(req, res);
    } catch (err) {
        console.error("Error in ranking search:", err.message);
        res.status(500).json({ 
            success: false, 
            error: "Server error occurred while searching for products." 
        });
    }
});

module.exports = router;