import dns.resolver
import subprocess
import sys

def stringToFile(fileName, contentsRaw):
    contents = str(contentsRaw)
    with open(fileName, "w+") as output_file:
        output_file.write(contents)
        output_file.close()

def fileToString(fileName) :
    fileContents = ""
    with open(fileName, 'r') as myfile:
        fileContents = myfile.read()
    return str(fileContents)

def parseArgs(allArgs):
    adict = {}
    adict["v"] = False
    i = 1
    for arg in allArgs:
        if arg[0] == "-":
            try:
                adict[str(arg[1:]).lower()] = allArgs[i]
            except IndexError:
                adict[arg[1:]] = True
            except Exception as e:
                print("Couldn't parse {}.\n{}", arg, e)
                sys.exit(3)
        i = i + 1
    return adict

def sh(command, verbose=False):
    commandList = command.split(" ")
    if verbose:
        print("{}".format(command))
        print("{}".format(commandList))
    commandOutputRaw = subprocess.run(commandList, capture_output=True, text=True).stdout
    if verbose:
        print("{}".format(commandOutputRaw))
    return commandOutputRaw


