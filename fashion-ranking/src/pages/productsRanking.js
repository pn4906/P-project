import React, { useState, useEffect, useMemo } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import '../styles/productsRanking.css';

const FashionRankingTable = () => {
    const [data, setData] = useState([]); // 백엔드로부터 받은 데이터 
    const [filterdData, setFilterdData] = useState([]) // 가격 필터링한 상품 데이터 
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchParams] = useSearchParams();
    const [sortOption, setSortOption] = useState('default'); // 랭킹순, 긍정 비율순, 리뷰순 설정값 

    // 가격 설정 
    const [minPrice, setMinPrice] = useState(2000); // 초기 최소값
    const [maxPrice, setMaxPrice] = useState(254000); // 초기 최대값

    const [initalMinPrice, setInitalMinPrice] = useState(); // 제일 상품 가격 낮은 값 
    const [initalMaxPrice, setInitalMaxPrice] = useState(); // 제일 상품 가격 높은 값 

    // 가격 설정 탭 오픈 여부   
    const [isPriceModalOpen, setIsPriceModalOpen] = useState(false);
    const togglePriceModal = () => {
        setIsPriceModalOpen(!isPriceModalOpen);
    };

    // 1. 사용자가 가격 설정 바꿨을때의 함수 
    const handleMinPriceChange = (e) => {
        const value = Math.min(Number(e.target.value), maxPrice - 1000); // 최소값은 최대값보다 작아야 함
        setMinPrice(value);
    };

    const handleMaxPriceChange = (e) => {
        const value = Math.max(Number(e.target.value), minPrice + 1000); // 최대값은 최소값보다 커야 함
        setMaxPrice(value);
    };

    // 2. 슬라이더 값 바꿀때 
    const handleSliderChange = (e, type) => {
        const slider = document.querySelector('.price-slider');
        slider.style.setProperty('--min-value', minPrice); // 최소값
        slider.style.setProperty('--max-value', maxPrice); // 최대값
        const value = Number(e.target.value);
        if (type === 'min') {
            setMinPrice(Math.min(value, maxPrice - 1000));
        } else if (type === 'max') {
            setMaxPrice(Math.max(value, minPrice + 1000));
        }
    };

    // 가격 필터링시 일치하는 상품만 보이게 설정 
    const filterByPrice = (data, minPrice, maxPrice) => {
        return data.filter(product => {
            return product.price >= minPrice && product.price <= maxPrice;
        });
    };

    // 2. 설정하기 버튼 클릭 시 필터링 로직 적용
    const applyPriceFilter = () => {
        const filteredData = filterByPrice(data, minPrice, maxPrice);
        setFilterdData(filteredData); // 필터링된 데이터를 저장
        setIsPriceModalOpen(false); // 모달 닫기
    };

    // 데이터 fetch
    useEffect(() => {
        const fetchData = async () => {
            try {
                const keyword = searchParams.get('keyword');
                const category = searchParams.get('category')?.toLowerCase() || 'best';
                const subcategory = searchParams.get('subcategory');
                const finalSubcategory = subcategory === 'undefined' || !subcategory ? 'all' : subcategory.toLowerCase();

                // 검색어 길이 체크
                if (keyword && keyword.trim().length === 0) {
                    setError('검색어를 입력해주세요.');
                    setLoading(false);
                    return;
                }

                console.log('URL Parameters:', JSON.stringify({
                    keyword: keyword || 'null',
                    category,
                    subcategory: finalSubcategory
                }, null, 2));

                // 검색어가 있을 때는 검색 API를, 없을 때는 카테고리 API를 호출
                const apiUrl = keyword && keyword.trim().length > 0
                    ? `${process.env.REACT_APP_API_URL}/search/${encodeURIComponent(keyword)}`
                    : `${process.env.REACT_APP_API_URL}?category=${category}&subcategory=${finalSubcategory}`;

                console.log('API URL:', apiUrl);

                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `서버 응답 실패 (상태 코드: ${response.status})`);
                }

                const responseData = await response.json();

                // 응답 데이터 로그
                console.log('API Response Details:', JSON.stringify({
                    status: response.status,
                    success: responseData.success,
                    totalItems: responseData.data?.length,
                    sampleItems: responseData.data?.slice(0, 2).map(item => ({
                        product_id: item.product_id,
                        product_name: item.product_name,
                        brand: item.brand
                    }))
                }, null, 2));

                if (!responseData || !Array.isArray(responseData.data)) {
                    console.error('Invalid response format:', JSON.stringify(responseData, null, 2));
                    throw new Error('API 응답 데이터 형식이 올바르지 않습니다.');
                }

                // 카테고리별 최저, 최고 가격 구하여 저장 
                const prices = responseData.data.map(item => item.price); // 데이터에서 price 값만 추출
                const minPrice = Math.floor(Math.min(...prices) / 1000) * 1000; // 최저 가격을 1000원 단위로 내림
                const maxPrice = Math.ceil(Math.max(...prices) / 1000) * 1000; // 최고 가격을 1000원 단위로 올림

                setInitalMinPrice(minPrice);
                setInitalMaxPrice(maxPrice);
                setMinPrice(minPrice);
                setMaxPrice(maxPrice);

                // 받은 상품 보를 저장
                setData(responseData.data);
                setFilterdData(responseData.data);
                console.log('Data updated with', responseData.data.length, 'items');
                setLoading(false);
            } catch (err) {
                console.error('Error in fetchData:', err);
                setError(`데이터를 불러오는데 실패했습니다. (${err.message})`);
                setLoading(false);
            }
        };

        fetchData();
    }, [searchParams]);

    // 정렬된 데이터 계산
    const sortedData = useMemo(() => {
        return [...filterdData].sort((a, b) => {
            if (sortOption === 'ranking') {
                return b.ranking_score - a.ranking_score;
            } else if (sortOption === 'review') {
                return b.review_count - a.review_count;
            } else if (sortOption === 'positive') {
                return b.positive_rate - a.positive_rate;
            }
            return 0;
        });
    }, [filterdData, sortOption]);

    const getRatingColorClass = (rating) => {
        if (rating >= 90) return 'excellent';
        if (rating >= 80) return 'great';
        if (rating >= 70) return 'good';
        if (rating >= 60) return 'fair';
        return 'poor';
    };

    if (loading) {
        return <div className="ranking-container">로딩 중...</div>;
    }

    if (error) {
        return <div className="ranking-container">에러: {error}</div>;
    }

    return (
        <div className="ranking-container">
            
            <div className="price-filter-container">
            <div className="sort-container">
                <select
                    name="sort_product"
                    value={sortOption}
                    onChange={(e) => setSortOption(e.target.value)}
                >
                    <option value="ranking">랭킹순</option>
                    <option value="review">리뷰 많은순</option>
                    <option value="positive">긍정 비율순</option>
                </select>
            </div>
                <button className="price-button" onClick={() => setIsPriceModalOpen(!isPriceModalOpen)}>
                    <i className="fas fa-filter"></i>가격 필터
                </button>
                <div className="price-range-card">
                    <div className="price-range-header">현재 설정한 범위</div>
                    <div className="price-range-values">
                        <span className="price-value">{minPrice.toLocaleString()}원</span>
                        <span className="price-separator"> ~ </span>
                        <span className="price-value">{maxPrice.toLocaleString()}원</span>
                    </div>
                </div>
            </div>

            {/* 가격 범위 설정 창 */}
            {isPriceModalOpen && (
                <div className="price-modal">
                    <div className="price-modal-header">
                        <h2>가격 범위 설정</h2>
                        <button className="close-button" onClick={togglePriceModal}>
                            ✕
                        </button>
                    </div>
                    <div className="price-modal-body">

                        {/* 1. 최소 가격 */}
                        <div className="price-inputs">
                            <div className='price-explain'>가격은 천원단위로 입력해주세요.</div>
                            <input
                                type="number"
                                value={minPrice}
                                min="0"
                                onChange={handleMinPriceChange}
                            />
                            <span class="unit1">원</span>
                            <span> ~ </span>
                            <input
                                type="number"
                                value={maxPrice}
                                min="0"
                                onChange={handleMaxPriceChange}
                            />
                            <span class="unit2">원</span>
                        </div>

                        {/* 2. 가격 슬라이더 */}
                        <div className="price-slider">
                            <input className='price-min'
                                type="range"
                                min={initalMinPrice}
                                max={initalMaxPrice}
                                step="1000"
                                value={minPrice}
                                onChange={(e) => handleSliderChange(e, 'min')}
                            />
                            <input className='price-max'
                                type="range"
                                min={initalMinPrice}
                                max={initalMaxPrice}

                                step="1000"
                                value={maxPrice}
                                onChange={(e) => handleSliderChange(e, 'max')}
                            />
                        </div>
                    </div>
                    <div className="price-modal-footer">
                        <button className="apply-button" onClick={applyPriceFilter}>
                            설정하기
                        </button>
                        <button className="cancel-button" onClick={togglePriceModal}>
                            취소
                        </button>
                    </div>
                </div>
            )}

            

            <div className="top-three">
                {sortedData.slice(0, 3).map((product, index) => {
                    const likes = product.positive_rate;
                    return (
                        <div key={product.product_id || index} className="product-item">
                            <div className="rank-badge">{index + 1}</div>
                            <Link to={`/products/${product.product_id}`}>
                                <div className="product-image-container">
                                    <img src={product.image_path} alt={product.product_name} className="product-image" />
                                </div>
                            </Link>
                            <div className="product-details">
                                <div className="product-info">
                                    <p className="brand">{product.brand || '브랜드 정보 없음'}</p>
                                    <Link to={`/products/${product.product_id}?keywords=5&positive=0`}>
                                        <p className="title">{product.product_name || '상품명 없음'}</p>
                                    </Link>
                                    <div className="price-info">
                                        <span className="price">
                                            {product.price !== undefined
                                                ? `${product.price.toLocaleString()}원~`
                                                : '가격 정보 없음'}
                                        </span>
                                    </div>
                                </div>
                                <div className="social-chart">
                                    <svg className="progress-ring" width="80" height="80">
                                        <circle
                                            className="progress-ring-circle progress-ring-background"
                                            stroke="#f2f2f2"
                                            cx="40"
                                            cy="40"
                                            r="36"
                                        />
                                        <circle
                                            className={`progress-ring-circle progress-ring-progress ${getRatingColorClass(likes)}`}
                                            cx="40"
                                            cy="40"
                                            r="36"
                                            strokeDasharray={`${(likes * 226.19) / 100} 226.19`}
                                        />
                                    </svg>
                                    <div className="progress-text">
                                        <div className="percent">
                                            {likes}
                                            <span className="percent-sign">%</span>
                                        </div>
                                        <div className="review-wrapper">
                                            <img
                                                src="/images/reviewCount.svg"
                                                alt="리뷰"
                                                className="review-icon"
                                            />
                                            <span className="review-count">
                                                {product.review_count || 0}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="bottom-groups">
                {[...Array(Math.ceil((sortedData.length - 3) / 5))].map((_, groupIndex) => (
                    <div className="bottom-group" key={groupIndex}>
                        {sortedData
                            .slice(3 + groupIndex * 5, 3 + (groupIndex + 1) * 5)
                            .map((product, index) => {
                                const likes = product.positive_rate;
                                return (
                                    <div key={product.product_id || index} className="product-item">
                                        <div className="rank-badge">
                                            {3 + groupIndex * 5 + index + 1}
                                        </div>
                                        <Link to={`/products/${product.product_id}`}>
                                            <div className="product-image-container">
                                                <img
                                                    src={product.image_path || '/images/placeholder.png'}
                                                    alt={product.product_name || '상품 이미지'}
                                                    className="product-image"
                                                />
                                            </div>
                                        </Link>
                                        <div className="product-details">
                                            <div className="product-info">
                                                <p className="brand">{product.brand || '브랜드 정보 없음'}</p>
                                                <Link to={`/products/${product.product_id}?keywords=5&positive=0`}>
                                                    <p className="title">{product.product_name || '상품명 없음'}</p>
                                                </Link>
                                                <div className="price-info">
                                                    <span className="price">
                                                        {product.price !== undefined
                                                            ? `${product.price.toLocaleString()}원~`
                                                            : '가격 정보 없음'}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="social-chart">
                                                <svg className="progress-ring" width="80" height="80">
                                                    <circle
                                                        className="progress-ring-circle progress-ring-background"
                                                        stroke="#f2f2f2"
                                                        cx="40"
                                                        cy="40"
                                                        r="36"
                                                    />
                                                    <circle
                                                        className={`progress-ring-circle progress-ring-progress ${getRatingColorClass(likes)}`}
                                                        cx="40"
                                                        cy="40"
                                                        r="36"
                                                        strokeDasharray={`${(likes * 226.19) / 100} 226.19`}
                                                    />
                                                </svg>
                                                <div className="progress-text">
                                                    <div className="percent">
                                                        {likes}
                                                        <span className="percent-sign">%</span>
                                                    </div>
                                                    <div className="review-wrapper">
                                                        <img
                                                            src="/images/reviewCount.svg"
                                                            alt="리뷰"
                                                            className="review-icon"
                                                        />
                                                        <span className="review-count">
                                                            {product.review_count || 0}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FashionRankingTable;