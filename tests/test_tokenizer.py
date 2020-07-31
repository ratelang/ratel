import ast

try:
    from ast import unparse
except ImportError:
    # Python version < 3.9
    from astunparse import unparse

import pytest

# XXX from vyper.ast.pre_parser import pre_parse
from vyper import compiler as vyper_compiler


@pytest.fixture
def contract_code():
    with open("examples/blind_auction.vy") as f:
        contract_code = f.read()
    return contract_code


@pytest.fixture
def contract_bytecode(contract_code):
    return vyper_compiler.compile_code(contract_code, ("bytecode",))["bytecode"]


@pytest.fixture
def pythonized_contract_code(contract_code):
    from ratl.legacy_vyper_pre_parser import pre_parse

    object_types, m_offsets, pythonized_code = pre_parse(contract_code)
    breakpoint()
    ast_unparsed = unparse(ast.parse(pythonized_code))
    breakpoint()
    return object_types, m_offsets, ast_unparsed


def test_vyperize(pythonized_contract_code, contract_bytecode):
    """The goal of this test is to check that contract code that goes
    through the following steps:

    1. pre-parsed into valid Python code, using ``vyper.ast.pre_parser``
    2. transformed into an abstract syntax tree, using ``ast.parse``
    3. recovered into vyper source code using ``astunparse.unparse``
       (Python < 3.9) or ``ast.unparse`` (Python >= 3.9)

    and compiles to the same bytecode than the original un-manipulated
    vyper source code.
    """
    from ratl.tokenizer import vyperize

    object_types, m_offsets, pythonized_code = pythonized_contract_code
    vyperized_code = vyperize(pythonized_code, object_types=object_types)
    bytecode = vyper_compiler.compile_code(vyperized_code, ("bytecode",))["bytecode"]
    assert bytecode == contract_bytecode
