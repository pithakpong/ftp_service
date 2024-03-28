import socket
import getpass
import random
class Ftp:
    def __init__(self):
        self.connection = False
        self.useable = False

    def quit(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            return
        self.Clientsocket.send(f'QUIT\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.connection = False
        self.useable = False
        self.Clientsocket.close()

    def bye(self):
        self.quit()

    def binary(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'TYPE I\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")

    def ascii(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'TYPE A\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")

    def cd(self,path=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        if path is None :
            path = input("Remote directory ")
        self.Clientsocket.send(f'CWD {path}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")

    def close(self):
        self.disconnect()

    def delete(self,file=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        if file is None:
            file = input('Remote file ')
        self.Clientsocket.send(f'DELE {file}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")

    def disconnect(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'QUIT\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.connection = False
        self.useable = False
        self.Clientsocket.close()

    def get(self, filename, local_file=None):
        if not hasattr(self, 'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        number = random.randint(0,65535)
        ipaddr = socket.gethostbyname(socket.gethostname())+f".{number//256}.{number%256}"
        ipaddr = ipaddr.replace('.',',')
        
        self.Clientsocket.send(f'PORT {ipaddr}\r\n'.encode())
        resp = self.Clientsocket.recv(1024).decode()
        print(resp,end='')

        self.Clientsocket.sendall(b'PASV\r\n')
        pasv_response = self.Clientsocket.recv(1024).decode()
        data_host, data_port = self.parse_pasv_response(pasv_response)
        
        self.Clientsocket.sendall(f'RETR {filename}\r\n'.encode())
        resp = self.Clientsocket.recv(1024).decode()
        print(resp,end='')
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.settimeout(10)
        data_socket.connect((data_host, data_port))
        with open(local_file, 'wb') as lf:
            while True:
                try:
                    data = data_socket.recv(1024)
                    if not data:
                        break
                    lf.write(data)
                except socket.timeout:
                    print("Data connection timed out.")
                    break
                except Exception as e:
                    print("An error occurred:", e)
                    break
        data_socket.close()
        resp = self.Clientsocket.recv(1024).decode()
        print(resp,end='')


    def send_command(self,sock,command):
        sock.sendall(command.encode()+b'\r\n')
        data = b''
        while True:
            response = sock.recv(4096)
            if not response:
                break
            data += response
            if response[-2:] == b'\r\n':
                break
        return data.decode()
    
    def parse_pasv_response(self,response):
        parts = response.split('(')[1].split(')')[0].split(',')
        host = '.'.join(parts[:4])
        port = int(parts[4])*256 + int(parts[5])
        return host, port
    
    def ls(self,file=''):
        if not hasattr(self, 'Clientsocket') or not self.connection:
            print("Not connected.")
            return
        number = random.randint(0,65535)
        ipaddr = socket.gethostbyname(socket.gethostname())+f".{number//256}.{number%256}"
        ipaddr = ipaddr.replace('.',',')
        
        self.Clientsocket.send(f'PORT {ipaddr}\r\n'.encode())
        resp = self.Clientsocket.recv(1024).decode()
        print(resp,end='')
        self.Clientsocket.sendall(b'PASV\r\n')
        pasv_response = self.Clientsocket.recv(1024).decode()
        data_host, data_port = self.parse_pasv_response(pasv_response)
        with socket.create_connection((data_host, data_port)) as data_socket:
            self.Clientsocket.sendall((f'NLST {file}\r\n').encode())
            dir_response = self.Clientsocket.recv(1024).decode()
            print(dir_response, end='')
            if dir_response.startswith('5'):
                return
            while True:
                data = data_socket.recv(4096)
                if not data:
                    break
                print(data.decode(), end='')
        control_response = self.Clientsocket.recv(1024).decode()
        print(control_response, end='')

    def open(self,host,port=21):
        if (hasattr(self, 'Clientsocket') and self.connection) or self.useable:
            print(f"Already connected to {self.name}, use disconnect first.")
            return
        if host == '':
            print("Usage: open host name [port]")
            return
        print(f'Connected to {host}.')
        self.Clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Clientsocket.connect((host,int(port)))
        self.Clientsocket.settimeout(1)
        self.name = host
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.Clientsocket.send(f'OPTS UTF8 ON\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.useable = True
        user = input(f'User ({host}:(none)): ')
        self.Clientsocket.send(f'USER {user}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        if resp.decode().startswith('5'):
            print('Login failed.')
            return
        password = getpass.getpass("Password: ")
        self.Clientsocket.send(f'PASS {password}\r\n'.encode())
        last_response = b''
        while True:
            try:
                resp = self.Clientsocket.recv(1024)
                if not resp:
                    break
                last_response = resp
                print(last_response.decode(), end="")
            except socket.timeout:
                break
        if last_response.decode().startswith('5'):
            print('Login failed.')
            return
        else:
            self.connection = True
        # print(resp.decode(),end="")
        self.username = user
        self.password = password

    def put(self, file=None,new=None):
        if not hasattr(self, 'Clientsocket') or not self.connection:
            print("Not connected.")
            return
        if file is None and new is None:
            file = input('Local file ')
            new = input('Remote file ')
        number = random.randint(0,65535)
        ipaddr = socket.gethostbyname(socket.gethostname())+f".{number//256}.{number%256}"
        ipaddr = ipaddr.replace('.',',')
        self.Clientsocket.send(f'PORT {ipaddr}\r\n'.encode())
        port_status = self.Clientsocket.recv(1024)
        print(port_status.decode(),end="")
        with open(file,'rb') as f:
            try:

                self.Clientsocket.sendall(b'PASV\r\n')
                response = self.Clientsocket.recv(1024).decode()
                port_start = response.find('(') + 1
                port_end = response.find(')')
                port_str = response[port_start:port_end].split(',')
                data_port = int(port_str[-2]) * 256 + int(port_str[-1])
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.connect((socket.gethostbyname(self.name), data_port))
                self.Clientsocket.sendall((f'STOR {new}\r\n').encode())
                response = self.Clientsocket.recv(4096).decode()
                print(response,end='')
                if not response.startswith('150'):
                    return
                data = f.read(4096)
                while data:
                    data_socket.sendall(data)
                    data = f.read(4096)
            finally:
                data_socket.close()
            response = self.Clientsocket.recv(1024)
            print(response.decode(),end='')
    def pwd(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'XPWD\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")

    def rename(self,filename=None,newname=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        if filename is None:
            filename = input('From name ')
        if filename == '':
            print('rename from-name to-name.')
            return
        if newname is None:
            newname = input('To name ')
        if newname == '':
            print('rename from-name to-name.')
            return
        self.Clientsocket.send(f'RNFR {filename}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="") 
        if not resp.decode().startswith('350') or resp.decode().startswith('5'):
            return
        self.Clientsocket.send(f'RNTO {newname}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="") 

    def user(self,username=None,password=None):
        if not hasattr(self,'Clientsocket') or self.useable == False:
            print("Not connected.")
            return
        if username is None:
            username = input('Username ')
        self.Clientsocket.send(f'User {username}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        if not resp.decode().startswith('331'):
            print('Login failed.')
            return
        if password is None:
            password = getpass.getpass("Password: ")
        self.Clientsocket.send(f'PASS {password}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        if resp.decode().startswith('5'):
            print('Login failed.')
            return
        else:
            self.connection = True
        self.username = username
        self.password = password
        print(resp.decode(),end="")