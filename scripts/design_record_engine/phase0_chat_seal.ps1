[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ExportRoot,
    [switch]$VerifyOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$ManifestFileName = "MANIFEST.sha256"
$MetadataFileName = "EXPORT_METADATA.json"
$SealReadmeFileName = "SEAL_README.md"
$SelfHashZero = "0000000000000000000000000000000000000000000000000000000000000000"

function Write-Utf8Lf {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $normalized = $Text -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    [System.IO.File]::WriteAllText($Path, $normalized, $Utf8NoBom)
}

function Get-Sha256HexOfBytes {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($Bytes)
        return ([System.BitConverter]::ToString($hashBytes) -replace "-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-Sha256HexOfText {
    param([Parameter(Mandatory = $true)][string]$Text)
    $bytes = $Utf8NoBom.GetBytes($Text)
    return Get-Sha256HexOfBytes -Bytes $bytes
}

function Get-Sha256HexOfFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $hashBytes = $sha.ComputeHash($stream)
        return ([System.BitConverter]::ToString($hashBytes) -replace "-", "").ToLowerInvariant()
    }
    finally {
        $stream.Dispose()
        $sha.Dispose()
    }
}

function Resolve-ExportRootPath {
    param([Parameter(Mandatory = $true)][string]$InputPath)
    $fullPath = [System.IO.Path]::GetFullPath($InputPath)
    if (-not [System.IO.Directory]::Exists($fullPath)) {
        throw "Export root does not exist or is not a directory: $InputPath"
    }
    return $fullPath
}

function To-PosixRelPath {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [Parameter(Mandatory = $true)][string]$FullPath
    )
    $rel = [System.IO.Path]::GetRelativePath($RootPath, $FullPath)
    return $rel.Replace("\", "/")
}

function Sort-Ordinal {
    param([Parameter(Mandatory = $true)][string[]]$Values)
    if ($null -eq $Values -or $Values.Count -eq 0) {
        return @()
    }
    $copy = [string[]]$Values.Clone()
    [System.Array]::Sort($copy, [System.StringComparer]::Ordinal)
    return $copy
}

function Get-FileRecords {
    param(
        [Parameter(Mandatory = $true)][string]$RootPath,
        [Parameter(Mandatory = $true)][string[]]$ExcludedNames
    )
    $excluded = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($name in $ExcludedNames) {
        [void]$excluded.Add($name)
    }

    $records = @()
    Get-ChildItem -LiteralPath $RootPath -Recurse -File | ForEach-Object {
        if (-not $excluded.Contains($_.Name)) {
            $records += [pscustomobject]@{
                FullPath  = $_.FullName
                RelPath   = (To-PosixRelPath -RootPath $RootPath -FullPath $_.FullName)
                SizeBytes = [int64]$_.Length
            }
        }
    }

    if ($records.Count -eq 0) {
        return @()
    }
    return @($records | Sort-Object -Property RelPath)
}

function Convert-ManifestMapToText {
    param([Parameter(Mandatory = $true)][hashtable]$ManifestMap)
    $paths = Sort-Ordinal -Values ([string[]]$ManifestMap.Keys)
    $lines = foreach ($path in $paths) {
        "{0} {1}" -f $ManifestMap[$path], $path
    }
    return ($lines -join "`n") + "`n"
}

function Write-ExportMetadata {
    param([Parameter(Mandatory = $true)][string]$RootPath)
    $sourceRecords = Get-FileRecords -RootPath $RootPath -ExcludedNames @($ManifestFileName, $MetadataFileName, $SealReadmeFileName)

    $sourceMap = @{}
    foreach ($record in $sourceRecords) {
        $sourceMap[$record.RelPath] = Get-Sha256HexOfFile -Path $record.FullPath
    }
    $sourceBasis = ""
    if ($sourceMap.Count -gt 0) {
        $sourceBasis = Convert-ManifestMapToText -ManifestMap $sourceMap
    }
    $exportId = Get-Sha256HexOfText -Text $sourceBasis

    $totalBytes = 0
    if ($sourceRecords.Count -gt 0) {
        $measure = $sourceRecords | Measure-Object -Property SizeBytes -Sum
        if ($null -ne $measure.Sum) {
            $totalBytes = [int64]$measure.Sum
        }
    }

    $conversations = @($sourceRecords.RelPath | Where-Object { $_ -like "conversations-*.json" } | Sort-Object)
    $attachments = @($sourceRecords.RelPath | Where-Object { $_ -like "attachments/*" } | Sort-Object)
    $htmlFiles = @($sourceRecords.RelPath | Where-Object { $_ -like "*.html" } | Sort-Object)

    $metadata = [ordered]@{
        schema_version = "design_record_engine.chat_export_seal.v1"
        export_id = $exportId
        sealed_at_utc = $null
        source_files_count = [int]$sourceRecords.Count
        source_files_total_bytes = $totalBytes
        special_files = [ordered]@{
            conversations = $conversations
            chat_html = $htmlFiles
            attachments = $attachments
            seal_files = @($MetadataFileName, $SealReadmeFileName, $ManifestFileName)
        }
    }

    $json = $metadata | ConvertTo-Json -Depth 6
    if (-not $json.EndsWith("`n")) {
        $json += "`n"
    }
    Write-Utf8Lf -Path (Join-Path $RootPath $MetadataFileName) -Text $json
}

