# 剪贴板历史管理器 — 项目文档

## 项目概述

Windows 桌面剪贴板历史记录工具。自动监听剪贴板变化，记录每次复制的文字和图片，支持历史查看、搜索、重新复制、深色/浅色模式切换。

**技术栈**: Python 3.12 + PyQt6 + SQLite + pywin32 + Pillow + PyInstaller

---

## 最终文件结构

```
G:\1-桌面复制粘贴项目\
├── main.py                  # 应用入口
├── config.py                # 常量配置（窗口尺寸、颜色、路径）
├── database.py              # SQLite 数据库层（CRUD + SHA-256 去重）
├── clipboard_monitor.py     # 剪贴板监听（QTimer 500ms 轮询 + win32clipboard）
├── image_handler.py         # 图片处理（PNG/DIB 解析、缩略图生成、JPEG 缓存）
├── requirements.txt         # 依赖：PyQt6, pywin32, Pillow
├── debug.bat                # 调试启动（显示控制台）
├── start.bat                # 后台启动（pythonw，无控制台）
├── ClipboardHistory.spec    # PyInstaller 打包配置
├── ClipboardHistory_v1.0.zip # 分发包
├── PROJECT_STATUS.md        # 本文档
├── data/
│   ├── clipboard_history.db # SQLite 数据库（运行时自动创建）
│   └── images/              # 剪贴板图片存储
├── dist/
│   └── ClipboardHistory.exe # PyInstaller 打包的独立 EXE（43MB）
├── build/                   # PyInstaller 构建临时文件
└── ui/
    ├── __init__.py
    ├── main_window.py       # 主窗口（无边框、拖拽、缩放、托盘、Toast）
    ├── styles.py            # QSS 样式（浅色/深色磨砂玻璃主题）
    ├── delegates.py         # 列表项自定义绘制（矢量图标 + 缩略图缓存）
    ├── history_list.py      # 历史列表组件（右键菜单 + 双击复制）
    ├── preview_panel.py     # 预览面板（文字/图片）
    └── search_bar.py        # 搜索栏（实时搜索 + × 清除按钮）
```

---

## 设计系统

基于 **ui-ux-pro-max** 设计技能指导，采用 **Glassmorphism + Minimalism + Micro-interactions**：

| 维度 | 取值 |
|------|------|
| 风格 | 磨砂玻璃（多层渲染：渐变底色 + 内边框 + 顶部高光 + 光泽边缘） |
| 强调色 | 靛蓝 `#6C7BFF` rgb(108, 123, 255) |
| 浅色主题 | 蓝白基调 #EBF0FA，半透明卡片，暖灰文字 |
| 深色主题 | 深邃底色 #0A0A0F，低透明度表面，冷白文字 |
| 字体 | Microsoft YaHei / Segoe UI |
| 图标 | QPainter 纯矢量绘制（无 emoji），线性轮廓风格 |
| 圆角 | 14px 窗口 / 10px 卡片 / 8px 按钮 |
| 窗口尺寸 | 260×440（最小 220×220，可自由缩放） |

### 磨砂玻璃实现（paintEvent 多层渲染）

```
第 1 层 — 主背景：rgba 半透明填充 + 描边
第 2 层 — 垂直渐变叠加（蓝白渐变，制造深度感）
第 3 层 — 内边框（模拟玻璃边缘折射）
第 4 层 — 顶部高光条（光源反射）
第 5 层 — 顶部光泽渐变（模拟玻璃表面反光）
```

---

## 核心技术问题及解决方案

### 1. PyQt6 严格类型检查：QPoint vs QPointF

**现象**: `QPainterPath.addEllipse(QPoint(...), r, r)` 崩溃
```
argument 1 has unexpected type 'QPoint'
```

**原因**: PyQt6 对 C++ 类型检查比 PyQt5 更严格，`addEllipse` 要求 `QPointF` 而非 `QPoint`。

