param(
    [Parameter(Mandatory = $true)]
    [string]$FramesDir
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$artifacts = Join-Path $projectRoot "artifacts"
$buildDir = Join-Path $artifacts "demo-build"
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

$ffmpeg = (Get-ChildItem -LiteralPath (Join-Path $projectRoot ".venv\Lib\site-packages\imageio_ffmpeg\binaries") -Filter "ffmpeg*.exe" | Select-Object -First 1).FullName
if (-not (Test-Path -LiteralPath $ffmpeg)) { throw "FFmpeg not found: $ffmpeg" }

Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice("Microsoft Zira Desktop")
$voice.Rate = 0
$voice.Volume = 100

$segments = @(
    @{ Name="01-cover"; Image=(Join-Path $artifacts "devpost-thumbnail.png"); Duration=14; Text="My system drive ran low while another drive had plenty of space. Finding files was easy. The hard question was what an autonomous agent could remove safely, and how to prove a retry never acts twice." },
    @{ Name="02-architecture"; Image=(Join-Path $artifacts "architecture.png"); Duration=27; Text="Red Tag is a background operations agent, not a chatbot. A threshold creates an incident. A public Cloud Run API writes Firestore and dispatches Pub Sub to a private worker. Five Google ADK specialists reason with Gemini 3.6 Flash. Deterministic code alone owns policy, execution, idempotency, and recovery verification." },
    @{ Name="03-local"; Image=(Join-Path $artifacts "demo-local-proof.png"); Duration=25; Text="Here is a real Windows action against a deliberately managed cache. Red Tag removed sixty four mebibytes and sixty four files. The protected sibling remained. An unmarked parent was blocked. Then the same delivery was replayed. The durable action count stayed exactly one." },
    @{ Name="04-cloud"; Frames=$FramesDir; Duration=49; Text="Now the live Google Cloud pipeline. One click creates a real Firestore incident and publishes it. The authenticated private Cloud Run worker invokes the five agent workflow. The intake agent normalizes evidence. The investigator separates facts from hypotheses. The planner chooses the smallest reversible action. Policy checks the boundary. Verification closes only after recovery is proven. Finally, Red Tag deliberately replays the delivery. Firestore rejects the duplicate, and the console ends on proof complete." },
    @{ Name="05-safety"; Image=(Join-Path $artifacts "demo-safety.png"); Duration=28; Text="The model never receives filesystem authority. The adapter requires an exact marker, rejects links and escaped paths, and touches only regular files inside the managed cache child. Severe or unknown actions require a human. If reasoning fails before action, the delivery claim is safely released for retry. If a retry arrives after action, the ledger blocks execution." },
    @{ Name="06-outro"; Image=(Join-Path $artifacts "demo-outro.png"); Duration=14; Text="Retries may repeat reasoning. Red Tag never repeats the operational action. Act once. Prove recovery. That is how an agent earns permission to act." }
)

$videoFilter = "scale=1440:900:force_original_aspect_ratio=decrease,pad=1440:900:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p"
$segmentFiles = @()
foreach ($segment in $segments) {
    $wav = Join-Path $buildDir "$($segment.Name).wav"
    $mp4 = Join-Path $buildDir "$($segment.Name).mp4"
    $voice.SetOutputToWaveFile($wav)
    $voice.Speak($segment.Text)
    $voice.SetOutputToNull()

    if ($segment.ContainsKey("Frames")) {
        $inputArgs = @("-framerate", "2", "-i", (Join-Path $segment.Frames "frame-%05d.jpg"))
    } else {
        $inputArgs = @("-loop", "1", "-i", $segment.Image)
    }
    $args = @("-y", "-loglevel", "warning") + $inputArgs + @(
        "-i", $wav, "-vf", $videoFilter, "-filter_complex", "[1:a]apad[a]",
        "-map", "0:v:0", "-map", "[a]", "-t", [string]$segment.Duration,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac",
        "-b:a", "160k", "-movflags", "+faststart", $mp4
    )
    & $ffmpeg @args
    if ($LASTEXITCODE -ne 0) { throw "FFmpeg failed for $($segment.Name)" }
    $segmentFiles += $mp4
}
$voice.Dispose()

$output = Join-Path $artifacts "red-tag-demo.mp4"
$concatArgs = @("-y", "-loglevel", "warning")
foreach ($segmentFile in $segmentFiles) { $concatArgs += @("-i", $segmentFile) }
$concatInputs = (0..($segmentFiles.Count - 1) | ForEach-Object { "[$($_):v:0][$($_):a:0]" }) -join ""
$concatArgs += @(
    "-filter_complex", ($concatInputs + "concat=n=$($segmentFiles.Count):v=1:a=1[v][a]"),
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart", $output
)
& $ffmpeg @concatArgs
if ($LASTEXITCODE -ne 0) { throw "FFmpeg concat failed" }
Write-Output $output
