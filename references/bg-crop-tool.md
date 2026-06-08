# 背景裁剪工具 bg-crop-tool

> 把下载的武侠壁纸裁剪成适合手游背景的尺寸（1080×1920 竖屏优先）。

## 安装位置

`/usr/local/bin/bg-crop-tool`（Python 脚本，依赖 Pillow）

## 用法

```bash
# 处理 /tmp/wuxia_images/ 和 /tmp/martial_arts_images/ 下所有图，输出 1080×1920
bg-crop-tool

# 指定输入和尺寸
bg-crop-tool /path/to/images -o ./output -W 768 -H 1024

# 预设
bg-crop-tool --preset phone      # 720×1280
bg-crop-tool --preset phone_hd   # 1080×1920（默认）
bg-crop-tool --preset landscape  # 1920×1080
bg-crop-tool --preset square     # 1080×1080

# 智能裁剪（主体偏上时用 crop_y=0.3）
bg-crop-tool -m smart --crop-y 0.3
```

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| -W / --width | 1080 | 目标宽度 |
| -H / --height | 1920 | 目标高度 |
| -q / --quality | 90 | JPEG 质量 |
| -m / --mode | center | center=中心裁剪, smart=自定义焦点 |
| --crop-y | 0.5 | 焦点 Y 位置（0=顶部, 1=底部） |
