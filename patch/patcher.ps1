param([ValidateSet('install','restore','verify')][string]$Mode='install',[string]$GameDir='')
$ErrorActionPreference='Stop'
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
function P([string]$a,[string]$b){[IO.Path]::Combine($a,$b)}
function Sha([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToUpper()}
function Fail([string]$msg,[int]$code){Write-Host $msg -ForegroundColor Red; exit $code}
$SteamHelp='请在 Steam 中右键 Voidigo，选择「属性 > 已安装文件 > 验证游戏文件的完整性」，Steam 会自动下载英文原版文件。完成后如需中文，请等待对应新版补丁。/ In Steam: right-click Voidigo > Properties > Installed Files > Verify integrity of game files.'
# 补丁工具 xdelta3.exe 的固定哈希
$XHash='6855C01CF4A1662BA421E6F95370CF9AFA2B3AB6C148473C63EFE60D634DFB9A'
$X=P $Here 'xdelta3.exe'
# 可直接升级的旧版汉化哈希（按文件列出，新增旧版时往列表里加）
$Old=@{
 'voidigo.exe'=@(
  '75199F10F2C127830FBBE533A84FD16CD0D1337F16C9D7E6AF5A0D90433F093D' # v9r
 );
 'data.win'=@()
}
$H=@{
 'voidigo.exe'=@{van='2459C26A501CD874ED8D015D671FA96A7E40DAC8F97EE7B4A4DC2A1965F00C6D';zh='492CE1DE7C37691A486D68A8D8D9A52FCDA687F860FDD499E612F8D5A86D9921'};
 'data.win'=@{van='713D6FD12960B52A36C1C04F5F40E008378536D4DC2CB8A86D503BFAFADF4743';zh='A0728BB041850195400E8528F8439C7CBA5D92186B2C01AEBF86F5E2EAA740C8'}}
function HasGame([string]$d){ $d -and (Test-Path -LiteralPath (P $d 'voidigo.exe') -PathType Leaf) }
if(-not $GameDir){
 foreach($c in @("${env:ProgramFiles(x86)}\Steam\steamapps\common\Voidigo","C:\Steam\steamapps\common\Voidigo","D:\SteamLibrary\steamapps\common\Voidigo",(Get-Location).ProviderPath)){ if(HasGame $c){$GameDir=$c;break} } }
if(-not (HasGame $GameDir)){ $GameDir=Read-Host '请输入 Voidigo 游戏目录 / Enter Voidigo folder' }
if(-not (HasGame $GameDir)){ Fail "找不到 voidigo.exe / voidigo.exe not found: $GameDir" 4 }
$Bak=P $GameDir 'zh_cn_backup'
Write-Host "Game: $GameDir"
if(Get-Process voidigo -ErrorAction SilentlyContinue){ Fail '请先关闭游戏 / Please close Voidigo first.' 2 }
if($Mode -eq 'verify'){ foreach($f in $H.Keys){$g=P $GameDir $f; if(-not (Test-Path -LiteralPath $g)){"$f  MISSING";continue}; $s=Sha $g; $st= if($s -eq $H[$f].van){'vanilla'}elseif($s -eq $H[$f].zh){'zh-CN'}elseif($Old[$f] -contains $s){'zh-CN (old)'}else{'UNKNOWN'}; "$f  $st  $s"}; exit 0 }
if($Mode -eq 'restore'){
 # 先全部检查，确认安全再动文件
 $todo=@()
 foreach($f in $H.Keys){
  $g=P $GameDir $f; $b=P $Bak "$f.vanilla"; $s=Sha $g
  if($s -eq $H[$f].van){ "$f 已是英文原版 / already vanilla"; continue }
  if($s -ne $H[$f].zh -and -not ($Old[$f] -contains $s)){ Fail "$f 既不是汉化版也不是本补丁对应的原版，游戏可能已被 Steam 更新，不能用旧备份覆盖。/ Game file changed (Steam update?), backup not applied.`n$SteamHelp" 3 }
  if(-not (Test-Path -LiteralPath $b -PathType Leaf)){ Fail "缺少备份 / missing backup: $b`n$SteamHelp" 3 }
  if((Sha $b) -ne $H[$f].van){ Fail "备份文件校验不符 / backup hash mismatch: $f`n$SteamHelp" 3 }
  $todo+=$f }
 foreach($f in $todo){ $g=P $GameDir $f
  [IO.File]::Copy((P $Bak "$f.vanilla"),$g,$true)
  if((Sha $g) -ne $H[$f].van){ Fail "还原校验失败 / restore verify failed: $f`n$SteamHelp" 3 }; "已还原 / restored $f" }
 '完成。/ Done.'; exit 0 }
# install
if(-not (Test-Path -LiteralPath $X -PathType Leaf)){ Fail "缺少 xdelta3.exe / missing: $X" 5 }
if((Sha $X) -ne $XHash){ Fail "xdelta3.exe 校验不符，文件可能被替换或损坏，已拒绝运行。请重新从发布页下载补丁包。/ xdelta3.exe hash mismatch, refusing to run. Re-download the package." 5 }
$plan=@()
foreach($f in $H.Keys){
 $g=P $GameDir $f; $s=Sha $g; $b=P $Bak "$f.vanilla"
 if($s -eq $H[$f].zh){ "$f 已是中文版 / already patched"; continue }
 $hasBak=(Test-Path -LiteralPath $b -PathType Leaf) -and ((Sha $b) -eq $H[$f].van)
 if(($Old[$f] -contains $s) -and $hasBak){ "$f 从旧版汉化升级 / upgrading older zh build"; $plan+=@{f=$f;fresh=$false}; continue }
 if($s -ne $H[$f].van){ Fail "$f 版本不符（SHA256 $s），补丁只支持当前 Steam 版。/ Unsupported version.`n$SteamHelp" 1 }
 $plan+=@{f=$f;fresh=$true} }
if($plan.Count -gt 0){ [IO.Directory]::CreateDirectory($Bak) | Out-Null }
foreach($it in $plan){ $f=$it.f; $g=P $GameDir $f; $b=P $Bak "$f.vanilla"
 if($it.fresh){ [IO.File]::Copy($g,$b,$true); if((Sha $b) -ne $H[$f].van){ Fail "备份失败 / backup failed: $f" 1 } }
 $tmp="$g.zhtmp"
 & $X -d -f -B 1610612736 -s $b (P $Here "$f.xd3") $tmp
 if($LASTEXITCODE -ne 0){ if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Force}; Fail "xdelta3 失败 / failed: $f" 1 }
 if((Sha $tmp) -ne $H[$f].zh){ Remove-Item -LiteralPath $tmp -Force; Fail "补丁结果校验失败 / patched hash mismatch: $f" 1 }
 Move-Item -LiteralPath $tmp -Destination $g -Force; "已安装 / patched $f" }
'完成。/ Done.'
exit 0
