import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import FashionRankingTable from './pages/productsRanking';
import ProductDetail from './pages/productDetail';
import './styles/App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMenu, setSelectedMenu] = useState('best');

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleMenuChange = (category) => {
    setSelectedMenu(category);
    setSearchTerm('');
  };

  return (
    <Router>
      <Navbar 
        setSelectedMenu={handleMenuChange} 
        selectedMenu={selectedMenu}
        onSearch={handleSearch}
      />
      <Routes>
        <Route path="/" element={<FashionRankingTable searchTerm={searchTerm} selectedMenu={selectedMenu} />} />
        <Route path="/products/:product_id" element={<ProductDetail />} />
      </Routes>
    </Router>
  );
}

export default App;