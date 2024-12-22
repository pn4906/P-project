const mysql = require('mysql');

// 데이터베이스 연결 설정
const pool = mysql.createPool({
    host: 'localhost',       // 데이터베이스 서버 주소 (로컬)
    user: 'dbid233',         // 데이터베이스 사용자 이름
    password: 'dbpass233',   // 데이터베이스 비밀번호
    database: 'db24329',     // 사용할 데이터베이스 이름
    waitForConnections: true, // 연결 대기 활성화
    connectionLimit: 10,      // 최대 연결 수
    queueLimit: 0,            // 대기열 제한 (0은 무제한)
    multipleStatements: true  // 여러 쿼리 실행 허용
});

// 데이터베이스 연결 테스트
pool.getConnection((err, connection) => {
    if (err) {
        console.error('❌ Database connection failed:', err.message);
    } else {
        console.log('✅ Database connected successfully!');
        connection.release(); // 연결 해제
    }
});

module.exports = pool;