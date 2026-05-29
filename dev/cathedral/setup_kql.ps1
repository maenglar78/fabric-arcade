# Create KQL table CathedralEvents
$cluster = "https://trd-z9b3f5xvzm87f8c2kd.z6.kusto.fabric.microsoft.com"
$dbName = "Cathedral_EH"
$kustoTok = az account get-access-token --resource https://kusto.kusto.windows.net --query accessToken -o tsv
$H = @{ Authorization = "Bearer $kustoTok"; "Content-Type" = "application/json" }

function Invoke-Kql {
    param([string]$Csl)
    $body = @{ db = $dbName; csl = $Csl } | ConvertTo-Json
    return Invoke-RestMethod -Method POST -Uri "$cluster/v1/rest/mgmt" -Headers $H -Body $body
}

$createTable = @'
.create-merge table CathedralEvents (
    EventId: guid, Timestamp: datetime, SessionId: string, PlayerId: string,
    EventType: string, PillarId: int, PillarKey: string,
    SubmittedValue: real, ExpectedValue: real, PassFail: string,
    MeasureCount: int, CalcGroupCount: int, EleganceScore: real,
    Rank: string, DurationSeconds: real
)
'@

Write-Host "1) Creating table..." -ForegroundColor Cyan
$r = Invoke-Kql -Csl $createTable
Write-Host "   OK rows=$($r.Tables[0].Rows.Count)" -ForegroundColor Green

Write-Host "2) Retention 90d..." -ForegroundColor Cyan
Invoke-Kql -Csl '.alter-merge table CathedralEvents policy retention softdelete = 90d' | Out-Null
Write-Host "   OK" -ForegroundColor Green

Write-Host "3) Streaming ingestion..." -ForegroundColor Cyan
try { Invoke-Kql -Csl '.alter table CathedralEvents policy streamingingestion enable' | Out-Null; Write-Host "   OK" -ForegroundColor Green }
catch { Write-Host "   WARN: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "4) Verify..." -ForegroundColor Cyan
$v = Invoke-Kql -Csl '.show table CathedralEvents | project TableName, DatabaseName'
$v.Tables[0].Rows | ForEach-Object { Write-Host "   $($_ -join ' | ')" -ForegroundColor Green }
