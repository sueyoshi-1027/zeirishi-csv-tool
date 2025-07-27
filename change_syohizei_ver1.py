import streamlit as st
import csv
import unicodedata
import io

def normalize(text):
    return unicodedata.normalize('NFKC', text.strip())

def load_rules(file_obj):
    rules = {}
    # アップロードファイルはバイトストリームなのでテキストIOに変換
    decoded = io.TextIOWrapper(file_obj, encoding='cp932')
    reader = csv.reader(decoded)
    header = next(reader)
    for row in reader:
        kamoku = normalize(row[0])
        hojo = normalize(row[1])
        for i in range(2, len(row), 2):
            if i + 1 < len(row):
                bumon = normalize(row[i])
                kubun = normalize(row[i+1])
                if bumon:
                    key = (kamoku, hojo, bumon)
                    rules[key] = kubun
    return rules

def apply_rule(row, rules):
    debit_kamoku = normalize(row[4])
    debit_hojo = normalize(row[5])
    debit_bumon = normalize(row[6])
    debit_key = (debit_kamoku, debit_hojo, debit_bumon)
    if debit_key in rules:
        row[7] = rules[debit_key]

    credit_kamoku = normalize(row[10])
    credit_hojo = normalize(row[11])
    credit_bumon = normalize(row[12])
    credit_key = (credit_kamoku, credit_hojo, credit_bumon)
    if credit_key in rules:
        row[13] = rules[credit_key]

    return row

st.title("CSV処理アプリ")

uploaded_journal = st.file_uploader("仕訳ファイルをアップロードしてください", type="csv")
uploaded_rules = st.file_uploader("ルールCSVファイルをアップロードしてください", type="csv")

if uploaded_journal is not None and uploaded_rules is not None:
    # ルールを読み込む
    rules = load_rules(uploaded_rules)

    # 仕訳ファイルを読み込む
    decoded_journal = io.TextIOWrapper(uploaded_journal, encoding='cp932')
    reader = csv.reader(decoded_journal)
    rows = list(reader)

    new_rows = []
    for row in rows:
        if len(row) >= 15:
            new_row = apply_rule(row, rules)
            new_rows.append(new_row)
        else:
            new_rows.append(row)

    # 加工結果を表示
    st.write("処理済みデータ：")
    st.dataframe(new_rows)

    # ファイル出力用にバイトストリーム作成
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(new_rows)
    processed_csv = output.getvalue()

    # ダウンロードボタン表示
    st.download_button(
        label="処理済みCSVをダウンロード",
        data=processed_csv,
        file_name="output.csv",
        mime="text/csv"
    )
