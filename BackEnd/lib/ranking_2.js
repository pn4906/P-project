const db = require('./db'); // 데이터베이스 연결

module.exports = {
    // 상품 목록 조회
    view: (req, res) => {
        // main_category와 sub_category 값 처리
        let mainCategory = req.query.category || 'best'; // 기본값: 'best'
        let subCategory = req.query.subcategory || 'all'; // 기본값: 'all'
        console.log("Received Parameters:", { mainCategory, subCategory });

        const mainCategoryMapping = {
            "best": null,  // 전체
            "men": 0,    // 남성
            "women": 1   // 여성
        };

        const subCategoryMapping = {
            "all": null,   // 전체
            "top": 1,    // 상의
            "outer": 2,  // 아우터
            "bottom": 3, // 하의
            "shoes": 4   // 신발
        };

        // 매핑된 값 적용
        mainCategory = mainCategoryMapping[mainCategory.toLowerCase()] || null;
        subCategory = subCategoryMapping[subCategory.toLowerCase()] || null;

        const query1 = `
            SELECT 
                P.*, PD.* 
            FROM 
                products P
            LEFT JOIN 
                products_detail PD 
                ON P.product_id = PD.product_id
                AND PD.price = (
                SELECT MIN(price)
                FROM products_detail
                WHERE products_detail.product_id = P.product_id
                )
            WHERE 
                (? IS NULL OR P.main_category = ?) 
                AND 
                (? IS NULL OR P.sub_category = ?)
            ORDER BY 
                P.ranking_score DESC
            LIMIT 300
        `;

        const query2 = `
            select MIN(price), MAX(price) 
            from products_detail 
            where 
        `
        const params = [mainCategory, mainCategory, subCategory, subCategory];

        db.query(query1, params, (err, results) => {
            if (err) {
                console.error("SQL Query Error:", err.message, "SQL:", query1, "Params:", params);
                return res.status(500).json({ success: false, error: "Database error occurred" });
            }
            console.log("Query results:", results?.length || 0);  // 결과 개수 로그 추가
            if (results.length === 0) {
                return res.status(404).json({ success: false, message: "No products found." });
            }

            res.json({
                success: true,
                data: results
            });
        });
    },

    //  ========================================================================================

    // 상품 검색
    search: (req, res) => {
        const keyword = req.params.keywords;
        console.log("Search keyword:", keyword);
        
        // 검색어가 공백이거나 없는 경우
        if (!keyword || keyword.trim().length === 0) {
            return res.status(400).json({ 
                success: false, 
                error: "검색어를 입력해주세요." 
            });
        }

        // 검색어를 공백으로 분리하고 빈 문자열 제거
        const keywords = keyword.split(/\s+/).filter(k => k.length > 0);
        const whereClauses = keywords.map(() => '(P.product_name LIKE ? OR P.brand LIKE ?)').join(' AND ');

        const query = `
            SELECT 
                P.*, PD.* 
            FROM 
                products P
            LEFT JOIN 
                products_detail PD 
                ON P.product_id = PD.product_id
                AND PD.price = (
                    SELECT MIN(price)
                    FROM products_detail
                    WHERE products_detail.product_id = P.product_id
                )
            WHERE ${whereClauses}
            ORDER BY 
                CASE 
                    WHEN P.brand LIKE ? THEN 1
                    WHEN P.product_name LIKE ? THEN 2
                    ELSE 3
                END,
                P.ranking_score DESC
        `;

        // 파라미터 생성
        const params = [];
        keywords.forEach(k => {
            params.push(`%${k}%`, `%${k}%`);
        });
        params.push(`%${keyword}%`, `%${keyword}%`);  // 정확한 매칭용

        console.log("Executing SQL query:", query);
        console.log("Query parameters:", params);

        db.query(query, params, (err, results) => {
            if (err) {
                console.error("SQL Error:", err.message);
                return res.status(500).json({ success: false, error: "Database error occurred" });
            }

            console.log("Query results:", results?.length || 0);

            if (results.length === 0) {
                return res.status(404).json({
                    success: false,
                    message: "검색 결과가 없습니다."
                });
            }

            res.json({
                success: true,
                data: results
            });
        });
    }
};