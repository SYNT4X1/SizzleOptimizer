#=========
# IMPORTS
#=========
from rich import print as rprint  # rich is a rich text library allotting colorful typescript
from rich.tree import Tree  # useful for outputting the current directory structure
from rich.progress import Progress # a progress bar object
from rich.console import Console # a console to print to. propietary. print() doesn't work with rich

from os.path import exists, isfile, isdir  # exists check if a directory exists for the filesystem
from os import path, listdir
import os

import subprocess

#==========


# custom errors for error stuff
class FileTokenError(Exception):
    pass

class RangeValueError(Exception):
    pass


# OMG ACTUAL CODE
class Optimizer:


    # grabs the argument range values from a specifc line assuming it's 
    # formatted like the [ARG] token line
    def getArgumentRanges(self, optLine):
        lowerRangeNumber = int(optLine.strip('[ARG] ').split(':')[1].split('-')[0])
        upperRangeNumber = int(optLine.strip('[ARG] ').split(':')[1].split('-')[1].split(';')[0])
        return tuple((lowerRangeNumber,upperRangeNumber))


    # function to check the .opt file for syntax errors and invalid values
    # used as a sanity check before storing the values from the file to 
    # the algorithm
    def checkOpt(self):
        
        fileTokenCount = 0
        with Progress() as progress:  # iterator for the progress bar

            with open(self.optFileDir, "r") as file:  # to open the actual file

                lines = file.readlines()  # reads file for line count for the progress bar

                # adds task to the progress bar to keep track of
                task = progress.add_task("[b green]Checking Optfile Validity[/]", total=len(lines)) 
                
                for line in lines:
                    
                    if "[FILE]" in line:  # Checking for tokens and raising errors on issues
                        fileTokenCount += 1
                        if fileTokenCount > 1:
                            raise FileTokenError(".opt file contains more [FILE] tokens than acceptable...")
                        else:
                            pass

                    elif "[ARG]" in line:
                        lower, upper = self.getArgumentRanges(line)
                        if upper < lower:
                            raise RangeValueError("range values are impossible to iterate upon, typically if the lower value bounds greater than the upper value...")
                        else:
                            pass     
                    
                    progress.update(task, advance=1)  # Update the progress
        
        return True


    # Function used to set the options. Called after the file has been checked
    def setOpt(self):
        with open(self.optFileDir, "r") as file:
            for line in file:
                # check for [FILE] token
                if "[FILE]" in line:

                    # I used strip() to strip the token from the line 
                    # then split() with the ; which is at the end of the line
                    # this creates a list of the stripped value and everything
                    # to the right of the line. Selecting the first value only
                    # returns the string value of the name. [1] would result
                    # in selecting everything to the right of the ; which is
                    # acting as the end line delimiter in the files syntax

                    self.testFileDir = line.strip('[FILE] ').split(';')[0]

                # check for [ARG] tokens
                elif "[ARG]" in line:

                    # The character stripping and splitting are very much ugly
                    # but this is the only way I could think of getting the
                    # numbers.

                    argumentNumber = int(line.strip('[ARG] ').split(':')[0].split(';')[0])
                    lowerRangeNumber = self.getArgumentRanges(line)[0]
                    upperRangeNumber = self.getArgumentRanges(line)[1]

                    self.testRanges[argumentNumber] = tuple((lowerRangeNumber, upperRangeNumber))

    # actual optimization process that goes through all possible parameters
    def optimitize(self):
        numberStart = [] # list for the beginning of the range
        numberEnd = [] # list for the end of the range

        # populate lists
        for individualRange in self.testRanges:
            numberStart.append(int(self.testRanges[individualRange][0]))
            numberEnd.append(int(self.testRanges[individualRange][1]))

        done = False # wether or not we're done

        # do work
        while not done:
            arguments = '' # this is a string to concat the arguments to for the subprocess call later

            # check if we're done
            if numberStart == numberEnd:
                done = True

            else:
                for index in range(0,len(numberStart)):
                    if numberStart[index] == numberEnd[index]:
                        pass
                    else:
                        numberStart[index] += 1
                        break
            
            # concat of elements to string for the subprocess call
            for element in numberStart:
                arguments += str(element) + " "

            # subprocess.run(f'python3 {self.testFileDir} {arguments}')
            print(f'python3 {self.testFileDir} {arguments}')

    # Optimizers constructor
    def __init__(self, fileDir):
        self.optFileDir = fileDir
        self.testRanges = {}
        if self.checkOpt():
            self.setOpt()
            self.optimitize()


class ui:


    # creation of the terminal menu
    def menu(self):
        
        # instances a console in order to print in color
        console = Console(width=100)
        
        # prints the flag in ./rsrc/flag.txt
        console.print(f'[b orange1]{self.getFlag()}[/]')

        console.print("\n[b blue]Hello![/]\n")
        console.print(ui.currentDirList())
         
        print("\n===\n")

        console.print("[b purple]example input: ./OptFiles/test.opt[/] \n")

        console.print("[b purple]you can also type 'exit' to quit.[/] \n")

        optFileSelected = False

        while not optFileSelected:
            # grabbing input of the optfile path
            userin = console.input("[b blue]Please Enter a Valid Optfile Selection[/] [b red](by path)[/]: ")
            # checks if file exists and if it does, produces the optimizer
            if exists(userin):
                optFileSelected = True
                console.print('[b green]Found it! [/]')
                bestOptimizer3000 = Optimizer(userin)
            
            # for fun if the user enters nothing
            elif userin == "":
                console.print("[b red]why not give us something to look for? huh?[/]")

            # a way for the user to exit the console
            elif userin.lower() == "exit":
                console.print("[b red]bye![/]")
                exit()

            # if all else fails ask them to try again
            else:
                console.print("[b red]Hmm...We can't seem to find it! Please try again![/]")


    # Ui element for listing the directory elements
    def currentDirList():
        directoryView = Tree('Here\'s what we see! 0-0')
        
        # iterate through the files
        for filename in listdir("./"):
            filepath = path.join("", filename)
            
            # get rid of the script file
            if filename == "Optimizer.py":
                pass
            
            # make file elements green
            elif isfile(filepath):
                directoryView.add(f"[b green]{filepath}[/]")
            
            # make folder elements red
            elif isdir(filepath):
                subTree = Tree(f"[b red]{filepath}[/]")
                
                # make file elements green and add to subtree
                for filename in listdir(filepath):
                    file = path.join("",filename)
                    subTree.add(f"[b green]{file}[/]")
                
                # add subtree to the main directory view
                directoryView.add(subTree)
        
        return directoryView

    def getFlag(self):
        with open('./rsrc/flag.txt') as flag:
            banner = flag.read()
        
        return banner

    # ui constructor
    def __init__(self):
        self.menu()


user = ui()