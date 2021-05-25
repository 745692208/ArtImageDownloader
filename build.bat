pyinstaller -F --path=C:\Users\Administrator\AppData\Local\Programs\Python\Python39\Lib\site-packages --hidden-import=you_get.extractors --hidden-import=you_get.cli_wrapper --hidden-import=you_get.processor --hidden-import=you_get.utl -i .\res\icon.ico .\src\MultipleDownloaders.py
@pause
