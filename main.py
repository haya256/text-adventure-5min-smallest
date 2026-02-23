"""
main.py - ゲームループ・タイマー・イントロ/エンディング
"""

import time
from console_interface import ConsoleInterface
from game import GameState, describe_area, setup_commands


def print_intro() -> None:
    print()
    print("=" * 50)
    print("        あと300秒の改札")
    print("=" * 50)
    print()
    print("深夜の無人駅。終電まであと5分。")
    print("改札を通ろうとしたが、ICカードが手元にない。")
    print("ホームのどこかに手がかりがあるはずだ——")
    print()
    print("(Tab で補完 / Help でコマンド一覧 / Quit で終了)")
    print()


def print_timeout() -> None:
    print()
    print("=" * 50)
    print("  終電が行ってしまった……")
    print()
    print("  改札の向こう、遠ざかるテールランプ。")
    print("  次の電車は朝まで来ない。")
    print("=" * 50)
    print()


def print_ending() -> None:
    time.sleep(0.8)
    print()
    print("電車が入線する音……")
    time.sleep(1.2)
    print()
    print("ホームの電光掲示板が点滅する：")
    time.sleep(0.6)
    print()

    lines = [
        "  ┌─────────────────────────────────────────┐",
        "  │  お疲れ様です。                          │",
        "  │  忘れ物センター研修AIシステム No.710     │",
        "  │  初回起動テスト: 完了                    │",
        "  │  次の目的地: 次の駅                      │",
        "  └─────────────────────────────────────────┘",
    ]
    for line in lines:
        print(line)
        time.sleep(0.15)

    print()
    time.sleep(0.8)
    print("あなたは駅のAIだった。")
    time.sleep(0.5)
    print("「忘れ物を回収し、駅を正常化する」——それが、あなたの使命。")
    time.sleep(0.5)
    print("さあ、電車が出発する。次の駅へ。")
    print()


def main() -> None:
    state = GameState(start_time=time.time())
    cli = ConsoleInterface()
    setup_commands(cli, state)

    print_intro()
    describe_area(state)

    while not state.game_over and not state.game_won:
        remaining = state.remaining
        if remaining <= 0:
            print_timeout()
            return

        color = "\033[31m" if remaining <= 60 else "\033[0m"
        cli.prompt = f"{color}[残り {remaining:3d}秒]\033[0m > "

        try:
            line = input(cli.prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n中断しました")
            return

        if not line.strip():
            continue

        if not cli._execute(line):
            print("終了します。")
            return

    if state.game_won:
        print_ending()


if __name__ == "__main__":
    main()
