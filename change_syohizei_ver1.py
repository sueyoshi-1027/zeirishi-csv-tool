# app.py
import streamlit as st
import pandas as pd

st.title("CSV処理アプリ")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="cp932")
    st.write("アップロードしたデータ：")
    st.dataframe(df)

    import csv
import unicodedata

def normalize(text):
    return unicodedata.normalize('NFKC', text.strip())

def load_rules(ルールファイル):
    rules = {}
    with open(ルールファイル, newline='', encoding='cp932') as f:
        reader = csv.reader(f)
        header = next(reader)  # ← これは必要（ルールファイルにはヘッダあり）

        for row in reader:
            kamoku = normalize(row[0])
            hojo = normalize(row[1])
            for i in range(2, len(row), 2):  # 2列ずつ処理
                if i + 1 < len(row):
                    bumon = normalize(row[i])
                    kubun = normalize(row[i + 1])
                    if bumon:
                        key = (kamoku, hojo, bumon)
                        rules[key] = kubun
    return rules

def apply_rule(row, rules):
    # 借方処理
    debit_kamoku = normalize(row[4])
    debit_hojo = normalize(row[5])
    debit_bumon = normalize(row[6])
    debit_key = (debit_kamoku, debit_hojo, debit_bumon)
    if debit_key in rules:
        row[7] = rules[debit_key]  # 借方消費税区分

    # 貸方処理
    credit_kamoku = normalize(row[10])
    credit_hojo = normalize(row[11])
    credit_bumon = normalize(row[12])
    credit_key = (credit_kamoku, credit_hojo, credit_bumon)
    if credit_key in rules:
        row[13] = rules[credit_key]  # 貸方消費税区分

    return row

def process_journal(仕訳ファイル, 出力ファイル, ルールファイル):
    rules = load_rules(ルールファイル)

    with open(仕訳ファイル, newline='', encoding='cp932') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 1行目もデータなので全部処理
    new_rows = []
    for row in rows:
        if len(row) >= 15:
            new_row = apply_rule(row, rules)
            new_rows.append(new_row)
        else:
            new_rows.append(row)

    with open(出力ファイル, 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

# --- ファイル指定 ---
仕訳ファイル = 'sample.csv'
出力ファイル = 'output.csv'
ルールファイル = 'rules.csv'

process_journal(仕訳ファイル, 出力ファイル, ルールファイル)
