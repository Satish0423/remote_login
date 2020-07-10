import argparse
import sys
import os
sudo pip3 install paramiko
import paramiko
pip3 install scp
import scp


class RemoteLogin(object):
    """This is a class for connect remote device."""

    def __init__(self, ip, port, user, password, key):
        """
        The constructor for Connecting remote device.

        :param ip: Remote device SSH ip address.
        :param port: Remote device SSH port number.
        :param user: Remote device SSH user name.
        :param password: Remote device SSH key passphrase.
        :param key: Remote device SSH key file.
        """
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.key = key
        self.ssh_client = None
        self.scp = None

    def connect(self):
        """
        The function to connect remote device.

        :return: Establish a connection between Local and Remote device
        """
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname = self.ip,
                                port=self.port,
                                username=self.user,
                                password=self.password,
                                key_filename=self.key)
        self.scp = scp.SCPClient(self.ssh_client.get_transport())

    def execute_command(self, command: str):
        """
        The function to execute command in remote device.

        :param command: The command to execute in remote device.
        :return: This function returns Output of command
        """
        _, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout, stderr

    def upload(self, local_path: str, remote_path: str):
        """
        The function upload File/Folder from Local machine to Remote device.

        :param local_path: The file to be upload.
        :param remote_path: Remote path for which location you want upload file/folder.
        :return: This function returns upload file to remote device.
        """
        
        self.scp.put(local_path, recursive=True, remote_path=remote_path)

    def download(self, remote_path: str, local_path: str):
        """
        The function download file from remote device to local machine.

        :param remote_path: The file to be download.
        :param local_path: Path for which location you want download fie/folder.
        :return: This function returns download file from remote device.
        """
        self.scp.get(remote_path, local_path=local_path, recursive=True)


def handler_run(args: list):
    """ The function to establish connection and execute commands """
    remote_login = RemoteLogin(ip=args.target_ip_address,
                               port=args.port_number,
                               user=args.user_name,
                               password=args.password,
                               key=args.ssh_key_file)
    remote_login.connect()
    stdout, stderr = remote_login.execute_command(args.command)
    if stdout:
        for line in stdout:
            print(line)
    if stderr:
        for line in stderr:
            print(line)


def handler_upload(args: list):
    """ The Function to establish connection and upload file to remote device"""
    remote_login = RemoteLogin(ip=args.target_ip_address,
                               port=args.port_number,
                               user=args.user_name,
                               password=args.password,
                               key=args.ssh_key_file)
    remote_login.connect()
    remote_login.upload(args.upload, args.destination_path)
    print(f'Uploaded {args.upload} to {args.destination_path}')


def handler_download(args: list):
    remote_login = RemoteLogin(ip=args.target_ip_address,
                               port=args.port_number,
                               user=args.user_name,
                               password=args.password,
                               key=args.ssh_key_file)
    remote_login.connect()
    remote_login.download(args.download, args.local_path)
    print(f'Download {args.download} to {args.local_path}')


def parse_input_args(args: list) -> argparse.Namespace:
    """
    function passing arguments
    """
    parser = argparse.ArgumentParser(description="Remote login to processor.")
    parser.add_argument("-k", "--ssh_key_file", required=True, type=str, help="Device ssh key")
    parser.add_argument("-t", "--target_ip_address", required=True, type=str, help="Target device ip address")
    parser.add_argument("-p", "--port_number", required=False, default=22, type=int, help="Device SSH port number")
    parser.add_argument("-u", "--user_name", required=False, default="", type=str, help="Device SSH user name")
    parser.add_argument("-ps", "--password", required=False, default="", type=str,
                        help="Device SSH key passphrase")
    parser.add_argument("-l", "--local_path", required=False, default="",
                        type=str, help="Local machine source path")
    parser.add_argument("-d", "--destination_path", required=False, default="",
                        type=str, help="Remote device path")
    parser.add_argument("-i", "--connected_interface", required=False, default="",
                        type=str, help="Remote device connected interface name")

    subparsers = parser.add_subparsers()
    parser_run = subparsers.add_parser('run', help=f"Run command on remote device")
    parser_upload = subparsers.add_parser('upload', help=f"Upload file/folder to remote device")
    parser_download = subparsers.add_parser('download', help=f"Download file/folder from remote device")
    parser_run.set_defaults(func=handler_run)
    parser_upload.set_defaults(func=handler_upload)
    parser_download.set_defaults(func=handler_download)

    parser_run.add_argument('-C', '--command', required=True, type=str,
                            help=f'The command to execute on the remote device.')
    parser_upload.add_argument('-U', '--upload', required=True, type=str,
                               help=f'File/Folder to upload to the remote device.')
    parser_download.add_argument('-D', '--download', required=True, type=str,
                                 help=f'File/Folder to download from the remote device.')
    return parser.parse_args(args)


def main():
    """" Process input arguments """
    args = parse_input_args(sys.argv[1:])
    try:
        args.func(args)
    except AttributeError:
        raise RuntimeError("Invalid input, check usage!!")


"""Script start point"""
if __name__ == "__main__":
    main()
