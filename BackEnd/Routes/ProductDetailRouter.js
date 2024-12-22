const express = require('express');
const router = express.Router();
const detail = require('../lib/detail');

// GET /products/:id - 특정 상품의 상세 정보 조회
// 상품 상세 정보 조회
router.get('/:id', async (req, res) => {
    try {
        const productId = req.params.id; // URL에서 :id 값을 받아옵니다.
        console.log(productId); // 확인용 로그

        // 유효성 검사
        if (isNaN(productId)) {
            return res.status(400).json({
                success: false,
                error: "Invalid product ID. Product ID must be a number."
            });
        }

        // 상품 상세 정보 조회 처리 (다른 코드에서 해당 상품 정보를 처리하도록 할 수 있음)
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