pyinstaller -y --windowed -F  -i .\res\icon.ico --add-data ".\res\error.mp3;res" --add-data ".\res\bring.mp3;res" .\src\ArtImageDownloader.py
@pause
