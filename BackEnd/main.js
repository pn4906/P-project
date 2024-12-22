const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors');

// 라우터 불러오기
const rankingRouter = require('./Routes/rankingRouter');
const productRouter = require('./Routes/ProductDetailRouter');
const searchRouter = require('./Routes/searchRouter');

const app = express(); // app 초기화
const port = 60029;

// Middleware 설정
app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// API 요청 라우터 연결 (모든 API 요청은 /api 경로 사용)
app.use('/api/ranking', rankingRouter);
app.use('/api/products', productRouter);
app.use('/api/search', searchRouter);

// 정적 파일 제공 (React 빌드 파일)
app.use(express.static(path.join(__dirname, 'fashion-ranking-build')));

// React SPA 처리 (정적 파일 제외한 모든 요청을 index.html로 리다이렉트)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'fashion-ranking-build', 'index.html'));
});

// 서버 실행
app.listen(port, () => {
    console.log(`Server running at http://ceprj.gachon.ac.kr:${port}`);
});