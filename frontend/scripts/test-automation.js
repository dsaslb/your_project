#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 색상 코드
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

// 로그 함수
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 성능 측정 함수
function measurePerformance(fn, name) {
  const start = process.hrtime.bigint();
  const result = fn();
  const end = process.hrtime.bigint();
  const duration = Number(end - start) / 1000000; // ms로 변환
  
  log(`⏱️  ${name}: ${duration.toFixed(2)}ms`, duration < 1000 ? 'green' : 'yellow');
  return { result, duration };
}

// 테스트 실행 함수
function runTests(testType = 'unit') {
  log(`\n🚀 ${testType.toUpperCase()} 테스트 실행 중...`, 'blue');
  
  try {
    const command = testType === 'unit' ? 'npm run test:unit' : 'npm run test:e2e';
    const output = execSync(command, { 
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 300000 // 5분 타임아웃
    });
    
    log(`✅ ${testType} 테스트 완료`, 'green');
    return { success: true, output };
  } catch (error) {
    log(`❌ ${testType} 테스트 실패`, 'red');
    log(error.stdout || error.message, 'red');
    return { success: false, error: error.stdout || error.message };
  }
}

// 코드 커버리지 분석
function analyzeCoverage() {
  log('\n📊 코드 커버리지 분석 중...', 'blue');
  
  try {
    const coverageCommand = 'npm run test:unit -- --coverage --watchAll=false';
    const output = execSync(coverageCommand, { 
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 300000
    });
    
    // 커버리지 결과 파싱
    const coverageMatch = output.match(/All files\s+\|\s+(\d+\.?\d*)\s+\|\s+(\d+\.?\d*)\s+\|\s+(\d+\.?\d*)\s+\|\s+(\d+\.?\d*)/);
    
    if (coverageMatch) {
      const [, statements, branches, functions, lines] = coverageMatch;
      log(`📈 커버리지 결과:`, 'cyan');
      log(`   Statements: ${statements}%`, statements >= 80 ? 'green' : 'yellow');
      log(`   Branches: ${branches}%`, branches >= 80 ? 'green' : 'yellow');
      log(`   Functions: ${functions}%`, functions >= 80 ? 'green' : 'yellow');
      log(`   Lines: ${lines}%`, lines >= 80 ? 'green' : 'yellow');
      
      return {
        success: true,
        coverage: { statements, branches, functions, lines }
      };
    }
    
    return { success: false, error: '커버리지 결과를 파싱할 수 없습니다.' };
  } catch (error) {
    log(`❌ 커버리지 분석 실패`, 'red');
    return { success: false, error: error.message };
  }
}

// 성능 테스트 실행
function runPerformanceTests() {
  log('\n⚡ 성능 테스트 실행 중...', 'blue');
  
  try {
    // 빌드 성능 테스트
    const buildStart = process.hrtime.bigint();
    execSync('npm run build', { stdio: 'pipe', timeout: 300000 });
    const buildEnd = process.hrtime.bigint();
    const buildTime = Number(buildEnd - buildStart) / 1000000;
    
    log(`🏗️  빌드 시간: ${buildTime.toFixed(2)}ms`, buildTime < 60000 ? 'green' : 'yellow');
    
    // 번들 크기 분석
    const bundleAnalyzer = 'npm run analyze';
    try {
      execSync(bundleAnalyzer, { stdio: 'pipe', timeout: 60000 });
      log('📦 번들 분석 완료', 'green');
    } catch (error) {
      log('⚠️  번들 분석 실패 (선택사항)', 'yellow');
    }
    
    return { success: true, buildTime };
  } catch (error) {
    log(`❌ 성능 테스트 실패`, 'red');
    return { success: false, error: error.message };
  }
}

// 보안 검사
function runSecurityChecks() {
  log('\n🔒 보안 검사 실행 중...', 'blue');
  
  try {
    // npm audit 실행
    const auditOutput = execSync('npm audit --audit-level=moderate', { 
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 60000
    });
    
    const vulnerabilities = auditOutput.match(/(\d+) vulnerabilities found/);
    if (vulnerabilities) {
      const count = parseInt(vulnerabilities[1]);
      if (count === 0) {
        log('✅ 보안 취약점 없음', 'green');
      } else {
        log(`⚠️  ${count}개의 보안 취약점 발견`, 'yellow');
        log(auditOutput, 'yellow');
      }
    }
    
    return { success: true };
  } catch (error) {
    log(`❌ 보안 검사 실패`, 'red');
    return { success: false, error: error.message };
  }
}

// 테스트 리포트 생성
function generateTestReport(results) {
  log('\n📋 테스트 리포트 생성 중...', 'blue');
  
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      coverage: null,
      performance: null,
      security: null,
    },
    details: results,
  };
  
  // 결과 집계
  Object.values(results).forEach(result => {
    if (result.success) {
      report.summary.passedTests++;
    } else {
      report.summary.failedTests++;
    }
    report.summary.totalTests++;
  });
  
  // 리포트 파일 저장
  const reportPath = path.join(__dirname, '../test-reports', `test-report-${Date.now()}.json`);
  const reportDir = path.dirname(reportPath);
  
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }
  
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  log(`📄 리포트 저장됨: ${reportPath}`, 'green');
  
  return report;
}

// 메인 실행 함수
async function main() {
  log('🧪 테스트 자동화 시스템 시작', 'bright');
  
  const results = {};
  
  // 1. 단위 테스트
  results.unitTests = measurePerformance(
    () => runTests('unit'),
    '단위 테스트'
  );
  
  // 2. E2E 테스트 (선택사항)
  if (process.argv.includes('--e2e')) {
    results.e2eTests = measurePerformance(
      () => runTests('e2e'),
      'E2E 테스트'
    );
  }
  
  // 3. 커버리지 분석
  results.coverage = measurePerformance(
    analyzeCoverage,
    '커버리지 분석'
  );
  
  // 4. 성능 테스트
  results.performance = measurePerformance(
    runPerformanceTests,
    '성능 테스트'
  );
  
  // 5. 보안 검사
  results.security = measurePerformance(
    runSecurityChecks,
    '보안 검사'
  );
  
  // 6. 리포트 생성
  const report = generateTestReport(results);
  
  // 7. 최종 결과 출력
  log('\n🎯 테스트 자동화 완료', 'bright');
  log(`총 테스트: ${report.summary.totalTests}`, 'cyan');
  log(`성공: ${report.summary.passedTests}`, 'green');
  log(`실패: ${report.summary.failedTests}`, report.summary.failedTests === 0 ? 'green' : 'red');
  
  if (report.summary.failedTests > 0) {
    log('\n❌ 일부 테스트가 실패했습니다.', 'red');
    process.exit(1);
  } else {
    log('\n✅ 모든 테스트가 성공했습니다!', 'green');
  }
}

// 스크립트 실행
if (require.main === module) {
  main().catch(error => {
    log(`\n💥 테스트 자동화 실패: ${error.message}`, 'red');
    process.exit(1);
  });
}

module.exports = {
  runTests,
  analyzeCoverage,
  runPerformanceTests,
  runSecurityChecks,
  generateTestReport,
}; 