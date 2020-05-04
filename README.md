# ratel
Ratel is a research project.

## Rough Idea
The current focus is to extend an existing smart contract programming
language such that it can support the writing of MPC (multi-party computation)
programs. Roughly speaking, `ratel`'s current goal is simply to be a kind of
hybrid language that would allow a programmer to write the smart contract
part and MPC part in one language, one file.

When compiling a `ratel` program, the output would be in two main parts:

1. smart contract ABI and bytecode
2. MPC program ABI and bytecode

The smart contract ABI and bytecode can be used to deploy the contract onto
the targeted blockchain and to interact with it.

The MPC program ABI and bytecode is meant to be passed to an MPC application
that would execute the MPC program.

For the near term, the MPC ABI can be parsed by an MPC application which will
then execute the corresponding program.

Eventually, assuming that an MPC framework would have a virtual machine, then
the bytecode would be passed to that virtual machine.

## Implementation
In terms of implementation, the current goal is to extend the Ethereum's
`vyper` smart contract language so that it can support MPC program function
definitions.

It's not clear how exactly this will be done but one approach that is
currently considered involves modifying `vyper`'s compilation phase such
that `vyper`'s compiler produces the usual expected `vyper` output, and in
addition `ratel`'s ABI and bytecode. The total output can be then passed to
a HonerBadgerMPC application that will consume the output such that the
smart contract ABI and bytecode will be used to interact with the contract
on Ethereum meanwhile the MPC program ABI and bytecode will be used to execute
the MPC program.
