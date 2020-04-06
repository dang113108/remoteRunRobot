import click
import paramiko
import re
import shlex
import subprocess
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


def shell_caller(cmd):
    resp = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding="utf-8")
    out, err = resp.communicate()
    return out if resp.poll() == 0 else err


def ssh_shell_caller(cmd):
    try:
        ssh = ssh_connect()
        stdin, stdout, stderr = ssh.exec_command(cmd)
        return stdout.read().decode() if stdout.channel.recv_exit_status() == 0 else stderr.read().decode()
    finally:
        ssh.close()


def git_local_file_diff(project, first, second):
    cmd = "git -C {}/{project} diff --name-only {first} {second}".format(
        LOCAL_PATH, **locals())
    resp = shell_caller(cmd)
    return list(filter(None, resp.split("\n")))


def git_current_commit(project, branch, remote=False):
    if remote:
        out = ssh_shell_caller("git -C {}/{project} pull && git -C {}/{project} checkout {branch}".format(
            REMOTE_BASE_PATH, REMOTE_BASE_PATH, LOCAL_PATH, **locals()))
        out = ssh_shell_caller("git -C {}/{project} rev-parse HEAD".format(
            REMOTE_BASE_PATH, **locals()))
        commit = out
    else:
        shell_caller(
            "git -C {}/{project} pull && git -C {}/{project} checkout {branch}"
            .format(LOCAL_PATH, LOCAL_PATH, **locals()))
        out = shell_caller("git -C {}/{project} rev-parse HEAD".format(
            LOCAL_PATH, **locals()))
        commit = "".join(out.split("\n"))
    return commit


@click.group()
def cli():
    pass


@click.command("test", help="test option")
@click.option("-p", "--project", help="The folder need to run")
@click.option("-b", "--branch", help="The branch need to run")
def test(project, branch):
    first = git_current_commit(project, branch)
    second = git_current_commit(project, branch, remote=True)
    resp = git_local_file_diff(project, first, second)
    print(resp)


@click.command("robot", help="Remote the robot command by ssh")
@click.option("-c", "--command", help="The command need to run")
def remote_robot(command):
    ssh = ssh_connect()
    stdin, stdout, stderr = ssh.exec_command(command)
    project = re.match(r'(-I) (?P<project>dqa-\w+)', stdout).group("project")
    ssh_copy("get", "", "")


cli.add_command(test)
cli.add_command(remote_robot)

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

# p=subprocess.Popen("dir", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# (stdoutput,erroutput) = p.communicate()

# &&
