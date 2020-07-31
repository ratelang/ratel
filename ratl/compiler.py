import ast
import copy

try:
    from ast import unparse
except ImportError:
    # Python version < 3.9
    from astunparse import unparse

# XXX from vyper.ast.pre_parser import pre_parse
from vyper import compiler as vyper_compiler
from vyper.opcodes import DEFAULT_EVM_VERSION

from .legacy_vyper_pre_parser import pre_parse
from .tokenizer import vyperize

# TODO figure out how to get an AST object from the mpc nodes extracted out


def ast_to_dict():
    raise NotImplementedError


# TODO: rename ...
# class Bisector(ast.NodeTransformer):
class Transformer(ast.NodeTransformer):
    def __init__(self):
        self.mpc_nodes = []
        self.mpc_module = ast.Module(body=[], type_ignores=[])

    def _visit_function_def(self, node):
        self.generic_visit(node)
        for dec in node.decorator_list:
            if dec.id == "mpc":
                # NOTE remove @mpc decorator as it is only needed in the
                # context of the vyper contract, and not in the context of
                # the MPC applicationcode
                node.decorator_list = [
                    dec for dec in node.decorator_list if dec.id != "mpc"
                ]
                self.mpc_nodes.append(node)
                self.mpc_module.body.append(node)
                return None
        else:
            return node

    def visit_FunctionDef(self, node):  # noqa N802
        return self._visit_function_def(node)

    def visit_AsyncFunctionDef(self, node):  # noqa N802
        return self._visit_function_def(node)


class RatelCompiler:
    def __init__(self, *, node_transformer_class=None):
        # XXX
        # def __init__(self, *, contract_source, node_transformer_class=None):
        if node_transformer_class is None:
            node_transformer_class = Transformer
        self.node_transformer = node_transformer_class()
        # XXX self.contract_source = contract_source
        # intermediate code elements
        self._pythonized_code = None
        self._metadata = {}
        self._code_tree = None
        self._vyper_code_tree = None
        self._mpc_code_tree = None
        self._vyper_code = None
        self._mpc_code = None

    def _pythonize(self, contract_source):
        object_types, m_offsets, reformatted_code = pre_parse(contract_source)
        self._pythonized_code = reformatted_code
        self._metadata["object_types"] = object_types
        self._metadata["m_offsets"] = m_offsets
        return object_types, reformatted_code

    def _parse(self, code):
        self._code_tree = ast.parse(code)
        return self._code_tree

    def _transform(self, tree):
        self.node_transformer.visit(tree)
        self._mpc_code_tree = self.node_transformer.mpc_module
        return tree

    def _recover_vyper_code(self, pythonized_vyper_code, object_types):
        return vyperize(pythonized_vyper_code, object_types=object_types)

    def _extract_codes(self, contract_source):
        object_types, reformatted_code = self._pythonize(contract_source)
        self._code_tree = self._parse(reformatted_code)
        self._vyper_code_tree = copy.deepcopy(self._code_tree)
        self._transform(self._vyper_code_tree)
        pythonized_vyper_code = unparse(self._vyper_code_tree)
        self._vyper_code = self._recover_vyper_code(pythonized_vyper_code, object_types)
        self._mpc_code = unparse(self._mpc_code_tree)
        return self._vyper_code, self._mpc_code

    def compile(
        self,
        contract_source,
        *,
        vyper_output_formats=None,
        vyper_interface_codes=None,
        evm_version=DEFAULT_EVM_VERSION,
        mpc_output_formats=None
    ):
        """Compiles the given contract source code."""
        if mpc_output_formats:
            raise NotImplementedError
        else:
            mpc_output_formats = ("src_code",)
        vyper_code, mpc_code = self._extract_codes(contract_source)
        vyper_output = vyper_compiler.compile_code(
            vyper_code,
            output_formats=vyper_output_formats,
            interface_codes=vyper_interface_codes,
            evm_version=evm_version,
        )
        mpc_output = {"src_code": self._mpc_code}
        return {"vyper": vyper_output, "mpc": mpc_output}
