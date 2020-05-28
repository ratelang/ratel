import io
from tokenize import (
    NAME,
    OP,
    TokenError,
    TokenInfo,
    tokenize,
    untokenize,
)

from vyper.exceptions import SyntaxException

VYPER_CLASS_TYPES = {"contract", "struct"}


def vyperize(code, *, class_types=None):
    """Recovers the vyper contract source code from its python-valid
    representation. This more or less undoes what
    ``vyper.ast.pre_parser.pre_parse`` does.

    Parameters
    ----------
    code : str
        The python-valid formatted vyper source code to be "un-formatted"
        back into "pure" vyper code aka "vyperized".
    class_types: dict
        Mapping of class types contained in the contract.
    """
    tokens = []
    previous_token = None

    try:
        code_bytes = code.encode("utf-8")
        g = tokenize(io.BytesIO(code_bytes).readline)

        for token in g:
            # if previous token was "class" then restore it to its vyper form
            if token.type == NAME and previous_token is not None:
                prev_token_dict = previous_token._asdict()
                prev_token_dict["string"] = class_types[token.string]
                vyper_restored_token = TokenInfo(**prev_token_dict)
                tokens[-1] = vyper_restored_token
            if (
                token.type == OP
                and token.string in ("(", ")")
                and previous_token is not None
            ):
                continue
            if token.type == OP and token.string == ":" and previous_token is not None:
                token_dict = token._asdict()
                token_dict["start"] = (token.start[0], token.start[1] - 2)
                token_dict["end"] = (token.end[0], token.end[1] - 2)
                token = TokenInfo(**token_dict)
                previous_token = None

            if token.type == NAME and token.string == "class" and token.start[1] == 0:
                previous_token = token

            tokens.append(token)
    except TokenError as e:
        raise SyntaxException(e.args[0], code, e.args[1][0], e.args[1][1]) from e

    return untokenize(tokens).decode("utf-8")
