const express = require('express');
var session = require('express-session');
var MySqlStore = require('express-mysql-session')(session);
var bodyParser = require('body-parser');
const app = express();
const cors = require('cors');

// 포트 설정
const port = 60029;

app.use(express.static('public'));
app.use(cors()); // 모든 도메인의 요청 허용

// 라우터 불러오기
var rankingRouter = require('./Routes/rankingRouter');
var productRouter = require('./Routes/ProductDetailRouter');
var searchRouter = require('./Routes/searchRouter');  
// 세션 스토어 설정
var options = {
    host: 'localhost',
    user: 'dbid233',
    password: 'dbpass233',
    database: 'db24329',
};
var sessionStore = new MySqlStore(options);

app.use(session({
    secret: 'keyboard cat',
    resave: false,
    saveUninitialized: true,
    store: sessionStore
}));

// 뷰 엔진 설정
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json()); 

// 라우터 연결
app.use('/search', searchRouter);  // 검색 라우터를 먼저 등록
app.use('/', rankingRouter);       // 그 다음 기본 라우터
app.use('/products', productRouter);
// favicon 요청 무시
app.get('/favicon.ico', (req, res) => res.status(204).end());

// 서버 실행
app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});