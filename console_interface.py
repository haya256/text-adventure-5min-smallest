"""
console_interface.py - PowerShell風コンソールインターフェイスモジュール

Verb-Noun 方式（例: Take-Ic-card）のコマンド入力と Tab 補完を提供します。

ルール:
  - コマンドは「動詞-名詞」の形式。動詞と名詞はハイフン1文字で繋ぐ。
  - Tab 補完で先頭が大文字化される: take → Take-、ic-card → Ic-card
  - 入力は大文字/小文字どちらでも受け付ける。
  - ハイフンのないコマンドは形式エラー（help / quit / exit を除く）。

使用例:
    from console_interface import ConsoleInterface

    cli = ConsoleInterface(prompt="adventure> ")

    @cli.command("take", "ic-card")
    def take_ic_card():
        print("ICカードを手に取った。")

    cli.run()
"""

import readline
from typing import Callable, Optional


def _setup_readline_tab() -> None:
    """macOS(libedit) と GNU readline の両方に対応して Tab 補完を有効にする。"""
    doc = getattr(readline, "__doc__", "") or ""
    if "libedit" in doc:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")


class ConsoleInterface:
    """
    PowerShell 風 Verb-Noun コマンドインターフェイス。

    コマンド形式: Take-Ic-card
      - 動詞と名詞をハイフン 1 文字で繋ぐ（必須）
      - Tab で先頭大文字に補完
      - 大文字・小文字どちらの入力も受け付ける
    """

    _BUILTIN_COMMANDS: frozenset[str] = frozenset({"help", "quit", "exit"})

    def __init__(self, prompt: str = "> ") -> None:
        self.prompt = prompt
        self.verbs: list[str] = []   # 小文字で保持
        self.nouns: list[str] = []   # 小文字で保持

        self._handlers: dict[tuple[str, str], Callable[[], None]] = {}
        self._verb_noun_pairs: set[tuple[str, str]] = set()

        _setup_readline_tab()
        readline.set_completer(self._completer)
        # ハイフンをデリミタから外す → Verb-Noun 全体が1トークンになる
        readline.set_completer_delims(" \t\n")

    # ------------------------------------------------------------------ #
    # 内部ユーティリティ
    # ------------------------------------------------------------------ #

    @staticmethod
    def _cap(s: str) -> str:
        """先頭1文字だけ大文字化: 'ic-card' → 'Ic-card'"""
        return s[0].upper() + s[1:] if s else s

    # ------------------------------------------------------------------ #
    # 登録 API
    # ------------------------------------------------------------------ #

    def register_verbs(self, verbs: list[str]) -> None:
        """使用可能な動詞を追加登録する（小文字に正規化して保持）。"""
        for v in verbs:
            v = v.lower()
            if v not in self.verbs:
                self.verbs.append(v)

    def register_nouns(self, nouns: list[str]) -> None:
        """使用可能な名詞を追加登録する（小文字に正規化して保持）。"""
        for n in nouns:
            n = n.lower()
            if n not in self.nouns:
                self.nouns.append(n)

    def command(
        self, verb: str, noun: str
    ) -> Callable[[Callable[[], None]], Callable[[], None]]:
        """
        コマンドハンドラを登録するデコレータ。

            @cli.command("take", "ic-card")
            def handler():
                print("took ic-card")
        """
        def decorator(fn: Callable[[], None]) -> Callable[[], None]:
            self._register_handler(verb, noun, fn)
            return fn
        return decorator

    def register_command(
        self, verb: str, noun: str, handler: Callable[[], None]
    ) -> None:
        """コマンドハンドラを直接登録する（デコレータを使わない場合）。"""
        self._register_handler(verb, noun, handler)

    def _register_handler(
        self, verb: str, noun: str, handler: Callable[[], None]
    ) -> None:
        verb, noun = verb.lower(), noun.lower()
        if verb not in self.verbs:
            self.verbs.append(verb)
        if noun not in self.nouns:
            self.nouns.append(noun)
        self._handlers[(verb, noun)] = handler
        self._verb_noun_pairs.add((verb, noun))

    # ------------------------------------------------------------------ #
    # Tab 補完
    # ------------------------------------------------------------------ #

    def _completer(self, text: str, state: int) -> Optional[str]:
        """readline から呼ばれる補完関数。"""
        line = readline.get_line_buffer().strip()

        # 最初の '-' を動詞・名詞の区切りとみなす
        hyphen_idx = line.find("-")

        if hyphen_idx == -1:
            # ---- 動詞の補完 ----
            prefix = line.lower()
            candidates = self._verb_candidates(prefix)
        else:
            # ---- 名詞の補完 ----
            verb_str = line[:hyphen_idx]          # 入力された動詞部分（大文字混じりでも可）
            noun_prefix = line[hyphen_idx + 1:].lower()
            candidates = self._noun_candidates(verb_str, noun_prefix)

        try:
            return candidates[state]
        except IndexError:
            return None

    def _verb_candidates(self, prefix: str) -> list[str]:
        """prefix に前方一致する動詞の補完候補リストを返す。"""
        result: list[str] = []
        # 組み込みコマンド（ハイフンなし）
        for v in sorted(self._BUILTIN_COMMANDS):
            if v.startswith(prefix):
                result.append(self._cap(v))
        # ゲーム動詞（末尾にハイフンを付けて次の入力を促す）
        for v in sorted(self.verbs):
            if v.startswith(prefix):
                result.append(self._cap(v) + "-")
        return result

    def _noun_candidates(self, verb_str: str, noun_prefix: str) -> list[str]:
        """
        verb_str に対応する名詞の補完候補リストを返す。
        戻り値は 'Verb-Noun' 形式（text 全体を置き換えるため）。
        """
        verb_lower = verb_str.lower()
        # その動詞に紐づいた名詞に絞る（登録がなければ全名詞）
        paired = {n for (v, n) in self._verb_noun_pairs if v == verb_lower}
        pool = paired if paired else set(self.nouns)
        matching = sorted(n for n in pool if n.startswith(noun_prefix))
        cap_verb = self._cap(verb_str) if verb_str else ""
        return [cap_verb + "-" + self._cap(n) for n in matching]

    # ------------------------------------------------------------------ #
    # コマンド解析・実行
    # ------------------------------------------------------------------ #

    def _execute(self, line: str) -> bool:
        """
        1行分のコマンドを解析・実行する。
        戻り値: False でメインループを終了する。
        """
        stripped = line.strip()
        lower = stripped.lower()

        # ---- 組み込みコマンド（ハイフン不要） ----
        if lower in ("quit", "exit"):
            return False
        if lower == "help":
            self._print_help()
            return True

        # ---- Verb-Noun 形式のチェック ----
        hyphen_idx = stripped.find("-")
        if hyphen_idx == -1:
            print(
                "[?] 形式エラー: 'Verb-Noun' の形式で入力してください "
                "(例: Take-Ic-card)"
            )
            return True

        verb = stripped[:hyphen_idx].lower()
        noun = stripped[hyphen_idx + 1:].lower()

        if not verb:
            print("[?] 動詞がありません (例: Take-Ic-card)")
            return True
        if not noun:
            print(f"[?] 名詞がありません (例: {self._cap(verb)}-Noun)")
            return True

        # ---- ハンドラ検索 ----
        handler = self._handlers.get((verb, noun))
        if handler:
            handler()
        else:
            if verb in self.verbs:
                print(
                    f"[?] '{self._cap(verb)}' に '{self._cap(noun)}' は使えません"
                )
            else:
                print(
                    f"[?] 不明なコマンド: {self._cap(verb)}-{self._cap(noun)}"
                )

        return True

    # ------------------------------------------------------------------ #
    # ヘルプ表示
    # ------------------------------------------------------------------ #

    def _print_help(self) -> None:
        print("\n--- 使用可能なコマンド ---")
        if self._verb_noun_pairs:
            for verb, noun in sorted(self._verb_noun_pairs):
                print(f"  {self._cap(verb)}-{self._cap(noun)}")
        else:
            if self.verbs:
                print(
                    "  動詞: "
                    + ", ".join(self._cap(v) for v in sorted(self.verbs))
                )
            if self.nouns:
                print(
                    "  名詞: "
                    + ", ".join(self._cap(n) for n in sorted(self.nouns))
                )
        print("  Help  - このヘルプを表示")
        print("  Quit  - 終了")
        print()

    # ------------------------------------------------------------------ #
    # メインループ
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        """
        コンソールの入力ループを開始する。
        Ctrl+C または Quit/Exit で終了。
        """
        print("(Tab で補完 / Help でコマンド一覧 / Quit で終了)\n")
        while True:
            try:
                line = input(self.prompt)
            except (KeyboardInterrupt, EOFError):
                print()
                break

            if not line.strip():
                continue

            if not self._execute(line):
                break
