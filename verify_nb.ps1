$token = (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }
$response = Invoke-WebRequest -Uri "https://api.fabric.microsoft.com/v1/workspaces/a5235927-0289-4a06-83d1-456be383b496/notebooks/27407ece-4b0a-4ba8-b00b-ad08ca9507c6/getDefinition?format=ipynb" -Method POST -Headers $headers -Body "{}"
Write-Host "Status:" $response.StatusCode
$location = $response.Headers["Location"]
Write-Host "Location:" $location

# Wait and poll
Start-Sleep -Seconds 3
$result = Invoke-RestMethod -Uri $location -Headers @{ "Authorization" = "Bearer $token" }
Write-Host "LRO Status:" $result.status

if ($result.status -eq "Succeeded") {
    $final = Invoke-RestMethod -Uri "$location/result" -Headers @{ "Authorization" = "Bearer $token" }
    $final | ConvertTo-Json -Depth 5 | Out-File "_def_result.json"
    Write-Host "Definition saved to _def_result.json"
    Write-Host "Parts:" $final.definition.parts.Count
    if ($final.definition.parts.Count -gt 0) {
        Write-Host "Part path:" $final.definition.parts[0].path
        Write-Host "Payload length:" $final.definition.parts[0].payload.Length
    }
}
