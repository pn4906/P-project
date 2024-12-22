const express = require('express');
const router = express.Router();
const ranking = require('../lib/ranking_2');

// 카테고리별 상품 조회 페이지 : GET /?category=best&subcategory=all
router.get('/', (req, res) => {
    try {
        ranking.view(req, res);
    } catch (err) {
        console.error("Error in ranking view:", err.message);
        res.status(500).json({ success: false, error: "Server error occurred while fetching ranking data." });
    }
});

// 검색 API: GET /search/:keywords


module.exports = router;