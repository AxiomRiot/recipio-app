$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$eventsDir = '..\common\events'
$pyUtilsDir = '..\py-utils\src\schema'

if (-not (Test-Path $eventsDir)) {
    New-Item -ItemType Directory -Path $eventsDir -Force | Out-Null
}

Write-Host 'Generating typescript json schemas'
npx tsx (Join-Path $scriptDir '..\types-ts\scripts\zodToSchemaGenerator.js')

Write-Host 'Generating Python Pydantic schemas'
$schemaFiles = Get-ChildItem -Path $eventsDir -Filter '*.json' -File

if ($schemaFiles) {
  $schemaFiles | ForEach-Object {
      $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
      python -m datamodel_code_generator `
        --input $eventsDir\$_ `
        --input-file-type jsonschema `
        --output $pyUtilsDir/$baseName.py `
        --output-model-type pydantic_v2.BaseModel `
        --class-name $baseName
  }
}
else {
  Write-Host 'No schema files found in ' $eventsDir
}
