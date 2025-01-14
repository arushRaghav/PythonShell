import sys
import os
import shlex
import subprocess

def check_if_known(cmd):
    # to work with system varriables
    pathList = os.environ.get('PATH').split(':')
    for path in pathList:
        if os.path.exists(path):
            # now get the list of all files in the given path
            lis = os.listdir(path)
            for el in lis:
                if os.path.isfile(os.path.join(path,el)):
                    if(os.path.splitext(el)[0] == cmd):
                        return [path,el]
    
    return False


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().strip()
        output = ""
        err=""
        fileName = None
        redir = None

        splitCommand = shlex.split(command, posix=True) 
        # posix true ensures that we handle both single and double qoutes better, returns list

        for i in range(0,len(splitCommand)-1):
            if splitCommand[i] in [">","1>","2>","1>>",">>","2>>"]:
                redir = splitCommand[i]
                fileName = splitCommand[i+1]
                splitCommand.remove(splitCommand[i])
                splitCommand.remove(splitCommand[i])
                break

        if len(splitCommand) == 0:
            continue

        # to exit code
        if splitCommand[0] == "exit":
            # sys.exit() to terminate program with status code 0
            # sys.exit(1) to terminate porgram with status code 1 to indicate error
            if len(splitCommand)>1 and isinstance(splitCommand[1],int):
                sys.exit(splitCommand[1])
            sys.exit()

        #  to use echo
        if splitCommand[0] == "echo":
            output = " ".join(splitCommand[1:])
        
        # to use type
        elif splitCommand[0] == "type":
            knowCommand = ['exit','type','echo','pwd','cd']
            cmd_path = None

            if len(splitCommand) > 1:

                path = check_if_known(splitCommand[1])
                if(path):
                    cmd_path = os.path.join(path[0],path[1])

                if splitCommand[1] in knowCommand:
                    output = splitCommand[1] + " is a shell builtin"

                elif cmd_path:
                    output = splitCommand[1]+" is "+cmd_path

                else:
                    output = splitCommand[1]+": not found"
            
            else:
                err = "Invalid syntax, type needs atleast 1 argument"
        
        # handle pwd
        elif splitCommand[0] == "pwd":
            output = os.getcwd()

        # handle cd
        elif splitCommand[0] == "cd":
            try:
                files = splitCommand[1].split('/')

                #to handle ~
                if files[0] == '~':
                    path = None
                    for file in files:
                        if file == '~':
                            path = os.path.expanduser("~")
                        else:
                            path = os.path.join(path,file)
                    os.chdir(path)
                else:
                    # handle absolute and relative paths
                    os.chdir(splitCommand[1])
            
            # will change the error messages later on
            except FileNotFoundError:
                err = "cd: "+splitCommand[1]+ ": No such file found"
            except PermissionError:
                err = "Permission denied"
            except NotADirectoryError:
                err = "cd: "+splitCommand[1]+ ": No such directory found"
            except Exception as e:
                err = "error: " + e

        # executing commands
        elif check_if_known(splitCommand[0]):
            # os.system(command.strip())
            res = subprocess.run(splitCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text= True)
            output = res.stdout.rstrip()
            err = res.stderr.rstrip()
        else:
            err = command+": command not found"

        if redir and fileName:
            if redir in ['>','1>','2>']:
                with open(fileName,'w') as file:
                    if redir in ['>','1>']:
                        file.write(output)
                        if output:
                            file.write('\n')
                    else:
                        file.write(err)
                        if err:
                            file.write('\n')
            elif redir in ['>>','1>>']:
                with open(fileName,'a') as file:
                    file.write(output)
                    if output:
                        file.write('\n')
            elif redir in ['2>>']:
                with open(fileName,'a') as file:
                    file.write(err)
                    if err:
                        file.write('\n')
        elif output:
            print(output)
        elif err:
            print(err)

        if output and redir in ['2>','2>>']:
            print(output)
        if err and redir in ['>','1>','>>','1>>']:
            print(err)

if __name__ == "__main__":
    main()
