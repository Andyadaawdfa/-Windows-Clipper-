
● 一个 Windows 桌面剪贴板历史记录工具。

  干什么的：你复制过的文字和图片，它都会自动记下来。随时可以翻出来查看、搜索、重新复制。

  怎么跑的：后台每 0.5 秒检查一次剪贴板，发现新内容就存进 SQLite 数据库。窗口关掉后仍然在系统托盘运行。

  架构四层：
  - clipboard_monitor.py → 剪贴板监听层（win32 API 轮询）
  - database.py → 存储层（SQLite，SHA-256 去重）
  - image_handler.py → 图片处理层（DIB/PNG 解析 → 缩略图）
  - ui/ → 界面层（PyQt6 无边框窗口 + 磨砂玻璃 + 托盘）

  启动方式：双击 ClipboardHistory.exe 就行，不需要装任何东西。
