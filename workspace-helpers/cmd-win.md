#### ====== Windows Commands ===== ####

# === delete directory === #
rmdir /s /q FolderName
# === delete file === #
del FileName.txt
# === create directory === #
mkdir NewFolder
# === rename file or folder === #
rename OldName NewName
# === copy file === #
copy source.txt destination.txt
# === copy directory recursively === #
xcopy SourceFolder DestinationFolder /E /I /H
# === move file or directory === #
move source.txt NewFolder\
move OldFolder NewFolder\
# === list directory contents === #
dir
dir /b             # bare format
dir /s             # with subfolders

# === change directory === #
cd FolderName
cd ..              # go up one level
# === clear screen === #
cls
# === show environment variables === #
set
# === set a temporary environment variable === #
set MY_VAR=value
# === show IP configuration === #
ipconfig
# === release & renew IP address === #
ipconfig /release
ipconfig /renew
# === flush DNS cache === #
ipconfig /flushdns
# === check network status === #
ping 8.8.8.8
tracert google.com
netstat -an
# === list running processes === #
tasklist
# === kill a process by name or PID === #
taskkill /IM notepad.exe /F
taskkill /PID 1234 /F
# === open registry editor === #
regedit
# === run a script or program === #
start myscript.bat
start notepad.exe
# === show current user === #
whoami
# === system information === #
systeminfo
# === get help for a command === #
command /?