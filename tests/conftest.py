import pytest


def _compile(
    source_code,
    *,
    lark_grammar,
    vyper_interface_codes=None,
    evm_version=None,
    vyper_output_formats=("abi", "bytecode"),
    mpc_output_formats=None
):
    from ratl import RatelCompiler

    ratel_compiler = RatelCompiler()
    output = ratel_compiler.compile(
        source_code,
        vyper_output_formats=vyper_output_formats,
        vyper_interface_codes=vyper_interface_codes,
        evm_version=evm_version,
        mpc_output_formats=mpc_output_formats,
    )
    lark_grammar.parse(ratel_compiler._vyper_code + "\n")  # Test grammar.
    return output


# NOTE Taken and adapted from vyperlang/vyper.
def _get_contract(
    w3, source_code, *args, lark_grammar, contract_factory_class, **kwargs
):
    out = _compile(
        source_code,
        lark_grammar=lark_grammar,
        vyper_output_formats=("abi", "bytecode"),
        vyper_interface_codes=kwargs.pop("interface_codes", None),
        evm_version=kwargs.pop("evm_version", None),
        mpc_output_formats=kwargs.pop("mpc_output_formats", None),
    )

    vyper_output = out["vyper"]
    abi = vyper_output["abi"]
    bytecode = vyper_output["bytecode"]
    value = (
        kwargs.pop("value_in_eth", 0) * 10 ** 18
    )  # Handle deploying with an eth value.
    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    deploy_transaction = c.constructor(*args)
    tx_info = {
        "from": w3.eth.accounts[0],
        "value": value,
        "gasPrice": 0,
    }
    tx_info.update(kwargs)
    tx_hash = deploy_transaction.transact(tx_info)
    address = w3.eth.getTransactionReceipt(tx_hash)["contractAddress"]
    contract = w3.eth.contract(
        address,
        abi=abi,
        bytecode=bytecode,
        ContractFactoryClass=contract_factory_class,
    )
    return contract


@pytest.fixture
def get_compiled_code(lark_grammar):
    def _compiled_code(
        source_code,
        vyper_output_formats=("abi", "bytecode"),
        vyper_interface_codes=None,
        evm_version=None,
        mpc_output_formats=None,
    ):
        return _compile(
            source_code,
            lark_grammar=lark_grammar,
            vyper_output_formats=vyper_output_formats,
            vyper_interface_codes=vyper_interface_codes,
            evm_version=evm_version,
            mpc_output_formats=mpc_output_formats,
        )

    return _compiled_code


@pytest.fixture
def get_contract(w3, _VyperContract, lark_grammar):
    def get_contract(
        source_code,
        *args,
        lark_grammar=lark_grammar,
        contract_factory_class=_VyperContract,
        **kwargs
    ):
        return _get_contract(
            w3,
            source_code,
            *args,
            lark_grammar=lark_grammar,
            contract_factory_class=_VyperContract,
            **kwargs
        )

    return get_contract


# def test_compile(mpc_contract_code):
#    from tests.grammar.conftest import get_lark_grammar
#    from ratel import RatelCompiler
#
#    LARK_GRAMMAR = get_lark_grammar()
#
#    ratel_compiler = RatelCompiler()
#    out = ratel_compiler.compile(
#        mpc_contract_code, vyper_output_formats=["abi", "bytecode"],
#    )
#
#    vyper_source = ratel_compiler._vyper_code
#    LARK_GRAMMAR.parse(vyper_source + "\n")  # Test grammar.
#    mpc_output = out["mpc"]
#    mpc_src_code = mpc_output["src_code"]
#    exec(mpc_src_code, globals())
#    assert multiply(3, 4) == 12  # noqa F821