**解决**: 所有 QPainterPath 绘制改用 `QPointF`，`addRoundedRect` 使用 `QRectF`。
```python
# 错误
path.addEllipse(QPoint(cx, cy), r, r)
# 正确
path.addEllipse(QPointF(cx, cy), r, r)
```

**影响范围**: `ui/main_window.py`（月亮图标）、`ui/delegates.py`（缩略图裁剪）

---

### 2. QSS 不支持 CSS3 transition 属性

**现象**: 程序启动后闪退，无错误提示。

**原因**: Qt Style Sheets 只支持 CSS2 子集，`transition`、`animation`、`transform` 等 CSS3 属性不被识别。PyQt6 静默报错 `Unknown property transition`，某些环境下直接崩溃。

**解决**: 删除 `ui/styles.py` 中所有 `* { transition: all 150ms ease-out; }` 块。

**教训**: QSS ≠ CSS，动画需要通过 QPropertyAnimation 或 QTimer 实现。

---

### 3. QLinearGradient 构造函数兼容性问题

**现象**: `QLinearGradient(rect.topLeft(), rect.bottomLeft())` 崩溃。

**原因**: `QLinearGradient(QPoint, QPoint)` 重载在某些 PyQt6 版本中存在兼容性问题。

**解决**: 改用坐标参数：
```python
# 错误
gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
# 正确
gradient = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.y() + rect.height())
```

---

### 4. DIB 剪贴板图片解析失败

**现象**: 从浏览器复制图片后无法识别。

**原因**: 原始代码 `dib_data[header_size - 4:]` 从 DIB 数据中错误地截掉了 36 字节（40 字节 BITMAPINFOHEADER 减去 4），导致 BMP 文件头损坏。

**解决**: 不截断 DIB 数据，直接在前面拼接完整的 14 字节 BMP 文件头：
```python
def dib_to_image(dib_data: bytes) -> Image.Image | None:
    import struct
    dib_size = len(dib_data)
    file_size = 14 + dib_size
    pixel_offset = 14 + 40  # file header + BITMAPINFOHEADER
    bmp_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, pixel_offset)
    return Image.open(BytesIO(bmp_header + dib_data))
```

---

### 5. 图片复制检测优先级错误

**现象**: 浏览器中复制图片时，只检测到了文本而非图片。

**原因**: 浏览器同时将图片和文本（alt 文本/URL）放入剪贴板。原代码 `elif` 先检查文本后检查图片，导致图片被跳过。

**解决**: 
- 优先检查 PNG 格式（通过 `RegisterClipboardFormat("image/png")` 注册）
- 再检查 DIB 格式（CF_DIB=8, CF_DIBV5=17）
- 最后检查文本（CF_UNICODETEXT=13）

**文件**: `clipboard_monitor.py`

---

### 6. 历史列表排序反转

**现象**: 最新复制的内容出现在列表最下方，而非最上方。

**原因**: `add_entry()` 用 `insertItem(0, item)` 将新条目插入顶部，但 `load_entries()` 正向遍历数据库返回的 newest-first 结果，导致顺序反转。

**解决**: `load_entries()` 中改为 `reversed(entries)`：
```python
def load_entries(self, entries: list[dict]):
    self.clear()
    for entry in reversed(entries):
        self.add_entry(entry)
```

**文件**: `ui/history_list.py`

---

### 7. QSettings 旧配置残留

**现象**: 修改 `config.py` 中的 `WINDOW_WIDTH`/`WINDOW_HEIGHT` 后，窗口仍然使用旧尺寸。

**原因**: 之前的版本将窗口 geometry（包含位置+尺寸）保存到 QSettings。新版本启动时从注册表读取到旧的 700×400，覆盖了代码中的新默认值。