function Write-SealReadme {
    param([Parameter(Mandatory = $true)][string]$RootPath)
    $content = @'
# Chat Export Seal

This folder is sealed by `scripts/design_record_engine/phase0_chat_seal.ps1`.

Generated files:
- `EXPORT_METADATA.json`
- `SEAL_README.md`
- `MANIFEST.sha256`

Manifest format:
`<sha256> <posix_rel_path>`

Verification:
`pwsh -NoProfile -File scripts/design_record_engine/phase0_chat_seal.ps1 -ExportRoot <path> -VerifyOnly`
'@
    if (-not $content.EndsWith("`n")) {
        $content += "`n"
    }
    Write-Utf8Lf -Path (Join-Path $RootPath $SealReadmeFileName) -Text $content
}

function Write-Manifest {
    param([Parameter(Mandatory = $true)][string]$RootPath)
    $records = Get-FileRecords -RootPath $RootPath -ExcludedNames @($ManifestFileName)

    $manifestMap = @{}
    foreach ($record in $records) {
        $manifestMap[$record.RelPath] = Get-Sha256HexOfFile -Path $record.FullPath
    }
    $manifestMap[$ManifestFileName] = $SelfHashZero

    $provisional = Convert-ManifestMapToText -ManifestMap $manifestMap
    $selfHash = Get-Sha256HexOfText -Text $provisional
    $manifestMap[$ManifestFileName] = $selfHash

    $final = Convert-ManifestMapToText -ManifestMap $manifestMap
    Write-Utf8Lf -Path (Join-Path $RootPath $ManifestFileName) -Text $final
}

function Verify-Manifest {
    param([Parameter(Mandatory = $true)][string]$RootPath)

    $manifestPath = Join-Path $RootPath $ManifestFileName
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Missing required manifest: $ManifestFileName"
    }

    $rawText = [System.IO.File]::ReadAllText($manifestPath, [System.Text.Encoding]::UTF8)
    $normalized = $rawText -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    $lines = @($normalized -split "`n" | Where-Object { $_ -ne "" })
    if ($lines.Count -eq 0) {
        throw "Manifest is empty."
    }

    $manifestMap = @{}
    $pathsInOrder = @()
    foreach ($line in $lines) {
        if ($line -notmatch "^([0-9a-f]{64}) (.+)$") {
            throw "Invalid manifest line format: $line"
        }
        $hash = $Matches[1]
        $path = $Matches[2]
        if ($path.Contains("\")) {
            throw "Manifest path must use POSIX separators: $path"
        }
        if ($manifestMap.ContainsKey($path)) {
            throw "Duplicate manifest path: $path"
        }
        $manifestMap[$path] = $hash
        $pathsInOrder += $path
    }

    if (-not $manifestMap.ContainsKey($ManifestFileName)) {
        throw "Manifest missing self entry: $ManifestFileName"
    }

    $sortedPaths = Sort-Ordinal -Values ([string[]]$pathsInOrder)
    for ($i = 0; $i -lt $pathsInOrder.Count; $i++) {
        if ($pathsInOrder[$i] -cne $sortedPaths[$i]) {
            throw "Manifest paths are not lexicographically sorted."
        }
    }

    foreach ($path in $sortedPaths) {
        if ($path -eq $ManifestFileName) {
            continue
        }
        $nativeRel = $path.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
        $fullPath = Join-Path $RootPath $nativeRel
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
            throw "Manifest references missing file: $path"
        }
        $actualHash = Get-Sha256HexOfFile -Path $fullPath
        $expectedHash = $manifestMap[$path]
        if ($actualHash -cne $expectedHash) {
            throw "Hash mismatch for '$path': expected $expectedHash got $actualHash"
        }
    }

    $selfHash = $manifestMap[$ManifestFileName]
    $manifestMap[$ManifestFileName] = $SelfHashZero
    $zeroedText = Convert-ManifestMapToText -ManifestMap $manifestMap
    $computedSelfHash = Get-Sha256HexOfText -Text $zeroedText
    if ($computedSelfHash -cne $selfHash) {
        throw "Manifest self-hash mismatch: expected $selfHash got $computedSelfHash"
    }
}

try {
    $resolvedRoot = Resolve-ExportRootPath -InputPath $ExportRoot
    if ($VerifyOnly) {
        Verify-Manifest -RootPath $resolvedRoot
        Write-Output "OK: Manifest verification succeeded."
        exit 0
    }

    Write-ExportMetadata -RootPath $resolvedRoot
    Write-SealReadme -RootPath $resolvedRoot
    Write-Manifest -RootPath $resolvedRoot
    Verify-Manifest -RootPath $resolvedRoot
    Write-Output "OK: Chat export sealed successfully."
    exit 0
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
