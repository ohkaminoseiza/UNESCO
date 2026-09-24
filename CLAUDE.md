# このリポジトリで作業するAIへの指示

サイト: https://ohkaminoseiza.github.io/UNESCO/ （GitHub Pages、`main` ブランチを公開）
全体の仕組みは `SYSTEM-GUIDE.md` を参照。

## 原稿と生成物の区別（最重要）

- 週次レポートの原稿は `weekly_reports/` の Markdown **だけ**。内容の修正は必ず原稿を直す。
- 次のものは `scripts/build_weekly.py` が原稿から自動生成する。**直接編集しない**（次回のビルドで消える）。
  - `weekly/` と `en/weekly/` 以下のすべて
  - `index.html` と `en/index.html` の `<!-- BEGIN GENERATED ... -->` 〜 `<!-- END GENERATED ... -->` の範囲
- 生成ページのデザイン・構成を変えるときは `templates/weekly/layout.html`、`scripts/build_weekly.py`、`style.css` を直す。
- 原稿を push すると GitHub Actions（`.github/workflows/build-weekly.yml`）が HTML を生成してコミットする。手元で確認するときは `pip install -r scripts/requirements.txt` のあと `python3 scripts/build_weekly.py` を実行する。

## ファイル名と書式（違うと公開されない）

- 保存先: `weekly_reports/{ai|human_rights|environment}/YYYY-MM-DD_unesco_{ai|human_rights|environment}_weekly.md`（英語版は末尾 `_weekly_en.md`）
- 1行目は必ず `# ` で始まるタイトル。日付はファイル名の日付がそのまま公開日付になる。
- 日本語版は `## 概要`、英語版は `## Overview` を最初の見出しにする（冒頭段落が一覧・検索結果の説明文になる）。
- 各項目は `## 項目名` の下に `**公開日:**` / `**情報源:**`（英語 `**Date:**` / `**Source:**`）を1行ずつ書く。
- 生の HTML タグは書かない（ビルド時に無効化される）。

## 品質基準（「毎週出すこと」より「信頼できるものだけ出すこと」を優先）

1. 原則として一次資料（unesco.org、ioc.unesco.org、whc.unesco.org など公式ページ）を使う。検索結果の要約文だけで書かない。
2. 本文を実際に開いて確認できた記事だけを掲載する。本文を取得できなかった記事は、タイトルから内容を推測して要約しない（掲載しないか、「本文未確認」と明記する）。
3. 年月日・金額・人数・国数には根拠となる記事を付け、原文の数字をそのまま使う。開催前の「見込み」と開催後の「実績」を混同しない。
4. 時制を正確に書く。「署名予定」「採択見込み」「開幕予定」を「署名した」「採択された」と書かない。
5. 記事にない解釈（例:「人権の観点から重要」）を加えるときは、記事の記述ではないことが分かるように書く。
6. 公開日が対象週の外の記事は原則載せない。載せる場合は公開日と「対象週外」であることを明記する。
7. 原文を転載せず要約する。引用は短く、引用符で示す。
8. 情報が不足する週は無理に項目を増やさず、「今週は確認できた新着情報がありませんでした」と書く（日英とも）。
9. 公開後に誤りが分かったら原稿を修正し、末尾に `*訂正（YYYY-MM-DD）：…*`（英語 `*Correction (YYYY-MM-DD): ...*`）を追記する。

## 情報取得できなかった場合

- unesco.org が 403/503 を返すときは時間をおいて再取得し、それでも失敗した記事は上記2に従う。
- 全テーマで情報源に一切アクセスできなかった場合は、推測でレポートを作らず、作成を見送った旨を報告する。
