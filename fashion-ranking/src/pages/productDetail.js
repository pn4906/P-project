import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/productDetail.css';

// 리뷰 탭 설정
const REVIEW_TABS = [
  { id: 'all', label: '전체 리뷰 보기', keywordId: '5' }, // 전체 리뷰
  { id: '0', label: '사이즈', keywordId: '0' },          // review_cate[0]
  { id: '1', label: '디자인', keywordId: '1' },          // review_cate[1]
  { id: '2', label: '품질', keywordId: '2' },            // review_cate[2]
  { id: '3', label: '기능성/편의성', keywordId: '3' },   // review_cate[3]
  { id: '4', label: '가격', keywordId: '4' }             // review_cate[4]
];

const RatingDetail = ({ title, positiveRate, reviewCount, description, onClick }) => {
  const [isAnimated, setIsAnimated] = useState(false);
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const dashoffset = circumference - ((positiveRate / 100) * circumference);

  useEffect(() => {
    setIsAnimated(true);
  }, []);
//수정
  return (
    <div className={`rating-details ${isAnimated ? 'animated' : ''}`} onClick={onClick}>
      <div className="progress-circle">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle 
            className="progress-circle-bg"
            cx="60"
            cy="60"
            r={radius}
          />
          <circle 
            className="progress-circle-value"
            cx="60"
            cy="60"
            r={radius}
            strokeDasharray={circumference}
            strokeDashoffset={isAnimated ? dashoffset : circumference}
            transform="rotate(-90 60 60)"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div className="progress-text">
          <div className="progress-percentage">{positiveRate}%</div>
        </div>
      </div>
      <div className="rating-stats">
        <div className="rating-title">{title}</div>
        <div className="rating-description">
          {description}
        </div>
      </div>
    </div>
  );
};

