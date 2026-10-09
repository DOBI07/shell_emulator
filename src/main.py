"""Эмулятор оболочки UNIX-подобной ОС (этап 1: REPL)."""

import getpass
import socket

QUOTES = ("'", '"')
LS_OPTIONS = ("-l", "-a", "-la", "-al")
MAX_CD_ARGS = 1
WINDOW_SIZE = "800x500"
BG_COLOR = "#000000"
FG_COLOR = "#d4d4d4"
FONT = ("Courier New", 12)

history = []
history_index = 0


def get_username():
    """Возвращает имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return "user"


USER = get_username()
HOST = socket.gethostname()
PROMPT = f"{USER}@{HOST}:~$ "
TITLE = f"Эмулятор - [{USER}@{HOST}]"


def parse_line(line):
    """Разбивает строку на слова, учитывая кавычки.

    Если кавычка не закрыта, вызывает ValueError.
    """
    words = []
    current = ""
    in_word = False
    quote = None
    for char in line:
        if quote:
            if char == quote:
                quote = None
            else:
                current += char
        elif char in QUOTES:
            quote = char
            in_word = True
        elif char.isspace():
            if in_word:
                words.append(current)
                current = ""
                in_word = False
        else:
            current += char
            in_word = True
    if quote:
        raise ValueError("не закрыта кавычка " + quote)
    if in_word:
        words.append(current)
    return words


def cmd_ls(args):
    """Заглушка ls: проверяет ключи, печатает имя и аргументы."""
    for arg in args:
        if arg.startswith("-") and arg not in LS_OPTIONS:
            return f"ls: неверный ключ -- '{arg}'"
    return f"ls: аргументы = {args}"


def cmd_cd(args):
    """Заглушка cd: не более одного аргумента, печатает имя и аргументы."""
    if len(args) > MAX_CD_ARGS:
        return "cd: слишком много аргументов"
    return f"cd: аргументы = {args}"


def cmd_exit(args):
    """Команда exit: возвращает None, что означает «закрыть окно»."""
    if args:
        return "exit: команда не принимает аргументов"
    return None


COMMANDS = {"ls": cmd_ls, "cd": cmd_cd, "exit": cmd_exit}


def run_command(line):
    """Выполняет строку. Возвращает текст ответа или None для exit."""
    try:
        words = parse_line(line)
    except ValueError as error:
        return f"ошибка разбора: {error}"
    if not words:
        return ""
    name = words[0]
    args = words[1:]
    if name not in COMMANDS:
        return f"{name}: команда не найдена"
    return COMMANDS[name](args)


def show_prompt(text):
    """Печатает приглашение и запоминает, где начинается ввод."""
    text.insert("end", PROMPT)
    text.mark_set("input_start", "end-1c")
    text.mark_gravity("input_start", "left")
    text.mark_set("insert", "end")
    text.see("end")


def replace_input(text, new_text):
    """Заменяет набранный пользователем текст на new_text."""
    text.delete("input_start", "end-1c")
    text.insert("end-1c", new_text)


def on_key(event):
    """Любая клавиша: не даёт печатать левее приглашения."""
    text = event.widget
    if text.compare("insert", "<", "input_start"):
        text.mark_set("insert", "end")


def on_backspace(event):
    """Backspace: не даёт стереть приглашение."""
    text = event.widget
    if text.compare("insert", "<=", "input_start"):
        return "break"
    return None


def on_home(event):
    """Home: курсор в начало ввода (сразу после приглашения)."""
    event.widget.mark_set("insert", "input_start")
    return "break"


def on_enter(event):
    """Enter: выполняет введённую команду и печатает результат."""
    global history_index
    text = event.widget
    line = text.get("input_start", "end-1c")
    text.insert("end", "\n")
    if line.strip():
        history.append(line)
    history_index = len(history)
    result = run_command(line)
    if result is None:
        text.winfo_toplevel().destroy()
        return "break"
    if result:
        text.insert("end", result + "\n")
    show_prompt(text)
    return "break"


def on_up(event):
    """Стрелка вверх: предыдущая команда из истории."""
    global history_index
    if history:
        history_index = max(history_index - 1, 0)
        replace_input(event.widget, history[history_index])
    return "break"


def on_down(event):
    """Стрелка вниз: следующая команда из истории."""
    global history_index
    history_index = min(history_index + 1, len(history))
    if history_index < len(history):
        replace_input(event.widget, history[history_index])
    else:
        replace_input(event.widget, "")
    return "break"


def main():
    """Создаёт окно-консоль и запускает главный цикл."""
    import tkinter as tk

    root = tk.Tk()
    root.title(TITLE)
    root.geometry(WINDOW_SIZE)
    text = tk.Text(
        root, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
        insertbackground=FG_COLOR, wrap="word",
    )
    text.pack(fill="both", expand=True)
    text.bind("<Key>", on_key)
    text.bind("<BackSpace>", on_backspace)
    text.bind("<Home>", on_home)
    text.bind("<Return>", on_enter)
    text.bind("<KP_Enter>", on_enter)
    text.bind("<Up>", on_up)
    text.bind("<Down>", on_down)
    show_prompt(text)
    text.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
