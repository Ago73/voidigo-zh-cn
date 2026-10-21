**《Voidigo》官方没有中文，只有英语和瑞典语。本补丁让中文玩家能完整游玩。**

# Voidigo 简体中文汉化补丁 v10.1（非官方）｜切屏优化 · 宋体12px像素字库 · 逐字换行 · 全文本含图鉴

为《Voidigo》（semiwork 开发）提供完整简体中文。**不含任何游戏文件**，只含二进制差分补丁，应用于你自己的正版游戏。

## 特色
- **切屏优化**：Alt-Tab 切出切入不再白屏闪烁；无边框窗口稳定，不会在窗口化/有边框之间来回闪烁。
- **宋体 12px 像素字库**：清晰锐利，贴合游戏像素风格（2,542 个汉字及符号）。
- **中文逐字换行 + 避头尾**：中文可在任意字间断行，标点不出现在行首，不再塞多余空格。
- **全文本汉化**：道具、武器、角色、对话旁白、教程、界面、联机大厅、片尾字幕，以及**图鉴（敌人、首领、场景物件）**。
- 安装前校验原版哈希、自动备份，一键还原；已装 v9r 可直接覆盖升级。

## 效果对比（截图待补）
> 以下截图位待补充，同一场景英文原版与汉化版对照。

| 场景 | 英文原版 | 汉化版 |
|---|---|---|
| 道具说明 | （待补：en_item.png） | （待补：zh_item.png） |
| 菜单界面 | （待补：en_menu.png） | （待补：zh_menu.png） |
| 图鉴 | （待补：en_bestiary.png） | （待补：zh_bestiary.png） |
| Alt-Tab 切屏 | （待补：原版切屏闪烁） | （待补：修复后切屏） |

## 兼容版本
仅支持当前 Steam 版（v1.1.0.1）：
| 文件 | 原版 SHA256 | 汉化后 SHA256 |
|---|---|---|
| voidigo.exe | `2459C26A501CD874ED8D015D671FA96A7E40DAC8F97EE7B4A4DC2A1965F00C6D` | `492CE1DE7C37691A486D68A8D8D9A52FCDA687F860FDD499E612F8D5A86D9921` |
| data.win | `713D6FD12960B52A36C1C04F5F40E008378536D4DC2CB8A86D503BFAFADF4743` | `A0728BB041850195400E8528F8439C7CBA5D92186B2C01AEBF86F5E2EAA740C8` |

哈希不符时补丁会拒绝安装。请先在 Steam“属性 → 已安装文件 → 验证游戏文件的完整性”。游戏更新后需等待新版补丁。

## 安装
1. 关闭游戏。
2. 解压后双击 `patch\install.bat`（推荐）。`安装中文.bat` 功能相同，但部分旧解压工具会把中文文件名解成乱码，此时请用 `install.bat`。
3. 自动查找 Steam 目录；找不到时会要求输入游戏目录，也可运行 `patcher.ps1 -GameDir "D:\...\Voidigo"`。
4. 补丁会先校验自带 xdelta3.exe 的哈希，再校验原版哈希 → 备份到 `游戏目录\zh_cn_backup\` → 生成汉化文件 → 校验结果哈希。

## 卸载 / 还原
双击 `patch\uninstall.bat`（推荐，`还原英文.bat` 功能相同）从备份还原并校验。若汉化后 Steam 更新过游戏，还原会停止并提示改用 Steam“验证游戏文件的完整性”，不会用旧备份覆盖新文件。
查看状态：`powershell -ExecutionPolicy Bypass -File patcher.ps1 -Mode verify`

## 目录
- `patch/`：补丁程序，支持路径含方括号等特殊字符的游戏目录（patcher.ps1、.bat、xdelta3.exe、*.xd3）
- `text/zh_final_v10.json`：英→中文本对照表；`glossary.*`：术语表；`cjk_charset.txt`：字库字符集
- `scripts/`：字库烘焙 `bake_cjk_atlas4.py`；exe 字符串重定位 `patch_exe_reloc_v9.py`（+`v9_new_keys.json`）与合成 `compose_v10.py`；UndertaleModTool 字体导入 `import_cjk_font_v.csx`、`import_cjk_font.csx`，构建脚本 `build_cn_v.cmd`

## 致谢
汉化：Plan5。

## 许可与声明
本汉化为玩家自制的非官方翻译，与 semiwork 无关。《Voidigo》本体及全部美术、音频、代码等资产版权归 semiwork 所有。本包仅分发译文与差分补丁，请支持正版。
`xdelta3.exe` 来自 xdelta 3.1.0（https://github.com/jmacd/xdelta-gpl ），按 GPL 授权，源码见该链接。

---
## English (short)
Unofficial Simplified Chinese fan translation for Voidigo (by semiwork), v10. Highlights: alt-tab without white flash & stable borderless window; SimSun 12px pixel font; per-character CJK line breaking with kinsoku; full text including the bestiary. NO game files included, binary deltas only.
Install: close the game, run `patch\install.bat` (checks vanilla SHA256 above, backs up to `<game>\zh_cn_backup\`, applies xdelta, verifies output). Uninstall: `patch\uninstall.bat` or verify files in Steam.
Translation: Plan5. Game and all assets © semiwork. xdelta3 is GPL (source link above).