const ProductDetail = () => {
  const { product_id } = useParams(); //상품 ID 추출
  const reviewDetailsRef = useRef(null);
  
  // 상태 관리
  const [productData, setProductData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reviews, setReviews] = useState([]); // 전체 리뷰 데이터
  const [filteredReviews, setFilteredReviews] = useState([]); // 필터링된 리뷰
  const [error, setError] = useState(null);  
  const [isPriceListOpen, setIsPriceListOpen] = useState(false);

  // 사용자 선택값 관리
  const [tabId, setTabId] = useState('all'); // 리뷰 카테고리 인덱스
  const [filterId, setFilterId] = useState(0); // 긍부정 여부 (0: 전체, 1: 긍정, 2: 부정)


   // 백엔드에서 리뷰 데이터 불러오기
  const fetchReviews = async () => {
    try {
      const url = `http://ceprj.gachon.ac.kr:60029/products/${product_id}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('리뷰 데이터를 불러오는데 실패했습니다.');

      const data = await response.json();
      setProductData(data);
      setReviews(data.reviews || []);
      setFilteredReviews(data.reviews || []); // 초기에는 전체 리뷰
      setLoading(false);
    } catch (err) {
      console.error(err.message);
      setError('리뷰 데이터를 불러오는 중 오류가 발생했습니다.');
      setLoading(false);
    }
  };

  // 필터링 함수: 리뷰 데이터 필터링
  const filterReviews = () => {
    if (!reviews.length) return;

    const filtered = reviews.filter((review) => {
      // 전체 탭일 경우 모든 리뷰를 보여줌
      if (tabId === 'all') {
        if (filterId === 1) return review.positive === 1; // 긍정 리뷰만
        if (filterId === 2) return review.positive === 0; // 부정 리뷰만
        return true; // 전체 리뷰
      }

      // tabId가 특정 키워드일 경우
      const categoryValue = parseInt(review.review_cate[tabId], 10); // tabId 인덱스 값 추출
      if (filterId === 0) return categoryValue !== 0; // 전체: 0이 아닌 값
      if (filterId === 1) return categoryValue === 1; // 긍정 리뷰
      if (filterId === 2) return categoryValue === 2; // 부정 리뷰
      return true;
    });

    setFilteredReviews(filtered); // 필터링된 리뷰 업데이트
  };

  // tabId나 filterId가 변경될 때마다 필터링
  useEffect(() => {
    filterReviews();
  }, [tabId, filterId, reviews]);

  // tabId가 바뀌면 filterId를 0으로 초기화
  useEffect(() => {
    setFilterId(0);
  }, [tabId]);


    // 페이지 로드 시 데이터 불러오기
    useEffect(() => {
      fetchReviews();
    }, [product_id]);

  // =========================================================================

  // 키워드별 만족도 분석 렌더링 함수
const renderKeywordAnalysis = () => {
  if (tabId !== null && tabId >= 0 && tabId <= 4) {
    const selectedTab = REVIEW_TABS[tabId+1]; // REVIEW_TABS에서 tabId를 사용하여 해당 카테고리 선택
    const positiveRate = productData.positive_rate[tabId]; // 긍정 비율

    return (
      <div className="keyword-rating-details">
        <RatingDetail
          title={
            <>
              {selectedTab.label} 만족도 <span className="ai-analysis-badge">AI 분석</span>
            </>
          }
          positiveRate={parseInt(positiveRate, 10)}
          reviewCount={productData.products[0].review_count}
          description={`이 제품의 ${selectedTab.label}에 대해 ${positiveRate}%의 구매자가 만족했어요. 관련 리뷰를 함께 확인해보세요.`}
        />
      </div>
    );
  }
  return null;
};




  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>{error}</div>;
  if (!productData) return <div>상품을 찾을 수 없습니다.</div>;

  // =========================================================================


  return (
    <>
      <div className="product-detail-container">
        {/* 상품 이미지 섹션 */}
        <div className="product-images-section">
          <div className="main-image">
            <img src={productData.lowPricePlatform.imagePath} alt="상품 이미지" />
          </div>
        </div>

        {/* 상품 정보 섹션 */}
        <div className="product-info-section">
          <div className="brand-name">{productData.products[0].brand}</div>
          <h1 className="product-title">{productData.products[0].product_name}</h1>

          {/* 평점 섹션 */}
          <div className="rating-section">
            <div className="rating-tab">
              긍정비율 {productData.products[0].positive_rate}% · 리뷰 {productData.products[0].review_count}건
            </div>           
            <div className="rating-details" onClick={() => reviewDetailsRef.current?.scrollIntoView({ behavior: 'smooth' })}>
              <RatingDetail 
                className="all-reviews-tab" // "전체 리뷰 분석" 탭에 클래스 추가
                title={<>전체 리뷰 분석 <span className="ai-analysis-badge">AI 분석</span></>}
                positiveRate={parseInt(productData.products[0].positive_rate)}
                reviewCount={productData.products[0].review_count}
                description={`총 ${productData.products[0].review_count}개의 리뷰 중 ${productData.products[0].positive_rate}%의 구매자가 만족했어요`}
              />
            </div>
          </div>

          {/* 가격 섹션 */}
          <div className="price-section">
            <div className="discount-price">
              <span className="discount">{productData.lowPricePlatform.discountRate}%</span>
              <span className="current-price">
                {productData.lowPricePlatform.price?.toLocaleString() ?? '가격 정보 없음'}원
              </span>
            </div>
          </div>

          {/* 가격 한눈에 보기 섹션 */}
          <div className="price-overview-tab" onClick={() => setIsPriceListOpen(!isPriceListOpen)}>
            <div className="price-overview-header">
              <span>가격 한눈에 보기</span>
              <span className={`arrow-icon ${isPriceListOpen ? 'open' : ''}`}>▼</span>
            </div>
          
            {isPriceListOpen && productData.platforms && (
            <div className="platform-list">
              {productData.platforms.map((platform, index) => (
                <div key={index} className="platform-item">
                  <a href={platform.flatform_path} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="platform-name">
                    {platform.platformName}
                  </a>
                  <span className='platform-discount'>
                    {platform.discountRate}%
                  </span>
                  <span className="platform-price">
                    {platform.price?.toLocaleString() ?? '가격 정보 없음'}원
                  </span>
                </div>
              ))}
            </div>
          )}
          </div>
        </div>
      </div>

      {/* 리뷰 상세 섹션 */}
      <div className="review-details-container" ref={reviewDetailsRef}>
        <div className="keyword-analysis-section">
          <div className="keyword-analysis-header">
            <h2 className="keyword-analysis-title">
              리뷰 키워드 분석
              <span className="keyword-analysis-badge">AI 분석</span>
            </h2>
            <p className="keyword-analysis-description">
              <span className="highlight-text">{productData.products[0].review_count}개의 실제 구매 리뷰</span>를 
              AI가 분석했어요. 각 항목을 클릭하면 생생한 구매 후기를 확인할 수 있습니다.
            </p>
          </div>
          <div className="keyword-analysis-tips">
            <div className="tip-content">
              <span className="tip-icon">💡</span>
              <div className="tip-text">
                <strong>클릭하여 상세 리뷰 확인하기</strong>
                <p>상품의 전체 리뷰와 키워드별 분석을 확인할 수 있어요.</p>
              </div>
            </div>
          </div>
          
        </div>

{/* 리뷰 탭 */}
<div className="review-tabs">
  <button
    className={`review-tab-button ${tabId === 'all' ? 'active' : ''}`}
    onClick={() => setTabId('all')}
  >
    전체 리뷰 보기
  </button>
  <button
    className={`review-tab-button ${tabId === 0 ? 'active' : ''}`}
    onClick={() => setTabId(0)}
  >
    사이즈
  </button>
  <button
    className={`review-tab-button ${tabId === 1 ? 'active' : ''}`}
    onClick={() => setTabId(1)}
  >
    디자인
  </button>
  <button
    className={`review-tab-button ${tabId === 2 ? 'active' : ''}`}
    onClick={() => setTabId(2)}
  >
    품질
  </button>
  <button
    className={`review-tab-button ${tabId === 3 ? 'active' : ''}`}
    onClick={() => setTabId(3)}
  >
    기능성/편의성
  </button>
  <button
    className={`review-tab-button ${tabId === 4 ? 'active' : ''}`}
    onClick={() => setTabId(4)}
  >
    가격
  </button>
</div>

{/* 리뷰 필터 */}
<div className="review-filters">
  <button
    className={`review-filter-button ${filterId === 0 ? 'active' : ''}`}
    onClick={() => setFilterId(0)}
  >
    전체
  </button>
  <button
    className={`review-filter-button ${filterId === 1 ? 'active' : ''}`}
    onClick={() => setFilterId(1)}
  >
    긍정리뷰 보기
  </button>
  <button
    className={`review-filter-button ${filterId === 2 ? 'active' : ''}`}
    onClick={() => setFilterId(2)}
  >
    부정리뷰 보기
  </button>
</div>


      {/* 키워드별 만족도 분석 */}
      {renderKeywordAnalysis()} 
      
      {/* 필터링된 리뷰 리스트 */}
      <div className="review-list">
        {filteredReviews.length > 0 ? (
          filteredReviews.map((review) => (
            <div key={review.reviews_id} className="review-item">
              <div>
                <strong>{review.platform_name}</strong>
              </div>
              <p>{review.sentence}</p>
            </div>
          ))
        ) : (
          <div>해당 조건에 맞는 리뷰가 없습니다.</div>
        )}
      </div>
        </div>
    </>
  );
};


export default ProductDetail;