from enum import Enum

from cli.process import Cat, Wc, Exit, Echo, Pwd, Assignment, CustomProcess, Grep, Cd, Ls


class State(Enum):
    WAITING_COMMAND = 0
    WAITING_PIPE = 1


command_to_process = {
    "cat": Cat,
    "wc": Wc,
    "exit": Exit,
    "pwd": Pwd,
    "echo": Echo,
    "grep": Grep,
    "cd": Cd,
    "ls": Ls,
    "=": Assignment
}


class ParseError(Exception):
    def __init__(self):
        super().__init__("Expected command after pipe")


def interpret(tokens):
    """Wraps commands separated by pipes into instances of Process class."""

    if not tokens:
        return []
    processes = []
    state = State.WAITING_COMMAND
    command = None
    args = []
    for token in tokens:
        if token == "|" and state == State.WAITING_PIPE:
            processes.append(build_process(command, args))
            args = []
            command = None
            state = State.WAITING_COMMAND
        elif state == State.WAITING_PIPE:
            args.append(token)
        elif state == State.WAITING_COMMAND:
            assignment = token.split('=', maxsplit=1)
            if len(assignment) == 2 and assignment[0]:
                args = assignment
                command = "="
            else:
                command = token
            state = State.WAITING_PIPE
    if state == State.WAITING_PIPE:
        processes.append(build_process(command, args))
    else:
        raise ParseError()
    return processes


def build_process(command, args):
    if command in command_to_process:
        return command_to_process.get(command)(args)
    else:
        return CustomProcess(command, args)
