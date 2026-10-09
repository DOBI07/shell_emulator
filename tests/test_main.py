"""Тесты парсера и команд эмулятора."""

import unittest

from src.main import parse_line, run_command


class ParserTest(unittest.TestCase):
    """Проверки разбора строки на слова."""

    def test_simple_words(self):
        self.assertEqual(parse_line("ls -l docs"), ["ls", "-l", "docs"])

    def test_extra_spaces(self):
        self.assertEqual(parse_line("  cd    home  "), ["cd", "home"])

    def test_double_quotes(self):
        self.assertEqual(parse_line('cd "my folder"'), ["cd", "my folder"])

    def test_single_quotes(self):
        self.assertEqual(parse_line("ls 'a  b'"), ["ls", "a  b"])

    def test_empty_quotes(self):
        self.assertEqual(parse_line('ls ""'), ["ls", ""])

    def test_empty_line(self):
        self.assertEqual(parse_line(""), [])

    def test_unclosed_quote(self):
        with self.assertRaises(ValueError):
            parse_line('ls "abc')


class CommandTest(unittest.TestCase):
    """Проверки команд и сообщений об ошибках."""

    def test_ls(self):
        self.assertEqual(run_command("ls"), "ls: аргументы = []")

    def test_ls_with_args(self):
        self.assertEqual(
            run_command('ls -l "my dir"'),
            "ls: аргументы = ['-l', 'my dir']",
        )

    def test_cd(self):
        self.assertEqual(run_command("cd /tmp"), "cd: аргументы = ['/tmp']")

    def test_unknown_command(self):
        self.assertEqual(run_command("foo"), "foo: команда не найдена")

    def test_ls_invalid_option(self):
        self.assertIn("неверный ключ", run_command("ls -z"))

    def test_cd_too_many_args(self):
        self.assertIn("слишком много", run_command("cd a b"))

    def test_unclosed_quote(self):
        self.assertIn("не закрыта кавычка", run_command('cd "abc'))

    def test_empty_line(self):
        self.assertEqual(run_command("   "), "")

    def test_exit(self):
        self.assertIsNone(run_command("exit"))

    def test_exit_with_args(self):
        self.assertIn("не принимает", run_command("exit 1"))


if __name__ == "__main__":
    unittest.main()
