# lattice-gas-ca

Introduction
------------
According to Wikipedia,
> Lattice gas automata (LGA), or lattice gas cellular automata, are a type of cellular automaton used to simulate fluid flows. They were the precursor to the lattice Boltzmann methods. From lattice gas automata, it is possible to derive the macroscopic Navier-Stokes equations

Here is a prallel implementation of the Lattice Gas Cellular Automata. The serial implementation is a modified version of [William Power's](https://github.com/wpower12) repository [LGS](https://github.com/wpower12/LGS) 

Requirements
------------
Language: Python
Libraries: 
* mpi4py
* numpy
* random 
* matplotlib
* sys
* math

Usage
-----
Serial:
```
$ python lattice-serial.py
```
Parallel:
```
$ mpirun -n <number of processes> python lattice-parallel.py
```

References
----------
* Github Repository: [LGS](https://github.com/wpower12/LGS)
* Wikipedia: [Lattice Gas Automaton](https://en.wikipedia.org/wiki/Lattice_gas_automaton)
* Wikipedia: [Lattice Gas Automaton - HPP Model](https://en.wikipedia.org/wiki/HPP_model)
