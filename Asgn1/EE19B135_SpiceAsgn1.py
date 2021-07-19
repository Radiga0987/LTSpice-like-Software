#! /usr/bin/env python3
"""The above line is for portability across different systems in case the 
language interpreter is installed in different locations."""
import sys

# This will store entire information about the circuit with all unimportant information removed
ckt = []


def cktstore(line):  # Function that stores the circuit in ckt
    # This function will be useful for assignment 2 and is not necessary here
    tokens = line.split('#')[0].split()
    ckt.append(tokens)


try:
    if (len(sys.argv) != 2):  # Checking if number of arguments is not 2
        # If not 2, the correct usage is shown
        print('Invalid number of arguments')
        print('Usage: %s <inputfile>' % sys.argv[0])
        exit(0)

    filename = sys.argv[1]
    file = open(filename)  # Opening the file
    lines = file.readlines()  # Each line is stored as an element in a list
    file.close()

    # Using constant variables for .circuit and .end rather than hardcoding
    CIRCUIT = ".circuit"
    END = ".end"

    # Following 2 variables are used to store index of line of .circuit and .end
    startloc = -1
    endloc = -1

    for line in lines:  # Determining values of startloc and endloc
        tokens = line.split()  # Each element in a given line is put into a list
        if(tokens[0] == CIRCUIT):
            startloc = lines.index(line)
        if(tokens[0] == END):
            endloc = lines.index(line)

    """If startloc/endloc is -1 implies, they do not exist in the file(But not
    necessary to check endloc==-1 as it will be taken care of in the following
    condition) or if startloc>=endloc,then circuit definition is invalid as
    .circuit should come before .end"""
    if(startloc == -1 or startloc >= endloc):
        print("Error! Circuit definition is invalid.")
        exit(0)

    # We use only the lines in from startloc to endloc(including startloc but not endloc)
    # We reverse the order of lines using reversed()
    # for loop to traverse throug every line of the circuit
    for line in reversed(lines[startloc:endloc]):
        tokens = line.split()  # Each element in a given line is put into a list

        """ If the following condition is true, it means that we have stored the entire circuit in ckt 
        by using the code after this if statement"""
        if(tokens[0] == CIRCUIT):
            # Since the entire circuit is stored in ckt, we can now reverse each line and print it out to get solution
            for l in ckt:
                print(' '.join(list(reversed(l))))
            break
        try:  # Components of the line in current iteration is stored in ckt using the function cktstore
            cktstore(line)
        except:  # In case there is some invalid format
            print("Invalid format inside the .netlist file")
            break


except Exception:  # If the file names are wrong,this error is printed
    print("Invalid File")

exit(0)
