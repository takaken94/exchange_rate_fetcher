import json
from pathlib import Path

def migrate_files(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 旧形式のファイルをすべて取得
    old_files = list(input_path.glob("*.json"))
    print(f"{len(old_files)} 件のファイルを変換します...")

    for file_path in old_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                print(f"スキップ (JSON不正): {file_path.name}")
                continue

        # 変換ロジック
        base_date_str = old_data["date"]  # "2026-01-22"
        base_currency = old_data["base"]
        fetched_at = old_data["fetched_at"]

        # ファイル名用の日付文字列を作成 ("2026-01-22" -> "20260122")
        yyyymmdd = base_date_str.replace("-", "")
        new_filename = f"rates_{yyyymmdd}.json"

        new_records = []
        for currency, rate in old_data["rates"].items():
            record = {
                "base_date": base_date_str,
                "base": base_currency,
                "currency": currency,
                "rate": rate,
                "fetched_at": fetched_at
            }
            new_records.append(json.dumps(record, ensure_ascii=False))

        # JSON Lines 形式で保存（既存ファイルがあれば上書き）
        save_path = output_path / new_filename
        with open(save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_records) + "\n")

        print(f"変換完了: {file_path.name} -> {new_filename}")

if __name__ == "__main__":
    # フォルダ名は環境に合わせて調整してください
    input_dir = "./data/old_format"
    output_dir = "./data/new_format"
    migrate_files(input_dir=input_dir, output_dir=output_dir)