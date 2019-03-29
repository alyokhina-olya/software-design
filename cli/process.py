import os
import subprocess
import re
from cli.file_service import get_absolute_path, get_files, is_exist
from abc import abstractmethod, ABC
from docopt import docopt
from pathlib import Path


class Process(ABC):
    """Base class for cli commands."""

    def __init__(self, command, args):
        self.command = command
        self.args = args

    @abstractmethod
    def run(self, input, scope):
        pass

    def __eq__(self, other):
        return isinstance(other, Process) and other.command == self.command and other.args == self.args


class Directory:
    path = os.getcwd()

    @staticmethod
    def open_file(file_name):
        return open(get_absolute_path(Directory.path, file_name))

    @staticmethod
    def get_files(directory_name):
        return "\n".join(get_files(Directory.path, directory_name))


class CustomProcess(Process):
    """Runs custom shell script."""

    def __init__(self, command, args):
        super().__init__(command, args)

    def run(self, input, scope):
        command = [self.command] + self.args
        result = subprocess.run(command, stdout=subprocess.PIPE, input=input, universal_newlines=True,
                                check=True, cwd=Directory.path)
        return result.stdout.rstrip()


class Echo(Process):
    """Returns it's arguments separated by spaces."""

    def __init__(self, args):
        super().__init__("echo", args)

    def run(self, input, scope):
        return " ".join(self.args)


class ArgumentError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Cat(Process):
    """Accepts a filename as an argument and returns it's contents. Can use piped input if file is not given."""

    def __init__(self, args):
        super().__init__("cat", args)

    def run(self, input, scope):
        if len(self.args) == 1:
            with Directory.open_file(self.args[0]) as f:
                return f.read()
        elif not self.args and input is not None:
            return input
        else:
            raise ArgumentError(self.__doc__)


class Wc(Process):
    """Accepts a filename as an argument and returns number of lines, words and symbols in it.
    Can use piped input if file is not given."""

    def __init__(self, args):
        super().__init__("wc", args)

    def run(self, input, scope):
        if not self.args and input is None or len(self.args) > 1:
            raise ArgumentError(self.__doc__)

        if self.args:
            with Directory.open_file(self.args[0]) as f:
                input = f.read()
        return " ".join(str(len(units)) for units in [input.split("\n"), input.split(), input])


class Exit(Process):
    """Shuts down cli."""

    def __init__(self, args):
        super().__init__("exit", args)

    def run(self, input, scope):
        if self.args:
            raise ArgumentError(self.__doc__)
        return ""


class Cd(Process):
    """Change the directory of cli"""

    def __init__(self, args):
        super().__init__("cd", args)

    def run(self, input, scope):
        if len(self.args) == 1:
            if is_exist(Directory.path, self.args[0]):
                if os.path.isdir(get_absolute_path(Directory.path, self.args[0])):
                    Directory.path = get_absolute_path(Directory.path, self.args[0])
                else:
                    raise ArgumentError(self.args[0] + " is not a directory")
            else:
                raise ArgumentError(self.args[0] + " does not exist")
        elif len(self.args) == 0:
            Directory.path = str(Path.home())
        return Directory.path


class Ls(Process):
    """ Print list computer files"""

    def __init__(self, args):
        super().__init__("ls", args)

    def run(self, input, scope):
        if len(self.args) == 0:
            return Directory.get_files(Directory.path)
        elif len(self.args) == 1:
            return Directory.get_files(self.args[0])
        else:
            raise ArgumentError(self.__doc__)


class Pwd(Process):
    """Prints a path of the current working directory."""

    def __init__(self, args):
        super().__init__("pwd", args)

    def run(self, input, scope):
        return Directory.path


class Assignment(Process):
    """Assigns a value to an environment variable."""

    def __init__(self, args):
        super().__init__("=", args)

    def run(self, input, scope):
        if len(self.args) != 2:
            raise ArgumentError(__doc__)
        scope[self.args[0]] = self.args[1]
        return ""


class Grep(Process):
    """Filters lines from file or input which match given pattern.

    Usage:
      grep <pattern> [<file>] [-i] [-w] [-A <int>]

    Options:
      -i                Ignore the case.
      -w                Match whole words.
      -A <int>          Non-negative number of lines to print after a match [default: 0].

    """

    def __init__(self, args):
        super().__init__("grep", args)

    def run(self, input, scope):
        args = docopt(str(self.__doc__), self.args, help=False)
        if args["<file>"]:
            with Directory.open_file(args["<file>"]) as f:
                input = f.read()
        if input:
            pattern, context = self.process_args(args)
            output = ""
            gap = 0
            for line in input.splitlines():
                if pattern.search(line):
                    output += line + '\n'
                    gap = context
                elif gap > 0:
                    output += line + '\n'
                    gap -= 1
            return output.rstrip()
        else:
            return ""

    def process_args(self, args):
        pattern = args["<pattern>"]
        if args["-w"]:
            pattern = r"\b" + pattern + r"\b"
        flags = re.IGNORECASE if args["-i"] else 0
        return re.compile(pattern, flags), int(args["-A"])


if __name__ == "__main__":
    grep = Grep(["Lisa", "-A", "11", "-i"])
    grep.run("", {})
