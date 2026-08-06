[CmdletBinding()]
param(
    [Parameter()]
    [string]$ProjectRoot,

    [Parameter()]
    [switch]$NoDialog,

    [Parameter()]
    [switch]$Wait
)

$ErrorActionPreference = 'Stop'

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

function Stop-Launcher {
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [Parameter(Mandatory)]
        [int]$ExitCode
    )

    if ($NoDialog) {
        [Console]::Error.WriteLine($Message)
    }
    else {
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show(
            $Message,
            'NCU Gym Monitor',
            [System.Windows.MessageBoxButton]::OK,
            [System.Windows.MessageBoxImage]::Error
        ) | Out-Null
    }

    exit $ExitCode
}

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    Stop-Launcher -ExitCode 10 -Message 'The NCU Gym Monitor checkout is missing. Restore it, then rerun Setup.'
}

$windowedPython = Join-Path $ProjectRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $windowedPython -PathType Leaf)) {
    Stop-Launcher -ExitCode 11 -Message 'The Project environment is missing. Rerun Setup to repair it.'
}

$widgetEntryPoint = Join-Path $ProjectRoot 'gym.pyw'
if (-not (Test-Path -LiteralPath $widgetEntryPoint -PathType Leaf)) {
    Stop-Launcher -ExitCode 12 -Message 'The Widget entry point is missing from the checkout. Restore the checkout, then rerun Setup.'
}

$dependencyCheck = Start-Process `
    -FilePath $windowedPython `
    -ArgumentList @('-c', '"import requests, bs4, PIL"') `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -Wait `
    -PassThru

if ($dependencyCheck.ExitCode -ne 0) {
    Stop-Launcher -ExitCode 13 -Message 'The Widget runtime dependencies are missing. Rerun Setup to repair the Project environment.'
}

$launchArguments = @('"' + $widgetEntryPoint + '"')
if ($Wait) {
    $monitorProcess = Start-Process `
        -FilePath $windowedPython `
        -ArgumentList $launchArguments `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -Wait `
        -PassThru

    if ($monitorProcess.ExitCode -ne 0) {
        Stop-Launcher -ExitCode 14 -Message 'The Widget failed during startup. Rerun Setup; if the problem continues, restore the checkout.'
    }
}
else {
    Start-Process `
        -FilePath $windowedPython `
        -ArgumentList $launchArguments `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden | Out-Null
}
