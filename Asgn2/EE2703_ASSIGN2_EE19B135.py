#!/usr/bin/env python3
"""The above line is for portability across different systems in case the 
language interpreter is installed in different locations."""

import sys
import numpy as np
import cmath

# Using constant variables rather than hard coding.
CIRCUIT = '.circuit'
END = '.end'
AC = '.ac'


def main():
    # Checks if the number of arguments is correct, else exits the script.
    if len(sys.argv) != 2:
        print("Invalid number of arguments.")
        print("Usage: %s <inputfile>" % sys.argv[0])
        sys.exit()
    else:
        filename = sys.argv[1]

    # Checks if the file exists, else exits the script.
    try:
        f = open(filename, 'r')
    except IOError:
        print('Invalid File')
        sys.exit()

    lines = f.read().splitlines()
    f.close()
    # print(lines)

    def CircuitDescription(lines):
        """This function returns a list describing the circuit removing 
        all the comments and other unimportant parts."""
        CircuitReturned, flag, AcCheck, circuit = [], 0, 0, []
        for line in lines:
            Token = line.strip().split()
            newline = []
            for token in Token:
                if token[0] == '#':  # Removing Comments
                    break
                newline.append(token)
            newline = ' '.join(newline)
            circuit.append(newline)

        for line in circuit:  # Checking for .circuit and .end
            if line == CIRCUIT:
                CircuitReturned.append(line)
                flag = 1
            elif line == END and flag == 1:
                CircuitReturned.append(line)
                flag = 2
            elif line.split(' ', 1)[0] == AC and flag == 2:
                CircuitReturned.append(line)
                AcCheck = 1
            elif flag == 1:
                CircuitReturned.append(line)

        if len(CircuitReturned) == 0:
            print('The file does not contain ".circuit" or ".end" line.')
            sys.exit()

        if CircuitReturned[-1] != END and AcCheck == 0:
            print('The netlist file doesnot contain ".end" line.')
            sys.exit()

        return AcCheck, CircuitReturned

    # All circuit elements required for this assignment
    CircuitElements = ['R', 'C', 'L', 'V', 'I']

    def Nodes(circuit):
        """
        Extracts nodes from the circuit.
        A list describing the circuit is given as input to this function 
        and it returns a dictionary containing nodes.
        """
        nodes, dict_of_nodes = [], {}
        for line in circuit:
            Token = line.split()
            x = Token[0][0]
            if x in CircuitElements:
                nodes.extend(Token[1:3])
            else:
                print('Unidentified device in the netlist file.')
                sys.exit()
        nodes = list(set(nodes))
        nodes.sort(reverse=True)

        for i in range(len(nodes)):
            if i == 0:
                dict_of_nodes['GND'] = 0
            else:
                dict_of_nodes[str(i)] = i

        return dict_of_nodes

    def val(Str):
        """
        Returns the numeric value from exponential notation.
        """
        if Str.isnumeric() or '-' in Str or '.' in Str:
            return float(Str)
        if Str.isalnum() or '-' in Str or '.' in Str:
            i = Str.index('e')
            try:
                number, power = float(Str[:i]), int(Str[i+1:])
                return number * (10**power)
            except Exception:
                print('Error in exponential notations.')
                sys.exit()
        return

    def FinalSoln_Print(final_soln, nodeSwap, nodes):
        """
        Function for printing the final values of node voltages
        and current through voltage sources for the given circuit
        in standard form.
        """
        for key, value in nodeSwap.items():
            if value in nodes:
                print('V_' + str(value), end=' ')
                print('= {0:.3e} ' .format(final_soln[key]), end='V\n')
            else:
                print('I_' + str(value), end=' ')
                print('= {0:.3e} ' .format(final_soln[key]), end='A\n')

    AcCheck, CircuitReturned = CircuitDescription(lines)

    """
    From line 132 to line 231, MNA-modified nodal analysis 
    has been applied to solve any given circuit, which can be
    an AC or DC ciruit(checked using AcCheck) but with a single 
    frequency only as mentioned in the assignment.
    If multiple frequencies are present, we can make another function
    which will perform the operation of superposition and hence solve
    the circuit.
    """
    datatype = float
    if AcCheck:
        datatype = complex
        freq = val(CircuitReturned[-1].split()[2])
        w = 2 * np.pi*freq
        del CircuitReturned[-1]
    del CircuitReturned[0], CircuitReturned[-1]

    nodes = Nodes(CircuitReturned)

    CurrentSources = np.zeros(len(nodes), dtype=datatype)

    Matrix_locs = np.zeros((len(nodes), len(nodes)), dtype=np.int32)

    Z, V = np.zeros_like(Matrix_locs), np.zeros_like(Matrix_locs)
    R, C, L = -np.ones_like(Matrix_locs, dtype=datatype), -np.ones_like(Matrix_locs, dtype=datatype),\
        -np.ones_like(Matrix_locs, dtype=datatype)

    nodes_variable = nodes.copy()

    for line in CircuitReturned:
        if line[0] == 'V':
            Token = line.split()
            nodes_variable[Token[0]] = len(nodes_variable)

    nodeSwap = nodes_variable.__class__(map(reversed, nodes_variable.items()))

    A = np.zeros((len(nodes_variable), len(nodes_variable)), dtype=datatype)
    b = np.zeros((len(nodes_variable)), dtype=datatype)
    solution = np.zeros_like(b)
    no = 0

    for line in CircuitReturned:
        Token = line.split()
        x = Token[0][0]
        p, n = nodes[Token[1]], nodes[Token[2]]
        Matrix_locs[p, n], Matrix_locs[n, p] = 1, 1
        value = val(Token[-1])

        if x == 'V':
            V[p, n], V[n, p] = nodes_variable[Token[0]], - \
                nodes_variable[Token[0]]
            if Token[3] == 'ac':
                phase = value
                A[no, p], A[no, n], b[no] = 1, - \
                    1, cmath.rect(val(Token[-2])*0.5, phase)
                no += 1
            elif Token[3] == 'dc':
                A[no, p], A[no, n], b[no] = 1, -1, value
                no += 1
            else:
                print('Error in voltage types.')
                sys.exit()

        if x == 'I':
            if Token[3] == 'ac':
                phase = value
                CurrentSources[p] += cmath.rect(val(Token[-2])*0.5, phase)
                CurrentSources[p] -= cmath.rect(val(Token[-2])*0.5, phase)
            elif Token[3] == 'dc':
                CurrentSources[p] += value
                CurrentSources[n] -= value
            else:
                print('Error in current types.')
                sys.exit()

        if x == 'R':
            Z[p, n], Z[n, p] = 1, 1
            R[p, n] = value if R[p, n] == - \
                1 else ((R[p, n]*value)/(value + R[p, n]))
            R[n, p] = R[p, n]

        if x == 'C' and AcCheck:
            Z[p, n], Z[n, p] = 1, 1
            C[p, n] = value if C[p, n] == -1 else C[p, n] + value
            C[n, p] = C[p, n]

        if x == 'L':
            if AcCheck:
                Z[p, n], Z[n, p] = 1, 1
                L[p, n] = value if L[p, n] == - \
                    1 else ((L[p, n]*value)/(value + L[p, n]))
                L[n, p] = L[p, n]
            else:
                A[no, p], A[no, n] = 1, -1
                no += 1

    I = (R > 0)*R + (C > 0)*(np.reciprocal(1j*w*C)) + \
        (L > 0)*(1j*w*L) if AcCheck else (R > 0)*R

    for i in range(len(nodes)-1):
        for j in range(len(nodes)):
            if Matrix_locs[i, j] and Z[i, j]:
                A[no, i] += np.reciprocal(I[i, j])
                A[no, j] -= np.reciprocal(I[i, j])
            if Matrix_locs[i, j] and V[i, j]:
                A[no, abs(V[i, j])] += np.sign(V[i, j])
        b[no] -= CurrentSources[i]
        no += 1
    A[no, 0] = 1

    try:
        solution = np.linalg.solve(A, b)  # Solving Ax=b
        # This solution is given to FinalSoln_Print to print final answers
        FinalSoln_Print(solution, nodeSwap, nodes)
    except np.linalg.LinAlgError:
        print('Singular Matrix.Inverse of A does not exist.')


main()