**解决**: 将 `saveState`/`restoreState` 改为分别保存 `pos` 和 `size` 两个独立键，手动清除旧键。
```python
# 保存
self._settings.setValue("pos", self.pos())
self._settings.setValue("size", self.size())
# 恢复
saved_pos = self._settings.value("pos")
saved_size = self._settings.value("size")
```

**文件**: `ui/main_window.py`

---

### 8. 列表项 sizeHint 为 0 导致不可见

**现象**: 图片条目在列表中高度为 0，完全不可见。

**原因**: `_make_list_item` 方法创建 `QListWidgetItem` 后没有调用 `item.setSizeHint()`。

**解决**: 统一使用 `HistoryListWidget.add_entry()` 方法，该方法在 `insertItem` 前自动设置 `sizeHint`。

---

### 9. 缩略图重复解码性能问题

**现象**: 每次列表重绘都解码 + 缩放缩略图，滚动时卡顿。

**解决**: 
- 添加 `_thumbnail_cache` 字典缓存（最大 120 条，超出后全清）
- 添加 `_font_cache` 字典缓存 QFont 对象
- 缓存键使用 `(thumbnail_bytes, size)` 元组

**文件**: `ui/delegates.py`

---

### 10. PyInstaller 打包 EXE

**问题**: 应用依赖 Python 运行时和多个第三方库，无法直接分享。

**解决**: 
- 使用 PyInstaller 6.20.0 打包为独立 EXE
- `console=False`（无控制台窗口）
- `hiddenimports` 包含 `win32clipboard`、`win32con`、`win32api`、`win32gui`
- 排除不必要的库（tkinter、numpy、pandas 等）以减小体积
- 最终 EXE 大小：43MB（包含完整 Qt6 运行时）

**配置**: `ClipboardHistory.spec`

---

### 11. 暗黑模式菜单项颜色不一致

**问题**: 深色模式下右键菜单选中项颜色与整体靛蓝主题不协调。

**解决**: 深色主题 `QMenu::item:selected` 使用亮靛蓝 `rgb(148, 163, 255)`（基础色 +40），浅色主题使用基础靛蓝 `rgb(108, 123, 255)`。

---

## UI 迭代历史

| 迭代 | 变更 | 用户反馈 |
|------|------|----------|
| 1 | 初始布局：380×520 水平分割 | "太宽了" |
| 2 | 缩小至 260×480 | "高度再低一点" |
| 3 | 改为垂直分割（上下布局），高度降至 400 | "右边区域竖着看很不方便" |
| 4 | 预览面板加蓝色底色区分 | "不太明显，再深一点" |
| 5 | 预览面板加深至 20% 蓝色 | "还是不明显" |
| 6 | 预览面板改为蓝白底 + 蓝色顶部边框 | 最终确认 |
| 7 | 标题字体：12px → 20px → 14px + 顶部内边距 | "往下来一点点" |
| 8 | 选中色：灰色 → 蓝色 55% alpha → 60% alpha | "再深一点" |
| 9 | 列表项字体缩小，文本截断基于宽度而非字符数 | "只能显示两个字" |
| 10 | 添加 Toast 通知（"已复制"/"图片已复制"） | 用户体验提升 |
| 11 | 深色/浅色模式图标：彩色圆圈 → 线性月亮/太阳 | "用线性图标" |
| 12 | 窗口宽度调整：260 → 260（保持），高度 400→440 | 最终尺寸 |

---

## 启动方式

```bash
# 开发调试（显示控制台输出）
debug.bat

# 后台运行（无控制台窗口）
start.bat

# 命令行
python main.py

# 分发给他人
# 解压 ClipboardHistory_v1.0.zip，双击 ClipboardHistory.exe
```

---

## 开发环境

| 组件 | 版本 |
|------|------|
| Windows | 11 Pro (Build 26100) |
| Python | 3.12.10 |
| PyQt6 | 6.11.0 |
| pywin32 | 311 |
| Pillow | 12.2.0 |
| PyInstaller | 6.20.0 |

---

*文档更新: 2026-05-28*
