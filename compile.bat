@echo off
rem Compile digsigclt as single-file exe.
rem Requires python >= 3.6 and pyinstaller.

pyinstaller --onefile digsigclt

echo "The compiled *.exe file can be found at:"
echo "dist\dicsigclt.exe"
