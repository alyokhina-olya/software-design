from enum import Enum


class State(Enum):
    BARE_STRING = 0
    SINGLE_QUOTE = 1
    DOUBLE_QUOTE = 2


class VariableExpansionError(Exception):
    def __init__(self, position):
        super().__init__("Error at position {}".format(position))


def break_on_whitespace(state):
    return state == State.BARE_STRING


def expand_variable(state):
    return state == State.BARE_STRING or state == State.DOUBLE_QUOTE


def last_whitespace(line, start, n):
    while start + 1 < n and line[start + 1] == ' ':
        start += 1
    return start


def expand(line, scope):
    return continue_expand(line, scope, State.BARE_STRING, "", [])


def continue_expand(line, scope, state, token, tokens):
    """Expands environment variables and splits command into tokens.

    @:returns (state, token, tokens) which can be reused in parsing of the next line
    @:param state -- state returned by previous call, indicates whether cursor is currently inside quotes
    @:param token -- token returned by previous call, stores a prefix of the current parsing word
    @:param tokens -- tokens returned by previous call, stores previous tokens of this command

    """
    i, n = 0, len(line)
    while i < n:
        if line[i] == ' ' and break_on_whitespace(state):
            if token:
                tokens.append(token)
                token = ""
            i = last_whitespace(line, i, n)
        elif line[i] == '\'' and state == State.BARE_STRING:
            state = State.SINGLE_QUOTE
        elif line[i] == '\'' and state == State.SINGLE_QUOTE:
            state = State.BARE_STRING
        elif line[i] == '"' and state == State.BARE_STRING:
            state = State.DOUBLE_QUOTE
        elif line[i] == '"' and state == State.DOUBLE_QUOTE:
            state = State.BARE_STRING
        elif line[i] == '~' and expand_variable(state):
            token += scope['HOME']
        elif line[i] == '$' and expand_variable(state):
            variable = ""
            for j in range(i + 1, n + 1):
                if j == n or line[j] == ' ':
                    raise VariableExpansionError(i)
                variable += line[j]
                if variable in scope:
                    token += scope[variable]
                    i = j
                    break
        else:
            token += line[i]
        i += 1
    if state == State.BARE_STRING:
        if token:
            tokens.append(token)
            token = ""
    else:
        token += '\n'
    return state, token, tokens
