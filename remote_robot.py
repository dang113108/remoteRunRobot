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
    if resp.poll() == 0:
        return out
    else:
        return err


def git_local_file_diff(project, first, second):
    cmd = "git -C {}/{project} diff --name-only {first} {second}".format(
        LOCAL_PATH,**locals())
    resp = shell_caller(cmd)
    return resp.split("\n")


def git_current_commit(project, branch, remote=False):
    if remote:
        ssh = ssh_connect()
        pre_cmd = "{REMOTE_BASE_PATH}/{project} git pull".format(locals())
        ssh.close()
    else:
        shell_caller(
            "git -C {}/{project} pull && git -C {}/{project} checkout {branch}"
            .format(LOCAL_PATH, LOCAL_PATH, **locals()))
        out = shell_caller("git -C {}/{project} rev-parse HEAD".format(
            LOCAL_PATH, **locals()))
    return "".join(out.split("\n"))


@click.group()
def cli():
    pass


@click.command("test", help="test option")
@click.option("-p", "--project", help="The folder need to run")
@click.option("-b", "--branch", help="The branch need to run")
@click.option("-r",
              "--remote",
              default=None,
              required=False,
              help="The remote need to run")
def test(project, branch, remote):
    first = git_current_commit(project, branch, remote)
    git_local_file_diff(project,first,"b6d77b68b030bd4d38947f3cc7b981f6037c6f1f")
    print(first)


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
