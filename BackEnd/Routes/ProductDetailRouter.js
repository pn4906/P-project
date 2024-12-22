const express = require('express');
const router = express.Router();
const detail = require('../lib/detail');

// GET /products/:id - 특정 상품의 상세 정보 조회
router.get('/:id', async (req, res) => {
    try {
        const productId = req.params.id;
        console.log(productId)
        // 유효성 검사 (숫자인지 확인)
        if (isNaN(productId)) {
            return res.status(400).json({
                success: false,
                error: "Invalid product ID. Product ID must be a number."
            });
        }


        // 상세 정보 조회
        await detail.detail(req, res);
    } catch (err) {
        console.error("Error in ProductDetailRouter:", err.message);
        res.status(500).json({
            success: false,
            error: "Server error occurred while fetching product details."
        });
    }
});

module.exports = router;