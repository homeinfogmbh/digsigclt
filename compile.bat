@echo off
rem Compile digsigclt as single-file exe.
rem Requires python >= 3.4 and pyinstaller.

pyinstaller --onefile files\digsigclt

echo "The compiled *.exe file can be found at:"
echo "dist\digsigclt.exe"

