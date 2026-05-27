$token = (az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)
$headers = @{ "Authorization" = "Bearer $token" }
Start-Sleep -Seconds 2
$result = Invoke-RestMethod -Uri "https://wabi-west-us3-a-primary-redirect.analysis.windows.net/v1/operations/3420a30b-906c-442d-a4a7-10b715abe2cd" -Headers $headers
Write-Host "Status:" $result.status
if ($result.status -eq "Succeeded") {
    $final = Invoke-RestMethod -Uri "https://wabi-west-us3-a-primary-redirect.analysis.windows.net/v1/operations/3420a30b-906c-442d-a4a7-10b715abe2cd/result" -Headers $headers
    Write-Host "Parts:" $final.definition.parts.Count
    if ($final.definition.parts.Count -gt 0) {
        Write-Host "Part path:" $final.definition.parts[0].path
        Write-Host "Payload length:" $final.definition.parts[0].payload.Length
    }
}
