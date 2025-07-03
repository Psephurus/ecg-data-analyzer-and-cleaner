# 数据处理

## 打包

```shell
python -m nuitka --standalone --onefile --mingw64 --enable-plugin=tk-inter --include-module=numpy --include-module=scipy --windows-console-mode=disable ecg_analyzer.py
```

```shell
python -m nuitka --standalone --onefile --enable-plugin=tk-inter --enable-plugin=matplotlib --windows-icon-from-ico=icon.ico --windows-console-mode=disable data_selection_app.py
```
