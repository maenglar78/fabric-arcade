$token = (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }

# Request fresh getDefinition
$response = Invoke-WebRequest -Uri "https://api.fabric.microsoft.com/v1/workspaces/a5235927-0289-4a06-83d1-456be383b496/notebooks/27407ece-4b0a-4ba8-b00b-ad08ca9507c6/getDefinition?format=ipynb" -Method POST -Headers $headers -Body "{}"
$location = $response.Headers["Location"][0]
Write-Host "LRO URL:" $location

Start-Sleep -Seconds 3
$result = Invoke-RestMethod -Uri $location -Headers @{ "Authorization" = "Bearer $token" }
Write-Host "Status:" $result.status

if ($result.status -eq "Succeeded") {
    $final = Invoke-RestMethod -Uri "$location/result" -Headers @{ "Authorization" = "Bearer $token" }
    Write-Host "Parts:" $final.definition.parts.Count
    Write-Host "Payload length:" $final.definition.parts[0].payload.Length
    
    # Decode and check content
    $payload = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($final.definition.parts[0].payload))
    $nb = $payload | ConvertFrom-Json
    Write-Host "Cells:" $nb.cells.Count
    Write-Host "First cell preview:" $nb.cells[0].source[0].Substring(0, 60)
}
