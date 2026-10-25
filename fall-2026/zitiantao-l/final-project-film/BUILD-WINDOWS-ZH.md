# EyeSpan V2 — 一条命令生成新版

## 放置
将本包内容解压到：
`F:\INFO7375-8\Final Project Pitch Film\eyespan-v2-kit`

确保 run_v2.py 直接在该文件夹中。原版 eyespan-film-starter/eyespan-film 保留不动。

## 运行
在已激活的 pitch-film PowerShell 中：
```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python 'F:\INFO7375-8\Final Project Pitch Film\eyespan-v2-kit\run_v2.py' --source 'F:\INFO7375-8\Final Project Pitch Film\eyespan-film-starter\eyespan-film' --project 'F:\INFO7375-8\Final Project Pitch Film\eyespan-film-v2' --toolkit 'F:\INFO7375-8\Final Project Pitch Film\brutalist.art'
```

脚本只读取原版，另建 eyespan-film-v2。它更新已审核的新版英文旁白，仅重新生成改变的段落；实测音频后按时长绘制动态片段，再运行原始 Brutalist 字体检查和最终编译/画面检查。不会更改原工具包或关闭检查。临时目录也设在新项目同盘。

若中途失败，保留报错；修复后重新运行同一命令，可以保留已完成的新版音频。不要同时运行两个构建进程。

## 成片
`F:\INFO7375-8\Final Project Pitch Film\eyespan-film-v2\eyespan-final-project-pitch.mp4`

```powershell
Start-Process -FilePath 'F:\INFO7375-8\Final Project Pitch Film\eyespan-film-v2\eyespan-final-project-pitch.mp4'
```

完整试听/观看新版后，再打包：
```powershell
python 'F:\INFO7375-8\Final Project Pitch Film\eyespan-film-v2\prepare_submission.py' --project 'F:\INFO7375-8\Final Project Pitch Film\eyespan-film-v2' --out 'F:\INFO7375-8\Final Project Pitch Film\submission-v2'
```

Canvas ZIP 与匹配的 GitHub 文件夹由打包脚本输出。尚未上传或生成真实 Git commit。

## 本版说明
- 新旁白 492 个英文单词；最终时长依本地 Kokoro 实测，不伪造时长。
- 双视角里的 A/B 是示意实例标签，不是模型实际读到的标签或运行结果。
- 三种时间情形使用构造的曲线；停留达标只请求确认，不直接抓取。
- 参考点/预测点对比是构造示例；数据拼图仅展示场景。
- 原型照片属于 RaycastGrasp，标注已有工作及你确认的实现贡献；不得改标为 EyeSpan 实际运行。
- 本片采用 Pillow/FFmpeg 图形片段，接入原工具包 media 槽；Manim 专用 A/W/B 检查不适用，不声称其通过。
- 字体检查使用完整自制文字区域清单，避免把照片纹理和图形轮廓当成字。最终 Gate V 仍检查全画面，无边界/稀疏/对比度豁免。
- 若日志出现 NO RENDERABLE BEATS，那是没有原生 Manim/Remotion 注释的提示；检查最终 13/13 filled、ready 状态和真实报告。
