# NBA数据平台 - 停止服务器

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NBA数据平台 - 停止服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($portCheck) {
    Write-Host "发现服务器进程，正在关闭..." -ForegroundColor Yellow
    
    $portCheck | ForEach-Object {
        Write-Host "  关闭进程: $($_.OwningProcess)" -ForegroundColor Gray
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host ""
    Write-Host "服务器已成功关闭" -ForegroundColor Green
} else {
    Write-Host "未发现运行中的服务器" -ForegroundColor Yellow
}

Write-Host ""
