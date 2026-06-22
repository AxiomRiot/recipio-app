# Requires PowerShell 7+ for ConvertFrom-Yaml
$ErrorActionPreference = 'Stop'

if (-not (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue)) {
    Write-Error 'ConvertFrom-Yaml is not available. Run this script with PowerShell 7+ or install a YAML parser module.'
    exit 1
}

$KAFKA_CONTAINER = if ($env:KAFKA_CONTAINER) { $env:KAFKA_CONTAINER } else { 'kafka' }
$BROKER = if ($env:KAFKA_BROKER) { $env:KAFKA_BROKER } else { 'kafka:9092' }
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TOPICS_FILE = Join-Path -Path $ScriptDir -ChildPath '..\kafka\topics.yml'

if (-not (Test-Path -Path $TOPICS_FILE)) {
    Write-Error "Topics file not found: $TOPICS_FILE"
    exit 1
}

Write-Host "Reading topic config from $TOPICS_FILE..."

$topicsConfig = Get-Content -Path $TOPICS_FILE -Raw | ConvertFrom-Yaml

foreach ($topic in $topicsConfig.topics) {
    $name = $topic.name
    $partitions = $topic.partitions
    $replication = $topic.replication_factor
    $retention_ms = $topic.retention_ms
    $cleanup_policy = $topic.cleanup_policy

    Write-Host "Creating topic: $name (partitions=$partitions, retention=${retention_ms}ms)"

    $dockerArgs = @(
        'exec', $KAFKA_CONTAINER,
        '/opt/kafka/bin/kafka-topics.sh',
        '--bootstrap-server', $BROKER,
        '--create',
        '--if-not-exists',
        '--topic', $name,
        '--partitions', [string]$partitions,
        '--replication-factor', [string]$replication,
        '--config', "retention.ms=$retention_ms",
        '--config', "cleanup.policy=$cleanup_policy"
    )

    docker @dockerArgs
}

Write-Host 'All topics created.'
