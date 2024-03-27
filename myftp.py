import socket
import getpass
import random
from libftp import Ftp

def main():
    ftp = Ftp()
    while True:
        line = input("ftp> ").strip()
        if not line:
            continue
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
            else :
                print('Usage: open host name [port]')
        elif command == 'disconnect':
            ftp.disconnect()
        elif command == 'ls':
            if len(args) == 1:
                ftp.ls()
            else:
                ftp.ls(args[1])
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
                ftp.put()
            elif len(args) == 2:
                ftp.put(args[1],args[1])
            else :
                ftp.put(args[1],args[2])
        elif command == 'binary':
            ftp.binary()
        elif command == 'user':
            if len(args) == 1:
                ftp.user()
            elif len(args) == 2:
                ftp.user(args[1])
            elif len(args) ==3 :
                ftp.user(args[1], args[2])
            elif len(args) > 4 :
                print('Usage: user username [password] [account]')
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
                if remote == '':
                    print('Remote file get [ local-file ].')
                    continue
                local = input('Local file ')
                ftp.get(remote,local)
            elif len(args)==2:
                ftp.get(args[1],args[1])
            elif len(args) >=3:
                ftp.get(args[1],args[2])
        else:
            print("Invalid command.")

if  __name__ == '__main__':
    main()