import socket
import getpass
import random
import time
class Ftp:
    def __init__(self):
        self.connection = False
        self.useable = False

    def quit(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            return
        self.Clientsocket.send(f'QUIT\r\n'.encode())
        self.receive_all(self.Clientsocket)
        self.connection = False
        self.useable = False
        self.Clientsocket.close()
    
    def get_open_port(self):
        tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_sock.bind(('', 0))
        port = tmp_sock.getsockname()[1]
        tmp_sock.close()
        return port

    def receive_all(self, sock, buff_size=4096, is_data=False, show=True):
        all_data = b''
        while True:
            data = sock.recv(buff_size)
            all_data += data

            if data == b'':
                break
            elif len(data) < buff_size:
                new_resp_list = [d for d in data.split(b'\r\n') if d != b'']

                if len(new_resp_list[-1]) >= 4 and not is_data:
                    last_resp = new_resp_list[-1].decode()
                    if last_resp[0:3].isnumeric() and last_resp[3] == ' ':
                        break
        
        if show:
            all_data = all_data.replace(b'\r\n\r\n', b'\r\n')
            print(all_data.decode(), end='')
        return all_data,last_resp

    def bye(self):
        self.quit()

    def binary(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'TYPE I\r\n'.encode())
        self.receive_all(self.Clientsocket)

    def ascii(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'TYPE A\r\n'.encode())
        self.receive_all(self.Clientsocket)

    def cd(self,path=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        if path is None :
            path = input("Remote directory ")
        self.Clientsocket.send(f'CWD {path}\r\n'.encode())
        self.receive_all(self.Clientsocket)

    def close(self):
        self.disconnect()

    def delete(self,file=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        if file is None:
            file = input('Remote file ')
        self.Clientsocket.send(f'DELE {file}\r\n'.encode())
        self.receive_all(self.Clientsocket)

    def disconnect(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'QUIT\r\n'.encode())
        self.receive_all(self.Clientsocket)
        self.connection = False
        self.useable = False
        self.Clientsocket.close()

    def get(self, filename, local_file=None):
        if not hasattr(self, 'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        port = self.get_open_port()
        local_ip = '127.0.0.1' if self.name == '127.0.0.1' else socket.gethostbyname(socket.gethostname())
        ip = (str(local_ip) + f".{port // 256}.{port % 256}").replace(".", ",")
        self.Clientsocket.send(f'PORT {ip}\r\n'.encode())
        self.receive_all(self.Clientsocket)
        byte = 0
        s_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as D_SOCKET :
            with open(local_file,'wb') as lf:

                D_SOCKET.bind((local_ip, port))
                D_SOCKET.listen(1)
                self.Clientsocket.send(f"RETR {filename}\r\n".encode())
                self.receive_all(self.Clientsocket)
                conn, _ = D_SOCKET.accept()
                all,_ = self.receive_all(conn,show=False)
                lf.write(all)
                byte += len(all)
                total = time.time() - s_time
                conn.close()
                D_SOCKET.close()
        self.receive_all(self.Clientsocket)
        print(f"ftp: {byte} bytes received in {total:.2f}Seconds {(byte) / total if not total == 0 else 0.000000001  :.2f}bytes/sec.")


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
    
    def ls(self, folder="") :
        if not hasattr(self, 'Clientsocket') or not self.connection:
            print("Not connected.")
            return
        port = self.get_open_port()
        local_ip = '127.0.0.1' if self.name == '127.0.0.1' else socket.gethostbyname(socket.gethostname())
        ip = (str(local_ip) + f".{port // 256}.{port % 256}").replace(".", ",")
        self.Clientsocket.send(f'PORT {ip}\r\n'.encode())
        self.receive_all(self.Clientsocket)
        byte = 0
        s_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as D_SOCKET :
            D_SOCKET.bind((local_ip, port))
            D_SOCKET.listen(1)
            self.Clientsocket.send(f"NLST {folder}\r\n".encode())
            self.receive_all(self.Clientsocket)
            conn, _ = D_SOCKET.accept()
            all,_ = self.receive_all(conn)
            total = time.time() - s_time
            byte += len(all)
            conn.close()
            D_SOCKET.close()
        self.receive_all(self.Clientsocket)
        print(f"ftp: {byte + 3} bytes received in {total:.2f}Seconds {(byte + 3) / total if not total == 0 else 0.000000001  :.2f}bytes/sec.")

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
        self.name = host
        self.receive_all(self.Clientsocket)
        self.Clientsocket.send(f'OPTS UTF8 ON\r\n'.encode())
        self.receive_all(self.Clientsocket)
        self.useable = True
        user = input(f'User ({host}:(none)): ')
        self.Clientsocket.send(f'USER {user}\r\n'.encode())
        _,last = self.receive_all(self.Clientsocket)
        if last.startswith('5') or last.startswith('4'):
            print('Login failed.')
            return
        password = getpass.getpass("Password: ")
        self.Clientsocket.send(f'PASS {password}\r\n'.encode())
        _,last = self.receive_all(self.Clientsocket)
        if last.startswith('5') or last.startswith('4'):
            print('Login failed.')
            return
        else:
            self.connection = True
        self.username = user
        self.password = password

    def put(self, file=None,new=None):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        port = self.get_open_port()
        local_ip = '127.0.0.1' if self.name == '127.0.0.1' else socket.gethostbyname(socket.gethostname())
        ip = (str(local_ip) + f".{port // 256}.{port % 256}").replace(".", ",")
        self.Clientsocket.send(f'PORT {ip}\r\n'.encode())
        self.receive_all(self.Clientsocket)
        byte = 0
        s_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as D_SOCKET :
            D_SOCKET.bind((local_ip, port))
            D_SOCKET.listen(1)
            self.Clientsocket.send(f"STOR {new}\r\n".encode())
            _,res = self.receive_all(self.Clientsocket)
            if res== "" or not res.startswith('150'): return
            conn, _ = D_SOCKET.accept()
            D_SOCKET.settimeout(10)
            with open(file, "rb") as localfile :
                while True :
                    try :
                        data = localfile.read(4096)
                        conn.sendall(data)
                        if data == b'' : localfile.close(); break
                        byte+=len(data)
                    except socket.timeout :
                        print("Data connection timed out.")
                        break
                    except Exception as error :
                        print("An error occurred:", error)
                        break
            total = time.time()-s_time
            conn.close()
            D_SOCKET.close()
        self.receive_all(self.Clientsocket)
        print(f"ftp: {byte} bytes received in {total:.2f}Seconds {(byte) / total if not total == 0 else 0.000000001  :.2f}bytes/sec.")

    def pwd(self):
        if not hasattr(self,'Clientsocket') or self.connection == False:
            print("Not connected.")
            return
        self.Clientsocket.send(f'XPWD\r\n'.encode())
        self.receive_all(self.Clientsocket)

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
        _,last = self.receive_all(self.Clientsocket)
        if not last.startswith('350') or last.startswith('5'):
            return
        self.Clientsocket.send(f'RNTO {newname}\r\n'.encode())
        self.receive_all(self.Clientsocket)

    def user(self,username=None,password=None,warn=False):
        if not hasattr(self,'Clientsocket') or self.useable == False:
            print("Not connected.")
            return
        if warn:
            print('Usage: user username [password] [account]')
            return
        if username is None:
            username = input('Username ')
        self.Clientsocket.send(f'User {username}\r\n'.encode())
        _,last = self.receive_all(self.Clientsocket)
        if not last.startswith('331'):
            if not(last.startswith('4') or last.startswith('5')):
                print('Login failed.')
            return
        if password is None:
            password = getpass.getpass("Password: ")
        self.Clientsocket.send(f'PASS {password}\r\n'.encode())
        _,last = self.receive_all(self.Clientsocket)
        if last.startswith('5') or last.startswith('4'):
            print('Login failed.')
            return
        else:
            self.connection = True
        self.username = username
        self.password = password