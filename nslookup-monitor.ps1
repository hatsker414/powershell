$logFile = "nslookup_results.txt"
$domain = "FQDN"
$interval = 5  # Интервал в секундах между проверками

Write-Host "Запуск мониторинга nslookup для $domain (лог: $logFile). Для остановки нажмите Ctrl+C"

try {
    while ($true) {
        # Создаем объект для результатов
        $result = [PSCustomObject]@{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            ExecutionTime = $null
            Output = $null
        }

        # Измеряем время выполнения и захватываем вывод
        $time = Measure-Command { 
            $result.Output = nslookup $domain 2>&1 | Out-String 
        }

        $result.ExecutionTime = "$([math]::Round($time.TotalMilliseconds)) ms"
        
        # Форматируем запись лога
        $logEntry = @"
[$($result.Timestamp)] Запрос к $domain
Время выполнения: $($result.ExecutionTime)
Результат:
$($result.Output.Trim())
-------------------------------------------
"@

        # Добавляем запись в лог
        $logEntry | Out-File -FilePath $logFile -Append

        # Ожидаем перед следующей итерацией
        Start-Sleep -Seconds $interval
    }
}
finally {
    Write-Host "Мониторинг остановлен. Лог сохранен в $logFile"
}
