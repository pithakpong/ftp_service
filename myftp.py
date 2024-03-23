import socket
import getpass
import random
class Ftp:
    def __init__(self):
        self.connection = False

    def quit(self):
        self.disconnect()

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
    
    def ls(self):
        if not hasattr(self, 'Clientsocket') or not self.connection:
            print("Not connected.")
            return
        self.Clientsocket.sendall(b'PASV\r\n')
        pasv_response = self.Clientsocket.recv(1024).decode()
        data_host, data_port = self.parse_pasv_response(pasv_response)
        with socket.create_connection((data_host, data_port)) as data_socket:
            self.Clientsocket.sendall(b'NLST\r\n')
            dir_response = self.Clientsocket.recv(1024).decode()
            print(dir_response, end='')
            while True:
                data = data_socket.recv(4096)
                if not data:
                    break
                print(data.decode(), end='')
        control_response = self.Clientsocket.recv(1024).decode()
        print(control_response, end='')

    def open(self,host,port=21):
        self.Clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Clientsocket.connect((host,int(port)))
        self.name = host
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.Clientsocket.send(f'OPTS UTF8 ON\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        self.connection = True
        user = input(f'User ({host}:(none)): ')
        self.Clientsocket.send(f'USER {user}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="")
        password = getpass.getpass("Password: ")
        self.Clientsocket.send(f'PASS {password}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        if resp.decode().startswith('530'):
            print('Login failed.')
            return
        print(resp.decode(),end="")
        self.username = user
        self.password = password

    def put(self, file=None,new=None):
        if not hasattr(self, 'Clientsocket') or not self.connection:
            print("Not connected.")
            return
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
        if newname is None:
            newname = input('To name ')
        self.Clientsocket.send(f'RNFR {filename}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="") 
        if not resp.decode().startswith('350'):
            return
        self.Clientsocket.send(f'RNTO {newname}\r\n'.encode())
        resp = self.Clientsocket.recv(1024)
        print(resp.decode(),end="") 

    def user(self,username=None,password=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
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
        self.username = username
        self.password = password
        print(resp.decode(),end="")

def main():
    ftp = Ftp()
    while True:
        line = input("ftp> ").strip()
        args = line.split()
        command = args[0]
        if command == 'quit' or command == 'bye':
            ftp.quit()
            break
        elif command == 'open':
            if len(args) == 1:
                host = input("To ")
                ftp.open(host)
            elif len(args) == 2:
                ftp.open(args[1])
            elif len(args) == 3:
                ftp.open(args[1],args[2])
        elif command == 'disconnect':
            ftp.disconnect()
        elif command == 'ls':
            ftp.ls()
        elif command == 'close':
            ftp.close()
        elif command == 'cd':
            if len(args)>1:
                ftp.cd(args[1])
            else:
                ftp.cd()
        elif command == 'pwd':
            ftp.pwd()
        elif command == 'ascii':
            ftp.ascii()
        elif command == 'put':
            if len(args) == 1:
                file = input('Local file ')
                remote = input('Remote file ')
                ftp.put(file,remote)
            elif len(args) == 2:
                ftp.put(args[1],args[1])
            else :
                ftp.put(args[1],args[2])
            ftp.put(args[1])
        elif command == 'binary':
            ftp.binary()
        elif command == 'user':
            if len(args) == 1:
                ftp.user()
            elif len(args) == 2:
                ftp.user(args[1])
            else :
                ftp.user(args[1], args[2])
        elif command == 'delete':
            if len(args) == 1:
                ftp.delete()
            else :
                ftp.delete(args[1])
        elif command == 'rename':
            if len(args) == 1:
                ftp.rename()
            elif len(args) == 2:
                ftp.rename(args[1])
            else :
                ftp.rename(args[1], args[2])
        elif command == 'get':
            if len(args)==1:
                remote = input('Remote file ')
                local = input('Local file ')
                ftp.get(remote,local)
            elif len(args)==2:
                ftp.get(args[1],args[2])
        else:
            print("Invalid command.")
if  __name__ == '__main__':
    main()