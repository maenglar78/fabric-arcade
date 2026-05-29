# Phase A: Create Cathedral infrastructure in Fabric Arcade Test workspace
# Run from FabricArcade root: pwsh -File .\dev\cathedral\setup_infra.ps1

$ErrorActionPreference = "Stop"
$WS = "a5235927-0289-4a06-83d1-456be383b496"
$FABRIC = "https://api.fabric.microsoft.com/v1"

function Get-Token {
    return (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
}

function Get-Headers {
    @{ Authorization = "Bearer $(Get-Token)"; "Content-Type" = "application/json" }
}

function Wait-Operation {
    param([string]$LocationUrl)
    $H = Get-Headers
    $deadline = (Get-Date).AddMinutes(5)
    while ((Get-Date) -lt $deadline) {
        $op = Invoke-RestMethod -Uri $LocationUrl -Headers $H
        if ($op.status -eq "Succeeded") {
            # Try to get result
            try {
                $res = Invoke-RestMethod -Uri ($LocationUrl + "/result") -Headers $H
                return $res
            } catch { return $op }
        }
        if ($op.status -eq "Failed") { throw "Operation failed: $($op | ConvertTo-Json -Depth 5)" }
        Start-Sleep -Seconds 3
    }
    throw "Operation timed out"
}

function New-FabricItem {
    param([string]$DisplayName, [string]$Type, [hashtable]$CreationPayload = $null, [string]$Description = "")
    $H = Get-Headers
    $payload = @{ displayName = $DisplayName; type = $Type }
    if ($Description) { $payload.description = $Description }
    if ($CreationPayload) { $payload.creationPayload = $CreationPayload }
    $body = $payload | ConvertTo-Json -Depth 10
    Write-Host "Creating $Type '$DisplayName'..." -ForegroundColor Cyan
    $r = Invoke-WebRequest -Method POST -Uri "$FABRIC/workspaces/$WS/items" -Headers $H -Body $body -SkipHttpErrorCheck
    if ($r.StatusCode -eq 201) {
        $obj = $r.Content | ConvertFrom-Json
        Write-Host "  Created id=$($obj.id)" -ForegroundColor Green
        return $obj
    } elseif ($r.StatusCode -eq 202) {
        $loc = $r.Headers.Location
        Write-Host "  Long-running op: $loc" -ForegroundColor Yellow
        $res = Wait-Operation -LocationUrl $loc
        Write-Host "  Done id=$($res.id)" -ForegroundColor Green
        return $res
    } else {
        throw "HTTP $($r.StatusCode): $($r.Content)"
    }
}

function Find-Item {
    param([string]$DisplayName, [string]$Type)
    $H = Get-Headers
    $r = Invoke-RestMethod -Uri "$FABRIC/workspaces/$WS/items?type=$Type" -Headers $H
    return $r.value | Where-Object { $_.displayName -eq $DisplayName } | Select-Object -First 1
}

# === 1. Lakehouse (no schemas — keeps it simple, avoids spark.sql default-context issues) ===
$lh = Find-Item -DisplayName "Cathedral_LH" -Type "Lakehouse"
if (-not $lh) {
    $lh = New-FabricItem -DisplayName "Cathedral_LH" -Type "Lakehouse" `
        -Description "Calc Groups Cathedral - Sales/Date/Customer/Budget"
} else {
    Write-Host "Lakehouse Cathedral_LH exists: $($lh.id)" -ForegroundColor Green
}

# === 2. Eventhouse ===
$eh = Find-Item -DisplayName "Cathedral_EH" -Type "Eventhouse"
if (-not $eh) {
    $eh = New-FabricItem -DisplayName "Cathedral_EH" -Type "Eventhouse" -Description "Calc Groups Cathedral - telemetry"
} else {
    Write-Host "Eventhouse Cathedral_EH exists: $($eh.id)" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Magenta
Write-Host "Lakehouse  Cathedral_LH = $($lh.id)"
Write-Host "Eventhouse Cathedral_EH = $($eh.id)"

# Save IDs for next steps
$ids = @{
    workspace = $WS
    lakehouse = $lh.id
    eventhouse = $eh.id
} | ConvertTo-Json
$ids | Out-File -FilePath "$PSScriptRoot\infra_ids.json" -Encoding utf8
Write-Host "IDs saved to $PSScriptRoot\infra_ids.json"
