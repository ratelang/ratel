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

# compound statements that are replaced with `class`
VYPER_CLASS_TYPES = {"event", "interface", "struct"}

# simple statements or expressions that are replaced with `yield`
VYPER_EXPRESSION_TYPES = {
    "log",
}


def vyperize(code, *, object_types=None):
    """Recovers the vyper contract source code from its python-valid
    representation. This more or less undoes what
    ``vyper.ast.pre_parser.pre_parse`` does.

    Parameters
    ----------
    code : str
        The python-valid formatted vyper source code to be "un-formatted"
        back into "pure" vyper code aka "vyperized".
    object_types: dict
        Mapping of class types contained in the contract.
    """
    code = code.strip("\n")

    tokens = []
    class_token = None
    yield_token = None
    yield_token_line = None

    try:
        code_bytes = code.encode("utf-8")
        g = tokenize(io.BytesIO(code_bytes).readline)

        for token in g:
            # if previous token was "class" then restore it to its vyper form
            if token.type == NAME and class_token is not None:
                prev_token_dict = class_token._asdict()
                prev_token_dict["string"] = object_types["class"][token.string]
                vyper_restored_token = TokenInfo(**prev_token_dict)
                tokens[-1] = vyper_restored_token
            if (
                token.type == OP
                and token.string in ("(", ")")
                and class_token is not None
            ):
                continue
            if token.type == OP and token.string == ":" and class_token is not None:
                token_dict = token._asdict()
                token_dict["start"] = (token.start[0], token.start[1] - 2)
                token_dict["end"] = (token.end[0], token.end[1] - 2)
                token = TokenInfo(**token_dict)
                class_token = None
            if token.type == NAME and token.string == "class" and token.start[1] == 0:
                class_token = token

            if token.type == NAME and yield_token is not None:
                prev_token_dict = yield_token._asdict()
                prev_token_dict["string"] = object_types["yield"][token.string]
                vyper_restored_token = TokenInfo(**prev_token_dict)
                tokens[-1] = vyper_restored_token
                if tokens[-2].string == "(":
                    del tokens[-2]
                yield_token = None

            if (
                token.type == OP
                and token.string == ")"
                and yield_token_line is not None
                and token.end[1] == len(yield_token_line) - 1
            ):
                token_dict = token._asdict()
                token_dict["start"] = (token.start[0], token.start[1] - 1)
                token_dict["end"] = (token.end[0], token.end[1] - 1)
                token = TokenInfo(**token_dict)
                for i, t in enumerate(tokens[::-1]):
                    if t.line != yield_token_line:
                        break
                    t_dict = t._asdict()
                    t_dict["start"] = (t.start[0], t.start[1] - 1)
                    t_dict["end"] = (t.end[0], t.end[1] - 1)
                    t = TokenInfo(**t_dict)
                    tokens[len(tokens) - i - 1] = t
                yield_token_line = None
                continue

            if token.type == NAME and token.string == "yield":
                yield_token = token
                yield_token_line = token.line

            tokens.append(token)
    except TokenError as e:
        raise SyntaxException(e.args[0], code, e.args[1][0], e.args[1][1]) from e

    return untokenize(tokens).decode("utf-8")
