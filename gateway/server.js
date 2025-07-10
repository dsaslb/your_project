const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const morgan = require('morgan');
const Redis = require('ioredis');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 8000;

// Redis 클라이언트
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// 미들웨어 설정
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 로깅
app.use(morgan('combined'));

// Rate Limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 100, // IP당 최대 요청 수
  message: {
    error: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

// JWT 인증 미들웨어
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    // Redis에서 토큰 검증
    const isValid = await redis.get(`token:${token}`);
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid or expired token' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// 권한 검증 미들웨어
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// 헬스체크 엔드포인트
app.get('/health', async (req, res) => {
  try {
    // Redis 연결 확인
    await redis.ping();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        gateway: 'running',
        redis: 'connected'
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// 메트릭 엔드포인트
app.get('/metrics', (req, res) => {
  res.json({
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    cpu: process.cpuUsage()
  });
});

// API 라우팅
const backendProxy = createProxyMiddleware({
  target: process.env.API_BACKEND_URL || 'http://backend:5001',
  changeOrigin: true,
  pathRewrite: {
    '^/api/backend': '/api'
  },
  onProxyReq: (proxyReq, req, res) => {
    // 요청 로깅
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path} -> Backend`);
  },
  onProxyRes: (proxyRes, req, res) => {
    // 응답 로깅
    console.log(`${new Date().toISOString()} - Backend responded with ${proxyRes.statusCode}`);
  }
});

const aiProxy = createProxyMiddleware({
  target: process.env.API_AI_URL || 'http://ai-server:8002',
  changeOrigin: true,
  pathRewrite: {
    '^/api/ai': ''
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path} -> AI Server`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`${new Date().toISOString()} - AI Server responded with ${proxyRes.statusCode}`);
  }
});

// 백엔드 API 라우팅
app.use('/api/backend', authenticateToken, backendProxy);

// AI 서버 라우팅
app.use('/api/ai', authenticateToken, aiProxy);

// WebSocket 프록시 (실시간 기능)
app.use('/ws', (req, res) => {
  // WebSocket 연결을 백엔드로 프록시
  const target = process.env.API_BACKEND_URL || 'http://backend:5001';
  res.redirect(target + req.url);
});

// 캐시 미들웨어
const cache = (duration) => {
  return async (req, res, next) => {
    const key = `cache:${req.originalUrl}`;
    
    try {
      const cached = await redis.get(key);
      if (cached) {
        return res.json(JSON.parse(cached));
      }
      
      res.sendResponse = res.json;
      res.json = (body) => {
        redis.setex(key, duration, JSON.stringify(body));
        res.sendResponse(body);
      };
      
      next();
    } catch (error) {
      next();
    }
  };
};

// 캐시 적용 예시
app.get('/api/cached-data', cache(300), (req, res) => {
  // 5분간 캐시되는 데이터
  res.json({ data: 'cached response' });
});

// 에러 핸들링 미들웨어
app.use((err, req, res, next) => {
  console.error('Gateway Error:', err);
  
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal Server Error',
      timestamp: new Date().toISOString(),
      path: req.path
    }
  });
});

// 404 핸들러
app.use('*', (req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found',
      path: req.originalUrl,
      timestamp: new Date().toISOString()
    }
  });
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Backend URL: ${process.env.API_BACKEND_URL || 'http://backend:5001'}`);
  console.log(`AI Server URL: ${process.env.API_AI_URL || 'http://ai-server:8002'}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await redis.quit();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  await redis.quit();
  process.exit(0);
});

module.exports = app; 