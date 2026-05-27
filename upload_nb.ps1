$token = (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
$headers = @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" }
$body = Get-Content ".\_nb_def3.json" -Raw
$response = Invoke-WebRequest -Uri "https://api.fabric.microsoft.com/v1/workspaces/a5235927-0289-4a06-83d1-456be383b496/notebooks/27407ece-4b0a-4ba8-b00b-ad08ca9507c6/updateDefinition" -Method POST -Headers $headers -Body $body
Write-Host "Status:" $response.StatusCode
$response.Headers | ConvertTo-Json | Out-File "_response.json"
Write-Host "Headers saved to _response.json"
