const db = require('./db');

module.exports = {
    // /product/:id/?keywords=5&positive=0
    detail: (req, res) => {
        let id = req.params.id; // 요청된 상품 ID
        console.log(id); 

        id = parseInt(id,10) 
        
        console.log("세부 상세 페이지 접속 => 리뷰와 상품 정보들을 띄움")


        // 긍정여부 전체 0 긍정 1 부정 2 
        
        // 상품 정보 전달 => 상품별 플랫폼폼이 2개가 올때 수정? 해야될듯 
        const query1 = `
            SELECT 
                P.*, PD.*
            FROM 
                products P
            LEFT JOIN 
                products_detail PD ON P.product_id = PD.product_id
            WHERE 
                P.product_id = ?;
        `;

        // 해당하는 상품의 리뷰 모두 전달 => 프론트가 시행 
        const query2 = `select * from reviews where product_id = ?;`

        
        // 해당하는 리뷰만 가져오기 
        
        db.query(query1, [id], (err, products) => {
            db.query(query2, [id], (err2,reviews) => {
                    if (err || err2) {
                        console.error("SQL Error:", err.message);
                        return res.status(500).json({
                            success: false,
                            error: "Database error occurred while fetching product details."
                        });
                    }


                    // 긍정,부정 산출 함수                     
                    let positive = new Array(5).fill(0); // 0으로 초기화된 크기 5의 배열
                    let negative = new Array(5).fill(0);  
    
                    for(i=0;i<reviews.length;i++) {
                        // 사이즈 디자인 품질 기능성 가격  
                        //   0       1    0    0     1 
                        review = reviews[i].review_cate; 
                        
                        for(j=0;j<5;j++) {
                            num = parseInt(review[j], 10)
                            if(num == 1) {
                                positive[j] += 1; 
                            } else if(num == 2) {
                                negative[j] += 1; 
                            }
                        }
                    }
                    //긍정 비율 산출 
                    let positive_rate = new Array(5).fill(0);
                    for(i=0;i<5;i++) {
                        if((positive[i]+negative[i]) != 0) {
                            positive_rate[i] = positive[i] / (positive[i]+negative[i])
                        }       
                        console.log(positive_rate[i])
                    }

                    positive_rate = positive_rate.map(rate => (rate * 100).toFixed(0));
                    console.log(positive_rate)

                    // ================================= 

                    if (products.length === 0) {
                        return res.status(404).json({
                            success: false,
                            message: "Product not found."
                        });
                    }

                    // 플랫폼 상품 판매 정보 전달 
                    const platforms = products.map(item => ({
                        platformName: item.platform_name,
                        price: item.price,
                        flatform_path: item.flatform_path,
                        discountRate: item.discount_rate,
                        productLink: item.product_link,
                        imagePath: item.image_path
                    }));

                    const minPrice = Math.min(...platforms.map(platform => platform.price));
                    const lowPricePlatform = platforms.find(platform => platform.price === minPrice);

                    res.json({
                            success: true,
                            products: products,  // 상품 정보 
                            platforms: platforms, // 각 플랫폼 판매 정보 
                            lowPricePlatform : lowPricePlatform, // 가장 가격 낮은 플랫폼 정보
                            positive_rate: positive_rate, // 각 키워드별 긍정 비율 
                            reviews: reviews   // 해당 모든 리뷰 전달                          
                        });
                })
            })
    },
};