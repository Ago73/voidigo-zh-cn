// Headless: append Fusion Pixel CJK glyphs to fnt_default on a new embedded texture; save data.win.cn
using System.Text;
using System.Linq;
using ImageMagick;
using UndertaleModLib.Util;
EnsureDataLoaded();
string dir = @"C:\Users\35036\voidigo-l10n\";
string log = dir + "import_cjk_" + Environment.GetEnvironmentVariable("CJK_V") + ".log";
File.WriteAllText(log, "start\n");
var f = Data.Fonts.First(x => x.Name.Content == "fnt_default");
var t = f.Texture;
int ow = t.SourceWidth, oh = t.SourceHeight;
var worker = new TextureWorker();
var orig = worker.GetTextureFor(t, "fnt_default", false);
var cjk = new MagickImage(dir + Environment.GetEnvironmentVariable("CJK_V") + "\\cjk_atlas.png");
int W = Math.Max(1024, ow), H = oh + 1 + (int)cjk.Height;
int PW = 1; while (PW < W) PW *= 2; int PH = 1; while (PH < H) PH *= 2;
var atlas = new MagickImage(MagickColors.Transparent, (uint)PW, (uint)PH);
atlas.Composite(orig, 0, 0, CompositeOperator.Copy);
atlas.Composite(cjk, 0, oh + 1, CompositeOperator.Copy);
atlas.Write(dir + "fnt_default_cn_atlas_" + Environment.GetEnvironmentVariable("CJK_V") + ".png");
var tex = new UndertaleEmbeddedTexture();
tex.Name = new UndertaleString("Texture " + Data.EmbeddedTextures.Count);
tex.TextureData.Image = GMImage.FromMagickImage(atlas).ConvertToPng();
Data.EmbeddedTextures.Add(tex);
var tpi = new UndertaleTexturePageItem();
tpi.Name = new UndertaleString("PageItem " + Data.TexturePageItems.Count);
tpi.SourceX = 0; tpi.SourceY = 0; tpi.SourceWidth = (ushort)W; tpi.SourceHeight = (ushort)H;
tpi.TargetX = 0; tpi.TargetY = 0; tpi.TargetWidth = (ushort)W; tpi.TargetHeight = (ushort)H;
tpi.BoundingWidth = (ushort)W; tpi.BoundingHeight = (ushort)H; tpi.TexturePage = tex;
Data.TexturePageItems.Add(tpi);
f.Texture = tpi;   // original glyph coords stay valid (orig region at 0,0)
var have = new HashSet<ushort>(f.Glyphs.Select(g => g.Character));
int added = 0;
foreach (var line in File.ReadAllLines(dir + Environment.GetEnvironmentVariable("CJK_V") + "\\cjk_glyphs.tsv")) {
  var p = line.Split('\t'); if (p.Length < 7) continue;
  ushort ch = ushort.Parse(p[0]); if (have.Contains(ch)) continue;
  var g = new UndertaleFont.Glyph();
  g.Character = ch; g.SourceX = ushort.Parse(p[1]); g.SourceY = (ushort)(ushort.Parse(p[2]) + oh + 1);
  g.SourceWidth = ushort.Parse(p[3]); g.SourceHeight = ushort.Parse(p[4]);
  g.Shift = short.Parse(p[5]); g.Offset = short.Parse(p[6]);
  f.Glyphs.Add(g); added++;
}
var sorted = f.Glyphs.OrderBy(g => g.Character).ToList();
f.Glyphs.Clear(); foreach (var g in sorted) f.Glyphs.Add(g);
f.RangeEnd = Math.Max(f.RangeEnd, (uint)sorted.Last().Character);
File.AppendAllText(log, $"orig={ow}x{oh} page={PW}x{PH} added={added} total={f.Glyphs.Count} EmSize={f.EmSize}\n");
using (var fs = new FileStream(dir + "data.win.cn" + Environment.GetEnvironmentVariable("CJK_V"), FileMode.Create)) UndertaleIO.Write(fs, Data);
File.AppendAllText(log, "SAVED\n");
