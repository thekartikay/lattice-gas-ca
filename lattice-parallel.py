import numpy as np
import random as r
from mpi4py import MPI
import matplotlib.pyplot as plt
import sys
import math

# simlulation parameters
SIZE_X = 256
SIZE_Y = 256
SUBGRIDSIZE = 4
MAX_P = float(SUBGRIDSIZE*SUBGRIDSIZE*4)
DENSITY = 0.25

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
stat = MPI.Status()

if size > SIZE_X:
    print("Not enough ROWS")
    exit()

subSIZE_X = SIZE_X//size+2

lattice = np.zeros((subSIZE_X, SIZE_Y), dtype=np.byte)
buffer_lattice = np.zeros((subSIZE_X, SIZE_Y), dtype=np.byte)

def msgUp(subGrid):
        # Sends and Recvs rows with Rank+1
        comm.send(subGrid[subSIZE_X-2,:],dest=rank+1)
        subGrid[subSIZE_X-1,:]=comm.recv(source=rank+1)
        return 0

def msgDn(subGrid):
        # Sends and Recvs rows with Rank-1
        comm.send(subGrid[1,:],dest=rank-1)
        subGrid[0,:] = comm.recv(source=rank-1)
        return 0

def init_lattice():
    for x in range(1,subSIZE_X-1):
        for y in range(SIZE_Y):
            for d in range(3):  # Looping over direction states.
                if r.random() < DENSITY:
                    lattice[x][y] += pow( 2, d )
    add_square()

def add_square():
    SSIZE = 0.15
    l = int(0.5*(subSIZE_X - SSIZE*subSIZE_X))
    w = int(0.5*(SIZE_Y - SSIZE*SIZE_Y))
    if rank  == 2:
        for x in range( l, l+int(2*SSIZE*subSIZE_X) ):
            for y in range( w, w+int(2*SSIZE*subSIZE_X) ):
                lattice[x][y] = 15
                buffer_lattice[x][y] = 15

def nthBit( n, i):
    mask = [1, 2, 4, 8]
    return ( n & mask[i] ) != 0

def setBufferBit(y, x, n, v):
        y %= SIZE_Y
        x %= subSIZE_X
        num = buffer_lattice[x][y]
        buffer_lattice[x][y] ^= (-v ^ num) & (1 << n)

def propagate():
    for x in range(subSIZE_X):
        for y in range(SIZE_Y):
            n = lattice[x][y]
            if nthBit(n, 0):   #Up
                setBufferBit( y-1, x, 0, 1 )
            if nthBit(n, 1):   #Right
                setBufferBit( y, x+1, 1, 1 )
            if nthBit(n, 2):   #Down
                setBufferBit( y+1, x, 2, 1 )
            if nthBit(n, 3):   #Left
                setBufferBit( y, x-1, 3, 1 )
            lattice[x][y] = 0

def resolveCollisions():
    for x in range(subSIZE_X):
        for y in range(SIZE_Y):
            n = lattice[x][y]
            if n == 10:
                lattice[x][y] = 5
            elif n == 5:
                lattice[x][y] = 10

def update():
    global lattice, buffer_lattice
    propagate()
    buffer_lattice, lattice = lattice, buffer_lattice
    resolveCollisions()

# BC for all ranks.
init_lattice()
lattice[:,0] = 1.
buffer_lattice[:,0] = 1.
# BC for rank 0.
if rank ==0:
    buffer_lattice[0,:] = 1
    buffer_lattice[:,0] = 1.

oldGrid=comm.gather(lattice[1:subSIZE_X-1,:],root=0)
bufferGrid=comm.gather(buffer_lattice[1:subSIZE_X-1,:],root=0)
for i in range(1,500):
    update()
#exhange edge rows for next interation
    if rank == 0:
        msgUp(lattice)
        msgUp(buffer_lattice)
    elif rank == size-1:
        msgDn(lattice)
        msgDn(buffer_lattice)
    else:
        msgUp(lattice)
        msgUp(buffer_lattice)
        msgDn(lattice)
        msgDn(buffer_lattice)
    newGrid=comm.gather(lattice[1:subSIZE_X-1,:],root=0)
    if rank == 0: 
        result= np.vstack(newGrid)
        print('Generation {} running ...'.format(i))
        plt.imsave('temp/'+str(i)+'.jpg',result)
#plt.imsave('temp/'+str(i)+'.jpg',result)
    
    update()