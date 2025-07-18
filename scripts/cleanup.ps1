# PowerShell용 임시 클린업 스크립트
Remove-Item -Recurse -Force ../cache/* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ../logs/* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ../frontend/.next/* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ../frontend/coverage/* -ErrorAction SilentlyContinue
Write-Host "임시 파일, 캐시, 로그 정리 완료" 