import shlex
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulatorGUI:

    def __init__(self, root: tk.Tk, vfs_name: str = "default_vfs") -> None:
        self.root = root
        self.vfs_name = vfs_name

        self.root.title(f"VFS Emulator — [{self.vfs_name}]")
        self.root.geometry("750x500")
        self.root.configure(bg="#1e1e1e")

        self._setup_ui()
        self._print_welcome()

    def _setup_ui(self) -> None:
        self.output_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4",
            font=("Consolas", 11),
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0,
        )
        self.output_area.pack(
            padx=10, pady=(10, 5), fill=tk.BOTH, expand=True
        )

        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.prompt_label = tk.Label(
            input_frame,
            text=f"user@{self.vfs_name}:~$ ",
            bg="#1e1e1e",
            fg="#4ec9b0",
            font=("Consolas", 11, "bold"),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            input_frame,
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 11),
            relief=tk.FLAT,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.focus_set()

    def _print_welcome(self) -> None:
        self.write_output(
            f"Эмулятор оболочки запущен. Имя VFS: {self.vfs_name}\n"
            "Доступные команды: ls, cd, exit.\n"
            + "-" * 60
        )

    def write_output(self, text: str) -> None:
        self.output_area.configure(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state=tk.DISABLED)

    def _on_enter(self, event: tk.Event) -> None:
        raw_command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        prompt = self.prompt_label.cget("text")
        self.write_output(f"{prompt}{raw_command}")

        if not raw_command.strip():
            return

        self.execute_command(raw_command)

    def execute_command(self, raw_command: str) -> bool:
        try:
            tokens = shlex.split(raw_command)
        except ValueError as err:
            self.write_output(
                f"Ошибка синтаксиса (неверные кавычки): {err}"
            )
            return False

        if not tokens:
            return True

        cmd_name = tokens[0]
        args = tokens[1:]

        if cmd_name == "exit":
            if args:
                self.write_output(
                    "Ошибка: exit: слишком много аргументов."
                )
                return False
            self.root.destroy()
            return True

        if cmd_name == "ls":
            return self._cmd_ls(args)

        if cmd_name == "cd":
            return self._cmd_cd(args)

        self.write_output(f"Ошибка: команда '{cmd_name}' не найдена.")
        return False

    def _cmd_ls(self, args: list[str]) -> bool:
        for arg in args:
            if arg.startswith("-") and arg not in ("-l", "-a", "-la", "-al"):
                self.write_output(
                    f"Ошибка: ls: неверный ключ '{arg}'."
                )
                return False

        self.write_output(f"[Заглушка] Команда: 'ls', Аргументы: {args}")
        return True

    def _cmd_cd(self, args: list[str]) -> bool:
        if len(args) > 1:
            self.write_output(
                "Ошибка: cd: слишком много аргументов."
            )
            return False

        self.write_output(f"[Заглушка] Команда: 'cd', Аргументы: {args}")
        return True


def main() -> None:
    root = tk.Tk()
    ShellEmulatorGUI(root, vfs_name="my_vfs")
    root.mainloop()


if __name__ == "__main__":
    main()