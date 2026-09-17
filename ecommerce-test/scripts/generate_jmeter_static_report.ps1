param(
    [Parameter(Mandatory = $true)]
    [string]$JtlPath,

    [Parameter(Mandatory = $true)]
    [string]$ReportDir,

    [string]$BuildNumber = "local",
    [int]$Threads = 0,
    [int]$RampUp = 0,
    [int]$Loops = 0,
    [double]$MaxErrorRate = 0,
    [int]$MaxP95Ms = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Percentile {
    param(
        [Parameter(Mandatory = $true)]
        [int[]]$Values,
        [Parameter(Mandatory = $true)]
        [double]$Percentile
    )

    if ($Values.Count -eq 0) {
        return 0
    }

    $sorted = @($Values | Sort-Object)
    $index = [math]::Ceiling($sorted.Count * $Percentile) - 1
    if ($index -lt 0) {
        $index = 0
    }
    if ($index -ge $sorted.Count) {
        $index = $sorted.Count - 1
    }

    return [int]$sorted[$index]
}

function HtmlEncode {
    param([AllowNull()][object]$Value)

    return [System.Net.WebUtility]::HtmlEncode([string]$Value)
}

if (-not (Test-Path -LiteralPath $JtlPath -PathType Leaf)) {
    throw "JTL 文件不存在: $JtlPath"
}
if (-not (Test-Path -LiteralPath $ReportDir -PathType Container)) {
    throw "JMeter 报告目录不存在: $ReportDir"
}

$rows = @(Import-Csv -LiteralPath $JtlPath)
if ($rows.Count -eq 0) {
    throw "JTL 文件没有测试样本: $JtlPath"
}

$elapsedValues = @($rows | ForEach-Object { [int]$_.elapsed })
$failedRows = @($rows | Where-Object { "$($_.success)".ToLowerInvariant() -ne "true" })
$total = $rows.Count
$failed = $failedRows.Count
$success = $total - $failed
$errorRate = [math]::Round(($failed / $total) * 100, 2)
$average = [math]::Round(($elapsedValues | Measure-Object -Average).Average, 2)
$minimum = ($elapsedValues | Measure-Object -Minimum).Minimum
$maximum = ($elapsedValues | Measure-Object -Maximum).Maximum
$p50 = Get-Percentile -Values $elapsedValues -Percentile 0.50
$p90 = Get-Percentile -Values $elapsedValues -Percentile 0.90
$p95 = Get-Percentile -Values $elapsedValues -Percentile 0.95
$p99 = Get-Percentile -Values $elapsedValues -Percentile 0.99

$startTimestamp = ($rows | ForEach-Object { [int64]$_.timeStamp } | Measure-Object -Minimum).Minimum
$endTimestamp = ($rows | ForEach-Object { [int64]$_.timeStamp + [int64]$_.elapsed } | Measure-Object -Maximum).Maximum
$durationSeconds = [math]::Max(($endTimestamp - $startTimestamp) / 1000.0, 0.001)
$throughput = [math]::Round($total / $durationSeconds, 2)

$errorGatePassed = $errorRate -le $MaxErrorRate
$p95GatePassed = $p95 -le $MaxP95Ms
$qualityGatePassed = $errorGatePassed -and $p95GatePassed
$qualityText = if ($qualityGatePassed) { "通过" } else { "未通过" }

# JMeter 原生 Dashboard 始终保留为 index.html，供 Jenkins HTML Publisher 直接发布。
# 另外生成 summary.html 作为不依赖 JavaScript 的备用报告，不覆盖原生入口。
$indexPath = Join-Path $ReportDir "index.html"
$summaryPath = Join-Path $ReportDir "summary.html"
if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
    throw "JMeter 原生 Dashboard 不存在: $indexPath"
}
Copy-Item -LiteralPath $JtlPath -Destination (Join-Path $ReportDir "raw-results.jtl") -Force

