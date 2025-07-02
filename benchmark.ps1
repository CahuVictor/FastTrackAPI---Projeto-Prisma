# benchmark.ps1
# Script PowerShell para testar latência da API FastTrackAPI

Write-Host "Fazendo login..."

$body = @{ username = "alice"; password = "secret123" }
$response = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method Post -Body $body
$token = $response.access_token

if (-not $token) {
    Write-Host "Erro ao obter token de autenticação."
    exit 1
}

Write-Host "Login bem-sucedido. Token obtido."

$headers = @{ Authorization = "Bearer $token" }

Write-Host "Enviando requisicao autenticada para /api/v1/eventos..."

$start = Get-Date
$response = Invoke-WebRequest -Uri http://localhost:8000/api/v1/eventos -Headers $headers
$end = Get-Date
$duration = $end - $start

Write-Host ""
Write-Host "Resultado:"
Write-Host "Status Code: $($response.StatusCode)"
Write-Host "Tempo total: $($duration.TotalMilliseconds) ms"
Write-Host "Conluido"
# Concluído