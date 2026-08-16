# voz.ps1 — lê em voz alta um ficheiro de texto UTF-8, na língua pedida.
# Usa o motor OneCore do Windows (Windows.Media.SpeechSynthesis), que é o
# único que tem a voz portuguesa "Microsoft Helia" neste PC.
# Correr com powershell.exe (5.1), não pwsh: o WinRT não carrega no PS 7.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File voz.ps1 -Ficheiro t.txt -Lingua pt-PT

param(
    [Parameter(Mandatory = $true)][string]$Ficheiro,
    [string]$Lingua = "pt-PT",
    [switch]$ListarVozes
)
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]

if ($ListarVozes) {
    [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices |
        ForEach-Object { $_.DisplayName + " | " + $_.Language }
    exit 0
}

$texto = [IO.File]::ReadAllText($Ficheiro, [Text.Encoding]::UTF8)
if (-not $texto.Trim()) { exit 0 }

$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$todas = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices
$voz = $todas | Where-Object { $_.Language -like ($Lingua + "*") } | Select-Object -First 1
if (-not $voz) {
    $pref = ($Lingua -split "-")[0]
    $voz = $todas | Where-Object { $_.Language -like ($pref + "*") } | Select-Object -First 1
}
if ($voz) { $synth.Voice = $voz }

# O IAsyncOperation do WinRT chega ao PowerShell como COM cru; a forma
# fiável de esperar por ele é convertê-lo num Task .NET por reflexão.
$asTaskGen = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq "AsTask" -and $_.GetParameters().Count -eq 1 -and
                   $_.GetParameters()[0].ParameterType.Name -eq "IAsyncOperation``1" })[0]
$asTask = $asTaskGen.MakeGenericMethod([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
$tarefa = $asTask.Invoke($null, @($synth.SynthesizeTextToStreamAsync($texto)))
$null = $tarefa.Wait(30000)
if (-not $tarefa.IsCompleted -or $tarefa.IsFaulted) { Write-Error "síntese de voz falhou"; exit 1 }
$stream = $tarefa.Result

# WinRT stream → WAV em disco → tocar de forma síncrona
$wav = [IO.Path]::ChangeExtension($Ficheiro, ".wav")
$leitura = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream.GetInputStreamAt(0))
$fs = [IO.File]::Create($wav)
$leitura.CopyTo($fs)
$fs.Close()

(New-Object System.Media.SoundPlayer $wav).PlaySync()
Remove-Item $wav -ErrorAction SilentlyContinue
