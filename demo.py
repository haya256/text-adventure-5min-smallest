"""
demo.py - console_interface モジュールの使用例

コマンド形式: Verb-Noun  (例: Take-Ic-card)
"""

from console_interface import ConsoleInterface

cli = ConsoleInterface(prompt="adventure> ")

# ---- デコレータでコマンドを登録 ----

@cli.command("take", "ic-card")
def take_ic_card():
    print("ICカードを手に取った。")


@cli.command("insert", "ic-card")
def insert_ic_card():
    print("ICカードをゲートに差し込んだ。ピッ！ゲートが開いた。")


@cli.command("examine", "gate")
def examine_gate():
    print("改札ゲートだ。ICカードをタッチすれば通れそうだ。")


@cli.command("go", "gate")
def go_gate():
    print("ゲートに近づいた。ICカードが必要だ。")


# ---- 直接登録する例 ----
def examine_door():
    print("重厚な木製のドアだ。鍵穴がある。")

cli.register_command("examine", "door", examine_door)


# ---- メインループ開始 ----
if __name__ == "__main__":
    cli.run()
