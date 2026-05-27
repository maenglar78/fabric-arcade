$token = (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
$headers = @{ "Authorization" = "Bearer $token" }
$lro = Invoke-RestMethod -Uri "https://wabi-west-us3-a-primary-redirect.analysis.windows.net/v1/operations/1653c241-b3e1-472b-b97c-5cc1d3df4776" -Headers $headers
Write-Host "Status:" $lro.status
$lro | ConvertTo-Json
