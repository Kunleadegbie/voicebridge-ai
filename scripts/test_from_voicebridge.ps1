param(
    [Parameter(Mandatory=$true)][string]$BaseUrl,
    [Parameter(Mandatory=$true)][string]$ApiKey
)

$uri = $BaseUrl.TrimEnd("/") + "/v1/chat/completions"
$headers = @{
    Authorization = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}
$body = @{
    model = "NCAIR1/N-ATLaS"
    messages = @(
        @{
            role = "system"
            content = "You are VoiceBridge, a concise financial-literacy assistant for everyday Nigerians."
        },
        @{
            role = "user"
            content = "What does collateral mean? Answer briefly in Nigerian English."
        }
    )
    temperature = 0.1
    max_tokens = 180
} | ConvertTo-Json -Depth 10

$result = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $body
Write-Host "MODEL:" $result.model -ForegroundColor Green
Write-Host "RESPONSE:" -ForegroundColor Cyan
Write-Host $result.choices[0].message.content
