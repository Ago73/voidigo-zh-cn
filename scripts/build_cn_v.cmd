@echo off
rem usage: build_cn_v.cmd A|B   -> data.win.cnA / data.win.cnB (not installed)
set V=%1
set CJK_V=%V%
set D=%USERPROFILE%\voidigo-l10n
"C:\Tools\UndertaleModTool\UndertaleModCli.exe" load "C:\steam\steamapps\common\Voidigo_backup\data.win.vanilla" --scripts "%D%\import_cjk_font_v.csx" < nul > "%D%\build_cn%V%.out" 2>&1
echo IMPORT_EXIT:%ERRORLEVEL% >> "%D%\build_cn%V%.out"
certutil -hashfile "%D%\data.win.cn%V%" SHA256 >> "%D%\build_cn%V%.out"
