# あと300秒の改札

5分間で脱出するテキストアドベンチャーゲームです。深夜の無人駅でICカードを探し、終電に乗り込みましょう。

## ストーリー

深夜の無人駅。終電まであと5分。
改札を通ろうとしたが、ICカードが手元にない。
ホームのどこかに手がかりがあるはずだ——

## 必要環境

- Python 3.10 以上
- macOS / Linux（readline 依存のため Windows は非対応）

## 起動方法

```bash
python main.py
```

## 操作方法

コマンドは **`動詞-名詞`** の形式で入力します（PowerShell 風）。

| コマンド例 | 説明 |
|---|---|
| `Examine-Bench` | ベンチを調べる |
| `Take-Locker-key` | ロッカーの鍵を拾う |
| `Go-Locker` | コインロッカーへ移動する |
| `Use-Ic-card` | ICカードを使う |
| `Help` | コマンド一覧を表示 |
| `Quit` | ゲームを終了 |

**Tab** を押すと入力中のコマンドを補完できます。

## エリア

```
改札前 ──── ベンチエリア
  │              │
  └──── コインロッカー
```

## ファイル構成

```
main.py             # ゲームループ・タイマー・イントロ/エンディング
game.py             # ゲーム状態・エリア説明・コマンド登録
console_interface.py  # Verb-Noun コマンドエンジン（Tab 補完付き）
demo.py             # console_interface の使用例
```

## console_interface の単体利用

`console_interface.py` は独立したモジュールとして利用できます。

```python
from console_interface import ConsoleInterface

cli = ConsoleInterface(prompt="adventure> ")

@cli.command("take", "ic-card")
def take_ic_card():
    print("ICカードを手に取った。")

cli.run()
```

## ライセンス

MIT License
