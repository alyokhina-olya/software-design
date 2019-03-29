import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from cli.process import CustomProcess, Echo, Pwd, Exit, Cat, Wc, Assignment, Grep, Ls, Cd


class TestProcess(TestCase):
    def test_custom_process(self):
        process = CustomProcess("echo", ["hello", "kitty"])
        output = process.run(None, {})
        self.assertEqual("hello kitty", output)

        process = CustomProcess("python", [])
        output = process.run("print(1 + 1)", {})
        self.assertEqual("2", output)

    def test_echo(self):
        process = Echo(["hello", "kitty"])
        output = process.run(None, {})
        self.assertEqual("hello kitty", output)

        process = Echo([])
        output = process.run("input", {})
        self.assertEqual("", output)

    def test_pwd(self):
        pwd = os.getcwd()

        process = Pwd([])
        output = process.run(None, {})
        self.assertEqual(pwd, output)

        process = Pwd(["a", "b", "c"])
        output = process.run(None, {})
        self.assertEqual(pwd, output)

        process = Pwd([])
        output = process.run("abc", {})
        self.assertEqual(pwd, output)

    def test_cat(self):
        process = Cat([])
        output = process.run("kitty", {})
        self.assertEqual("kitty", output)

        with TemporaryDirectory() as dir:
            with open(dir + "/test", "w") as f:
                f.write("hello kitty")

            process = Cat([f.name])
            output = process.run(None, {})
            self.assertEqual("hello kitty", output)

            process = Cat([f.name])
            output = process.run("world", {})
            self.assertEqual("hello kitty", output)

    def test_ls(self):
        with TemporaryDirectory() as dir:
            with open(dir + "/test", "w") as f:
                f.write("hello\nkitty")

            process = Ls([dir])
            output = process.run(None, {})
            self.assertEqual("test", output)

    def test_cd(self):
        with TemporaryDirectory() as dir:
            with open(dir + "/test", "w") as f:
                f.write("hello\nkitty")

            process = Cd([dir])
            output = process.run(None, {})
            process_pwd = Cd([dir])
            cur_dir = process_pwd.run(None, {})
            self.assertEqual(dir, output)
            self.assertEqual(dir, cur_dir)
            process = Cd([os.getcwd()])
            process.run(None, {})

    def test_wc(self):
        process = Wc([])
        output = process.run("hello\nkitty", {})
        self.assertEqual("2 2 11", output)

        with TemporaryDirectory() as dir:
            with open(dir + "/test", "w") as f:
                f.write("hello\nkitty")

            process = Wc([f.name])
            output = process.run(None, {})
            self.assertEqual("2 2 11", output)

            process = Wc([f.name])
            output = process.run("world", {})
            self.assertEqual("2 2 11", output)

    def test_assignment(self):
        scope = {}
        process = Assignment(["hello", "kitty"])
        process.run(None, scope)
        self.assertEqual(scope, {"hello": "kitty"})

        scope = {"hello": "world"}
        process = Assignment(["hello", "kitty"])
        process.run(None, scope)
        self.assertEqual(scope, {"hello": "kitty"})

    def test_exit(self):
        process = Exit([])
        output = process.run(None, {})
        self.assertEqual("", output)

    def test_grep(self):
        process = Grep(["Li.?a", "-w"])
        output = process.run("Lia\nLisan\nLima", {})
        self.assertEqual("Lia\nLima", output)

        process = Grep(["Lisa", "-i"])
        output = process.run("Lia\nrLiSAr\nLima", {})
        self.assertEqual("rLiSAr", output)

        process = Grep(["Lisa", "-A", "2"])
        output = process.run("K\nLisa\nrLiSAr\nALisa\nK\nJ\nM\nLisa", {})
        self.assertEqual("Lisa\nrLiSAr\nALisa\nK\nJ\nLisa", output)

        with TemporaryDirectory() as dir:
            with open(dir + "/test", "w") as f:
                f.write("hello\nkitty")

            process = Grep(["kIt", f.name, "-i"])
            output = process.run(None, {})
            self.assertEqual("kitty", output)
