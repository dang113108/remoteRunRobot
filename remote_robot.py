import click
import paramiko
import re
from env import *


def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP_HOST, 22, USER, PWD)
    return ssh


def ssh_copy(method, localpath, remotepath):
    t = paramiko.Transport((IP_HOST, 22))
    t.connect(username=USER, password=PWD)
    sftp = paramiko.SFTPClient.from_transport(t)
    if method == "get":
        sftp.get(remotepath, localpath)
    elif method == "put":
        sftp.put(localpath, remotepath)
    t.close()


@click.group()
def cli():
    pass


@click.command()
@click.option("robot", help="Remote the robot command by ssh")
@click.option("-c", "--command", help="The command need to run")
def remote_robot(command):
    ssh = ssh_connect()
    stdin, stdout, stderr = ssh.exec_command(command)
    project = re.match(r'(-I) (?P<project>dqa-\w+)').group("project")
    ssh_copy("get", "", "")



if __name__ == "__main__":
    USER = input("User name: ") if USER == "" else USER
    PWD = input("Password: ") if PWD == "" else PWD
    cli()

# ssh.close()

# stdin, stdout, stderr = ssh.exec_command("")
# print(stdout.readlines())

# python dqa-script/exo-robot-runner run -I dqa-exosense -i api \
# -O --suite=request_removal \
# --docker_skip