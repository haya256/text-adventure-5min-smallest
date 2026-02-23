"""
game.py - ゲーム状態・エリア説明・コマンド登録
"""

import time
from dataclasses import dataclass, field
from console_interface import ConsoleInterface


@dataclass
class GameState:
    current_area: str = "gate"
    inventory: set = field(default_factory=set)
    locker_open: bool = False
    ic_charged: bool = False
    game_won: bool = False
    game_over: bool = False
    start_time: float = field(default_factory=time.time)

    @property
    def remaining(self) -> int:
        return max(0, int(300 - (time.time() - self.start_time)))


def describe_area(state: GameState) -> None:
    if state.current_area == "gate":
        print()
        print("【改札前】")
        print("終電まであとわずか。無人の改札が静かに光を放っている。")
        print("掲示板、時刻表、券売機、そして改札がある。")
        print("  調べる: notice-board / timetable / ticket-machine / gate")
        print("  移動:   Go-Bench / Go-Locker")
        print()
    elif state.current_area == "bench":
        print()
        print("【ベンチエリア】")
        print("薄暗いホームの端。古びたベンチが一脚置かれている。")
        print("ベンチと、その横に置かれた本が見える。")
        print("  調べる: bench / book")
        print("  移動:   Go-Gate / Go-Locker")
        print()
    elif state.current_area == "locker":
        print()
        print("【コインロッカー】")
        print("番号のかすれたロッカーが並んでいる。一つだけ鍵穴が光っている。")
        print("  調べる: locker / umbrella（取得後）")
        print("  移動:   Go-Gate / Go-Bench")
        print()


