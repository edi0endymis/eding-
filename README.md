【最新】最直接的办法：
点击dist文件夹里的.exe文件即可直接使用，这个文件可以拖拽到桌面，在哪无所谓


运行方法1：
1，打开文件夹
2，右键，用终端打开
3，输入：python tool_app.py
>该方法每次打开都要这么操作

运行方法2：
1，打开文件夹
2，右键，用终端打开
3，输入：pip install pyinstaller
4，输入：pyinstaller --onefile --noconsole tool_app.py
>在生成的 dist 文件夹中找到 tool_app.exe，可以直接双击运行，无需Python环境.
>该方法只需要操作一次以后直接打开.exe文件即可


