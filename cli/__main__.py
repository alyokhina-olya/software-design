from cli.expansion import expand, continue_expand, State, VariableExpansionError
from cli.interpretation import interpret, ParseError
from cli.process import Exit, ArgumentError
from os import environ


def controller():
    """Runs cli. Supported commands: cat [file], echo, wc [file], pwd, exit, a=b."""
    scope = environ
    while True:
        try:
            line = input("my-cli$ ")
            tokens = read(line, scope)
            processes = interpret(tokens)
            pipe = None
            if not processes:
                continue
            elif len(processes) == 1:
                process = processes[0]
                if isinstance(process, Exit):
                    break
                else:
                    pipe = process.run(pipe, scope)
            else:
                for process in processes:
                    pipe = process.run(pipe, {})
            print(pipe)
        except (FileNotFoundError, ArgumentError, ParseError, VariableExpansionError, PermissionError) as e:
            print(str(e))


def read(line, scope):
    state, token, tokens = expand(line, scope)
    while state != State.BARE_STRING:
        line = input("> ")
        state, token, tokens = continue_expand(line, scope, state, token, tokens)
    return tokens


if __name__ == "__main__":
    controller()