$labelRows = New-Object System.Text.StringBuilder
foreach ($group in ($rows | Group-Object -Property label | Sort-Object Name)) {
    $groupRows = @($group.Group)
    $groupElapsed = @($groupRows | ForEach-Object { [int]$_.elapsed })
    $groupFailed = @($groupRows | Where-Object { "$($_.success)".ToLowerInvariant() -ne "true" }).Count
    $groupErrorRate = [math]::Round(($groupFailed / $groupRows.Count) * 100, 2)
    $groupAverage = [math]::Round(($groupElapsed | Measure-Object -Average).Average, 2)
    $groupMin = ($groupElapsed | Measure-Object -Minimum).Minimum
    $groupMax = ($groupElapsed | Measure-Object -Maximum).Maximum
    $groupP95 = Get-Percentile -Values $groupElapsed -Percentile 0.95

    [void]$labelRows.AppendLine(@"
<tr>
  <td>$(HtmlEncode $group.Name)</td>
  <td>$($groupRows.Count)</td>
  <td>$groupFailed</td>
  <td>$groupErrorRate%</td>
  <td>$groupAverage ms</td>
  <td>$groupMin ms</td>
  <td>$groupP95 ms</td>
  <td>$groupMax ms</td>
</tr>
"@)
}

$failedRowsHtml = New-Object System.Text.StringBuilder
if ($failed -eq 0) {
    [void]$failedRowsHtml.AppendLine('<p><strong>没有失败请求。</strong></p>')
} else {
    [void]$failedRowsHtml.AppendLine('<table border="1" cellspacing="0" cellpadding="6">')
    [void]$failedRowsHtml.AppendLine('<thead><tr><th>请求</th><th>响应码</th><th>错误信息</th><th>URL</th></tr></thead><tbody>')
    foreach ($row in ($failedRows | Select-Object -First 20)) {
        [void]$failedRowsHtml.AppendLine(@"
<tr>
  <td>$(HtmlEncode $row.label)</td>
  <td>$(HtmlEncode $row.responseCode)</td>
  <td>$(HtmlEncode $row.failureMessage)</td>
  <td>$(HtmlEncode $row.URL)</td>
</tr>
"@)
    }
    [void]$failedRowsHtml.AppendLine('</tbody></table>')
}

$generatedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$qualityColor = if ($qualityGatePassed) { "green" } else { "red" }
$html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JMeter 性能测试报告摘要</title>
</head>
<body>
  <h1>JMeter 性能测试报告摘要</h1>
  <p>这是专门为 Jenkins HTML Publisher 生成的静态摘要页，不依赖 JavaScript，因此不会被 Jenkins CSP 安全策略拦截。</p>

  <h2>构建信息</h2>
  <table border="1" cellspacing="0" cellpadding="6">
    <tbody>
      <tr><th>Jenkins 构建号</th><td>$(HtmlEncode $BuildNumber)</td></tr>
      <tr><th>报告生成时间</th><td>$(HtmlEncode $generatedAt)</td></tr>
      <tr><th>并发线程数</th><td>$Threads</td></tr>
      <tr><th>Ramp-Up</th><td>$RampUp 秒</td></tr>
      <tr><th>循环次数</th><td>$Loops</td></tr>
      <tr><th>测试持续时间</th><td>$([math]::Round($durationSeconds, 2)) 秒</td></tr>
    </tbody>
  </table>

  <h2>核心结果</h2>
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr><th>总样本</th><th>成功</th><th>失败</th><th>错误率</th><th>吞吐量</th><th>平均响应</th><th>P90</th><th>P95</th><th>P99</th><th>最大响应</th></tr>
    </thead>
    <tbody>
      <tr><td>$total</td><td>$success</td><td>$failed</td><td>$errorRate%</td><td>$throughput 次/秒</td><td>$average ms</td><td>$p90 ms</td><td>$p95 ms</td><td>$p99 ms</td><td>$maximum ms</td></tr>
    </tbody>
  </table>

  <h2>质量门禁</h2>
  <p><strong>结果：<span style="color:$qualityColor">$qualityText</span></strong></p>
  <ul>
    <li>错误率：$errorRate%，阈值：不高于 $MaxErrorRate% —— $(if ($errorGatePassed) { '通过' } else { '未通过' })</li>
    <li>P95：$p95 ms，阈值：不高于 $MaxP95Ms ms —— $(if ($p95GatePassed) { '通过' } else { '未通过' })</li>
  </ul>

  <h2>各请求统计</h2>
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr><th>请求名称</th><th>样本数</th><th>失败数</th><th>错误率</th><th>平均响应</th><th>最小响应</th><th>P95</th><th>最大响应</th></tr>
    </thead>
    <tbody>
$($labelRows.ToString())
    </tbody>
  </table>

  <h2>失败请求</h2>
$($failedRowsHtml.ToString())

  <h2>原始产物</h2>
  <ul>
    <li><a href="index.html">JMeter 原生交互式 Dashboard</a></li>
    <li><a href="statistics.json">JMeter statistics.json</a></li>
    <li><a href="raw-results.jtl">原始 JTL 结果</a></li>
  </ul>
</body>
</html>
"@

# 使用 UTF-8 无 BOM，避免 Jenkins/浏览器出现中文编码问题。
[System.IO.File]::WriteAllText(
    $summaryPath,
    $html,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "[OK] 已生成 JMeter 备用静态摘要: $summaryPath"
Write-Host "[INFO] 总样本=$total, 失败=$failed, 错误率=$errorRate%, P95=$p95 ms"
