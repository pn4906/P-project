import React, { useState } from 'react';
import { FaSearch } from 'react-icons/fa';
import { useNavigate, useSearchParams } from 'react-router-dom';

const SUBCATEGORIES = {
  '전체': 'all',
  '아우터': 'outer',
  '상의': 'top',
  '하의': 'bottom',
  '신발': 'shoes'
};

const Navbar = ({ setSelectedMenu, selectedMenu }) => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const categories = ['BEST', 'WOMEN', 'MEN'];
  const [showSearch, setShowSearch] = useState(false);
  const [selectedSubMenu, setSelectedSubMenu] = useState('전체');
  const [searchInput, setSearchInput] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearchClick = () => {
    if (!showSearch) {
      setShowSearch(true);
    } else {
      handleSearchSubmit();
    }
  };

  const handleSearchSubmit = async () => {
    const trimmedInput = searchInput.trim();
    if (trimmedInput === '') {
      setErrorMessage('공백은 입력이 불가합니다.');
      setTimeout(() => setErrorMessage(''), 3000);
      return;
    }
    if (/[\s!@#$%^&*()_+=-]+/.test(trimmedInput)) {
      setErrorMessage('특수문자는 입력이 불가합니다.');
      setTimeout(() => setErrorMessage(''), 3000);
      return;
    }
    if (trimmedInput.length < 2) {
      setErrorMessage('검색어는 최소 2글자 이상이어야 합니다.');
      setTimeout(() => setErrorMessage(''), 3000);
      return;
    }
    setErrorMessage('');
    setLoading(true);

    try {
      navigate(`/?keyword=${trimmedInput}`);
      setShowSearch(false);
      setSearchInput('');
    } catch (err) {
      console.error('Search Error:', err);
      setErrorMessage(`검색 중 오류가 발생했습니다: ${err.message}`);
      setTimeout(() => setErrorMessage(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setSearchInput(e.target.value);
  };

  const handleTitleClick = () => {
    navigate('/');
    setSelectedMenu('');
  };

  const handleMenuClick = (category) => {
    setSelectedMenu(category);
    setSelectedSubMenu('전체');
    setSearchInput('');
    setShowSearch(false);
    navigate(`/?category=${category.toLowerCase()}&subcategory=all`);
  };

  const handleSubCategoryClick = (subCategory) => {
    setSelectedSubMenu(subCategory);
    navigate(`/?category=${selectedMenu.toLowerCase()}&subcategory=${SUBCATEGORIES[subCategory]}`);
  };

  const subCategory = () => {
    if (!selectedMenu) return null;
    
    return (
      <nav className="Navbar">
        {['전체', '아우터', '상의', '하의', '신발'].map((item) => (
          <a
            key={item}
            href="#"
            style={{ fontWeight: selectedSubMenu === item ? 'bold' : 'normal' }}
            onClick={(e) => {
              e.preventDefault();
              handleSubCategoryClick(item);
            }}
          >
            {item}
          </a>
        ))}
      </nav>
    );
  };

  return (
    <header>
      {errorMessage && (
        <div className="popup">
          {errorMessage}
        </div>
      )}
      <div className="titleContainer">
        <h1 
          className="left-aligned-heading"
          onClick={handleTitleClick}
        >
          <span className="hover-text">청바지</span>
          <span className="hover-effect">청춘은 바로 지금</span>
        </h1>
      </div>
      <nav className="Navbar">
        <div className="menuContainer">
          {categories.map((category) => (
            <a
              key={category}
              href="#"
              style={{ fontWeight: selectedMenu === category ? 'bold' : 'normal' }}
              onClick={(e) => {
                e.preventDefault();
                handleMenuClick(category);
              }}
            >
              {category}
            </a>
          ))}
        </div>
        <div className="searchContainer">
          {showSearch && (
            <>
              <input
                type="text"
                placeholder="상품을 입력하세요"
                className="searchInput"
                value={searchInput}
                onChange={handleInputChange}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearchSubmit();
                  }
                }}
                autoFocus
                disabled={loading}
              />
            </>
          )}
          <FaSearch 
            className={`searchIcon ${loading ? 'loading' : ''}`} 
            onClick={!loading ? handleSearchClick : undefined} 
          />
        </div>
      </nav>
      {subCategory()}
    </header>
  );
};

export default Navbar;
