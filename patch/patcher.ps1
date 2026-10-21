param([ValidateSet('install','restore','verify')][string]$Mode='install',[string]$GameDir='')
$ErrorActionPreference='Stop'
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
$X=Join-Path $Here 'xdelta3.exe'
$Old=@('75199F10F2C127830FBBE533A84FD16CD0D1337F16C9D7E6AF5A0D90433F093D')
$H=@{
 'voidigo.exe'=@{van='2459C26A501CD874ED8D015D671FA96A7E40DAC8F97EE7B4A4DC2A1965F00C6D';zh='492CE1DE7C37691A486D68A8D8D9A52FCDA687F860FDD499E612F8D5A86D9921'};
 'data.win'=@{van='713D6FD12960B52A36C1C04F5F40E008378536D4DC2CB8A86D503BFAFADF4743';zh='A0728BB041850195400E8528F8439C7CBA5D92186B2C01AEBF86F5E2EAA740C8'}}
function Sha($p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToUpper()}
if(-not $GameDir){
 foreach($c in @("${env:ProgramFiles(x86)}\Steam\steamapps\common\Voidigo","C:\Steam\steamapps\common\Voidigo","D:\SteamLibrary\steamapps\common\Voidigo",(Get-Location).Path)){ if(Test-Path (Join-Path $c 'voidigo.exe')){$GameDir=$c;break} } }
if(-not $GameDir -or -not (Test-Path (Join-Path $GameDir 'voidigo.exe'))){ $GameDir=Read-Host '请输入 Voidigo 游戏目录 / Enter Voidigo folder' }
$Bak=Join-Path $GameDir 'zh_cn_backup'
Write-Host "Game: $GameDir"
if(Get-Process voidigo -ErrorAction SilentlyContinue){ Write-Host '请先关闭游戏 / Please close Voidigo first.'; exit 2 }
if($Mode -eq 'verify'){ foreach($f in $H.Keys){$s=Sha (Join-Path $GameDir $f); $st= if($s -eq $H[$f].van){'vanilla'}elseif($s -eq $H[$f].zh){'zh-CN'}else{'UNKNOWN'}; "$f  $st  $s"}; exit 0 }
if($Mode -eq 'restore'){
 foreach($f in $H.Keys){ $b=Join-Path $Bak "$f.vanilla"; if(-not (Test-Path $b)){throw "缺少备份 / missing backup: $b"}
  if((Sha $b) -ne $H[$f].van){throw "备份校验失败 / backup hash mismatch: $f"}
  Copy-Item -LiteralPath $b (Join-Path $GameDir $f) -Force
  if((Sha (Join-Path $GameDir $f)) -ne $H[$f].van){throw "还原校验失败 / restore verify failed: $f"}; "已还原 / restored $f" }
 exit 0 }
New-Item -ItemType Directory -Force $Bak | Out-Null
foreach($f in $H.Keys){
 $g=Join-Path $GameDir $f; $s=Sha $g
 if($s -eq $H[$f].zh){ "$f 已是中文版 / already patched"; continue }
 $b=Join-Path $Bak "$f.vanilla"
 if($Old -contains $s -and (Test-Path $b) -and (Sha $b) -eq $H[$f].van){ "$f 从旧版汉化升级 / upgrading older zh build" }
 else{
 if($s -ne $H[$f].van){ throw "$f 版本不符（SHA256 $s）。请在 Steam 中「验证游戏文件完整性」后重试。/ Unsupported version; verify game files in Steam." }
 Copy-Item -LiteralPath $g $b -Force
 if((Sha $b) -ne $H[$f].van){throw "备份失败 / backup failed: $f"} }
 $tmp="$g.zhtmp"; & $X -d -f -B 1610612736 -s $b (Join-Path $Here "$f.xd3") $tmp
 if($LASTEXITCODE -ne 0){throw "xdelta3 失败 / failed: $f"}
 if((Sha $tmp) -ne $H[$f].zh){Remove-Item $tmp; throw "补丁结果校验失败 / patched hash mismatch: $f"}
 Move-Item -LiteralPath $tmp $g -Force; "已安装 / patched $f" }
'完成！/ Done.'
