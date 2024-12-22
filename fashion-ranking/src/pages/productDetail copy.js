import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/productDetail.css';

// ===== 상수 정의 =====
// 리뷰 탭 설정
const REVIEW_TABS = [
  { id: 'all', label: '전체 리뷰 보기', keywordId: '5' },
  { id: 'size', label: '사이즈', keywordId: '0' },
  { id: 'design', label: '디자인', keywordId: '1' },
  { id: 'quality', label: '품질', keywordId: '2' },
  { id: 'functionality', label: '기능성/편의성', keywordId: '3' },
  { id: 'price', label: '가격', keywordId: '4' }
];

// 리뷰 필터 설정
const REVIEW_FILTERS = [
  { id: 'all', label: '전체', positiveId: '0' },
  { id: 'positive', label: '긍정리뷰 보기', positiveId: '1' },
  { id: 'negative', label: '부정리뷰 보기', positiveId: '2' }
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
  const navigate = useNavigate();
  const reviewDetailsRef = useRef(null);
  
  // 상태 관리
  const [productData, setProductData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState(null);
  const [isPriceListOpen, setIsPriceListOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [activeFilter, setActiveFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

   // 리뷰 API 요청 함수
   const fetchReviews = async (tabId, filterId) => {
    try {
      setLoading(true);
      const selectedTab = REVIEW_TABS.find(tab => tab.id === tabId);
      const selectedFilter = REVIEW_FILTERS.find(filter => filter.id === filterId);
      console.log(selectedTab.keywordId, selectedFilter.positiveId)


      const url = `${process.env.REACT_APP_API_URL}products/${product_id}?keywords=${selectedTab.keywordId}&positive=${selectedFilter.positiveId}`;
      console.log('Fetching reviews from:', url);

      const response = await fetch(url);
      if (!response.ok) throw new Error('리뷰 데이터를 불러오는데 실패했습니다.');

      const data = await response.json();
      setProductData(data);
      setReviews(data.cor_reviews || []);
      setLoading(false);
    } catch (err) {
      console.error(err.message);
      setError('리뷰 데이터를 불러오는 중 오류가 발생했습니다.');
      setLoading(false);
    }
  };

  // 리뷰 렌더링 함수 수정
  const renderReviews = () => {
      return (
        <div className="review-list">
          {productData.cor_reviews?.map((cor_reviews, index) => (
            <div key={index} className="review-item">
              <div className="review-header">
                <span className="review-platform">{cor_reviews.platform_name}</span>
              </div>
              <div className="review-content">
                <p className="review-text">{cor_reviews.sentence}</p>
              </div>
            </div>
          ))}
        </div>
      );
    return null;
  };

  // 키워드별 만족도 분석 렌더링 함수
  const renderKeywordAnalysis = () => {
    if (activeTab !== 'all') {
      const selectedTab = REVIEW_TABS.find(tab => tab.id === activeTab); // { id: 'design', label: '디자인', keywordId: '1' },
      const positiveRate = productData.positive_rate[parseInt(selectedTab.keywordId)]; // 긍정 비율 
      
      return (
        <div className="keyword-rating-details">
          <RatingDetail 
            title={<>{selectedTab.label} 만족도 <span className="ai-analysis-badge">AI 분석</span></>}
            positiveRate={parseInt(positiveRate)}
            reviewCount={productData.products[0].review_count}
            description={`이 제품의 ${selectedTab.label}에 대해 ${positiveRate}%의 구매자가 만족했어요. 관련 리뷰를 함께 확인해보세요.`}
          />
        </div>
      );
    }
    return null;
  };

  // ================ 리뷰 ======================
    // 탭 변경 시 리뷰 새로 가져오기
    const handleTabChange = (tabId) => {
      setActiveTab(tabId);
      setActiveFilter('all'); // 필터를 초기화
      fetchReviews(tabId, 'all'); // 리뷰 요청
    };
  
    // 필터 변경 시 리뷰 새로 가져오기
    const handleFilterChange = (filterId) => {
      setActiveFilter(filterId);
      fetchReviews(activeTab, filterId); // 현재 탭과 선택된 필터로 리뷰 요청
    };


  
  
  // 초기 데이터 로딩
    useEffect(() => {
      fetchReviews('all', 'all'); // 초기에는 전체 리뷰를 불러옴
    }, [product_id]);

  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>{error}</div>;
  if (!productData) return <div>상품을 찾을 수 없습니다.</div>;



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
        {REVIEW_TABS.map(tab => (
          <button
            key={tab.id}
            className={`review-tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 리뷰 필터 */}
      <div className="review-filters">
        {REVIEW_FILTERS.map(filter => (
          <button
            key={filter.id}
            className={`review-filter-button ${activeFilter === filter.id ? 'active' : ''}`}
            onClick={() => handleFilterChange(filter.id)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* 키워드별 만족도 분석 */}
      {renderKeywordAnalysis()} 
      
      {/* 리뷰 목록 */}
      <div className="review-list">
        {reviews.length > 0 ? (
          reviews.map(review => (
            <div key={review.reviews_id} className="review-item">
              <div>{review.platform_name}</div>
              <p>{review.sentence}</p>
            </div>
          ))
        ) : (
          <div>리뷰가 없습니다.</div>
        )}

        
      </div>
        </div>
    </>
  );
};


export default ProductDetail;