def setup_commands(cli: ConsoleInterface, state: GameState) -> None:

    # ------------------------------------------------------------------ #
    # examine
    # ------------------------------------------------------------------ #

    def examine_notice_board():
        print()
        print("掲示板を読んだ。")
        print("  「忘れ物センター 本日の預かり品: 傘・本・定期券（ICカード）」")
        print("  「心当たりのある方は、ベンチおよびロッカーをご確認ください。」")
        print()

    def examine_timetable():
        print()
        print("時刻表を確認した。")
        print("  終電 10番線 23:58発")
        print("  ※改札通過には最低 10円のチャージが必要です。")
        print()

    def examine_ticket_machine():
        print()
        print("券売機を調べた。")
        print("  「ICカードチャージ専用機」")
        print("  Use-Ticket-machine でチャージできる。")
        print()

    def examine_gate():
        print()
        print("改札機を調べた。")
        print("  ICカードをかざすリーダーがある。")
        if "ic-card" in state.inventory:
            print("  Use-Ic-card で通過を試みられる。")
        else:
            print("  ICカードがないと通過できない。")
        print()

    def examine_bench():
        print()
        print("ベンチを調べた。")
        if "locker-key" not in state.inventory:
            print("  座面の下に何かある……小さな鍵だ。")
            print("  Take-Locker-key で手に取れる。")
        else:
            print("  座面の下はもう空だ。")
        print()

    def examine_book():
        if "book" not in state.inventory:
            print()
            print("本を調べた。ベンチの横に置かれた文庫本。")
            print("  Take-Book で持てる。")
            print()
        else:
            print()
            print("本を開いた。")
            print("  付箋が3枚挟まっている。")
            print("  付箋1: 7ページ")
            print("  付箋2: 1ページ")
            print("  付箋3: 0ページ")
            print("  ……数字を並べると何かになるかもしれない。")
            print()

    def examine_locker():
        print()
        print("ロッカーを調べた。")
        if state.locker_open:
            print("  ロッカーは開いている。中に傘が入っている。")
            if "umbrella" not in state.inventory:
                print("  Take-Umbrella で傘を取れる。")
        elif "locker-key" in state.inventory:
            print("  鍵穴がある。Use-Locker-key で開けられそうだ。")
        else:
            print("  暗証番号式のロッカー。鍵が必要そうだ。")
        print()

    def examine_umbrella():
        if "umbrella" not in state.inventory:
            print()
            print("傘を調べた。ロッカーの中にある。")
            print("  Take-Umbrella で持てる。")
            print()
        else:
            print()
            print("傘の柄を調べた。")
            if "ic-card" not in state.inventory:
                print("  柄の中に何か入っている……薄いカードだ。")
                print("  Take-Ic-card で取り出せる。")
            else:
                print("  もう何も入っていない。")
            print()

    def examine_ic_card():
        if "ic-card" in state.inventory:
            print()
            print("ICカードを見た。")
            if state.ic_charged:
                print("  残高: 10円（チャージ済み）")
            else:
                print("  残高: 0円。このままでは改札を通れない。")
            print()
        else:
            print()
            print("[?] ICカードを持っていない。")
            print()

    # ------------------------------------------------------------------ #
    # take
    # ------------------------------------------------------------------ #

    def take_book():
        if state.current_area != "bench":
            print("[?] ここには本がない。")
            return
        if "book" in state.inventory:
            print("[?] もう持っている。")
            return
        state.inventory.add("book")
        print()
        print("本を手に取った。（所持: 本）")
        print("  Examine-Book で内容を確認できる。")
        print()

    def take_locker_key():
        if state.current_area != "bench":
            print("[?] ここには鍵がない。")
            return
        if "locker-key" in state.inventory:
            print("[?] もう持っている。")
            return
        state.inventory.add("locker-key")
        print()
        print("ベンチの下から鍵を拾った。（所持: ロッカーの鍵）")
        print()

    def take_umbrella():
        if state.current_area != "locker":
            print("[?] ここには傘がない。")
            return
        if not state.locker_open:
            print("[?] ロッカーが閉まっている。")
            return
        if "umbrella" in state.inventory:
            print("[?] もう持っている。")
            return
        state.inventory.add("umbrella")
        print()
        print("傘を取った。（所持: 傘）")
        print("  Examine-Umbrella で傘を調べられる。")
        print()

    def take_ic_card():
        if "umbrella" not in state.inventory:
            print("[?] 傘を持っていない。")
            return
        if "ic-card" in state.inventory:
            print("[?] もう持っている。")
            return
        state.inventory.add("ic-card")
        print()
        print("傘の柄からICカードを取り出した。（所持: ICカード）")
        print("  残高: 0円。チャージが必要かもしれない。")
        print()

    # ------------------------------------------------------------------ #
    # go
    # ------------------------------------------------------------------ #

    def go_bench():
        state.current_area = "bench"
        describe_area(state)

    def go_locker():
        state.current_area = "locker"
        describe_area(state)

    def go_gate():
        state.current_area = "gate"
        describe_area(state)

    # ------------------------------------------------------------------ #
    # use
    # ------------------------------------------------------------------ #

    def use_locker_key():
        if state.current_area != "locker":
            print("[?] ここにはロッカーがない。")
            return
        if "locker-key" not in state.inventory:
            print("[?] ロッカーの鍵を持っていない。")
            return
        if state.locker_open:
            print("[?] ロッカーはすでに開いている。")
            return
        print()
        print("鍵穴に鍵を差し込んだ。暗証番号の入力を求められた。")
        try:
            pin = input("  暗証番号: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return
        if pin == "710":
            state.locker_open = True
            print("  カチッ。ロッカーが開いた！")
            print("  中に傘が入っている。Take-Umbrella で取り出せる。")
        else:
            print("  ブー。番号が違う。")
        print()

    def use_ic_card():
        if state.current_area != "gate":
            print("[?] 改札がない。Go-Gate で改札前へ移動しよう。")
            return
        if "ic-card" not in state.inventory:
            print("[?] ICカードを持っていない。")
            return
        if not state.ic_charged:
            print()
            print("  ピーッ！ 残高不足。")
            print("  不足額: 10円。Use-Ticket-machine でチャージできる。")
            print()
        else:
            print()
            print("  ピッ——改札が開いた！")
            print()
            state.game_won = True

    def use_ticket_machine():
        if state.current_area != "gate":
            print("[?] 券売機がない。Go-Gate で改札前へ移動しよう。")
            return
        if "ic-card" not in state.inventory:
            print("[?] チャージするICカードがない。")
            return
        if state.ic_charged:
            print("[?] すでにチャージ済みだ。")
            return
        state.ic_charged = True
        print()
        print("  ICカードに 10円チャージした。（残高: 10円）")
        print()

    # ------------------------------------------------------------------ #
    # 登録
    # ------------------------------------------------------------------ #

    cli.register_command("examine", "notice-board",  examine_notice_board)
    cli.register_command("examine", "timetable",     examine_timetable)
    cli.register_command("examine", "ticket-machine", examine_ticket_machine)
    cli.register_command("examine", "gate",          examine_gate)
    cli.register_command("examine", "bench",         examine_bench)
    cli.register_command("examine", "book",          examine_book)
    cli.register_command("examine", "locker",        examine_locker)
    cli.register_command("examine", "umbrella",      examine_umbrella)
    cli.register_command("examine", "ic-card",       examine_ic_card)

    cli.register_command("take", "book",        take_book)
    cli.register_command("take", "locker-key",  take_locker_key)
    cli.register_command("take", "umbrella",    take_umbrella)
    cli.register_command("take", "ic-card",     take_ic_card)

    cli.register_command("go", "bench",  go_bench)
    cli.register_command("go", "locker", go_locker)
    cli.register_command("go", "gate",   go_gate)

    cli.register_command("use", "locker-key",     use_locker_key)
    cli.register_command("use", "ic-card",        use_ic_card)
    cli.register_command("use", "ticket-machine", use_ticket_machine)
