# UNESCO ウィークリーレポート自動生成システム ガイド

作成日: 2026-07-14  
更新日: 2026-09-24（B型＝公開前にHTMLを生成する方式へ移行）  
対象リポジトリ: `ohkaminoseiza/UNESCO`

---

## 1. システム全体の構成

このサイトは、毎週以下の仕組みが連携して自動更新されます（「公開前に記事ページを作る」B型）。

```
Claude (AI)
  → weekly_reports/ に Markdown 原稿を push
    → GitHub Actions (build-weekly.yml) が HTML を生成してコミット
      → GitHub Pages が公開
```

生成されるページ:

| ページ | 日本語 | 英語 |
|------|------|------|
| レポート個別ページ | `weekly/{ai,human-rights,environment}/YYYY-MM-DD.html` | `en/weekly/.../YYYY-MM-DD.html` |
| テーマ別一覧 | `weekly/{テーマ}/index.html` | `en/weekly/{テーマ}/index.html` |
| 全レポート一覧 | `weekly/index.html` | `en/weekly/index.html` |
| トップページの「最新のウィークリーレポート」とサイドバー | `index.html` の GENERATED 範囲 | `en/index.html` の GENERATED 範囲 |

各レポートは専用URLを持ち、JavaScript なしで表示され、検索エンジンにも認識されます。
旧 `weekly-news-archive.html` は `weekly/index.html` への転送ページです。

---

## 2. 各コンポーネントの役割

### Claude（AI）
- ユネスコ公式サイトを検索してAI・人権・環境の最新情報を収集する
- 日本語版・英語版のMarkdownレポートを各3本（合計6本）作成する
- `git push` でGitHubに保存する

### `weekly_reports/` フォルダ
Markdownファイルを日付別・テーマ別に蓄積するフォルダ。

```
weekly_reports/
  ai/
    YYYY-MM-DD_unesco_ai_weekly.md        ← 日本語版
    YYYY-MM-DD_unesco_ai_weekly_en.md     ← 英語版
  human_rights/
    YYYY-MM-DD_unesco_human_rights_weekly.md
    YYYY-MM-DD_unesco_human_rights_weekly_en.md
  environment/
    YYYY-MM-DD_unesco_environment_weekly.md
    YYYY-MM-DD_unesco_environment_weekly_en.md
```

### ビルド（`scripts/build_weekly.py`）
- `weekly_reports/` の Markdown を読み、上表の HTML を生成する
- ページのひな形は `templates/weekly/layout.html`、見た目は `style.css` の「8b. Weekly Reports」
- `weekly/`・`en/weekly/` は毎回まるごと作り直す。生成物は**直接編集しない**（原稿かひな形を直す）
- 命名規則に合わないファイルやタイトル行のない原稿は、警告を出して公開対象から外す／仮タイトルで公開する
- 手元での確認: `pip install -r scripts/requirements.txt` → `python3 scripts/build_weekly.py`

### GitHub Actions（`.github/workflows/build-weekly.yml`）
- `weekly_reports/` などへの push をきっかけにビルドし、生成物に変化があるときだけコミットする
- ボットのコミットは次のワークフローを起動しないため、無限ループにならない
- 失敗した場合は GitHub の「Actions」タブで確認できる。「Run workflow」から手動実行も可能

### GitHub Pages
- `main` ブランチをそのまま公開する（設定の変更は不要）

### AIへの品質ルール
- リポジトリ直下の `CLAUDE.md` に記載。Claude はこのファイルを毎回自動で読み込むため、週次の定期実行にも適用される

---

## 3. レポートの書き方ルール

### ファイル命名
| 種別 | 命名パターン |
|------|-------------|
| AI 日本語 | `weekly_reports/ai/YYYY-MM-DD_unesco_ai_weekly.md` |
| AI 英語 | `weekly_reports/ai/YYYY-MM-DD_unesco_ai_weekly_en.md` |
| 人権 日本語 | `weekly_reports/human_rights/YYYY-MM-DD_unesco_human_rights_weekly.md` |
| 人権 英語 | `weekly_reports/human_rights/YYYY-MM-DD_unesco_human_rights_weekly_en.md` |
| 環境 日本語 | `weekly_reports/environment/YYYY-MM-DD_unesco_environment_weekly.md` |
| 環境 英語 | `weekly_reports/environment/YYYY-MM-DD_unesco_environment_weekly_en.md` |

### 日本語レポートの構成
```
# ユネスコ [テーマ]ウィークリーレポート YYYY-MM-DD

## 概要
（その週の活動の要約）

## [記事タイトル]
**公開日:** YYYY年M月D日
**情報源:** URL

（2〜3文の要約）

---

## 情報源
- URL1
- URL2
```

### 英語レポートの構成
```
# UNESCO [Theme] Weekly Report YYYY-MM-DD

## Overview
(Executive summary of the week's activities)

## [Article Title]
**Date:** Month D, YYYY
**Source:** URL

(2–3 sentence summary)

---

## Sources
- URL1
- URL2
```

---

## 4. Claudeへの指示プロンプト（毎週使う）

下記をそのままClaudeに渡せば、当週のレポートが作成・コミット・プッシュされます。
`YYYY-MM-DD` は実行日の日付に置き換えてください。

---

```
あなたはリサーチエージェントです。
過去7日間のユネスコ公式情報を3つのテーマで収集し、
日本語・英語それぞれのウィークリーサマリーレポート（計6本）を作成してください。

3つのテーマ: AI（人工知能）、人権、環境

---

## テーマ1: AI（人工知能）

### 検索
- Fetch: https://www.unesco.org/en/artificial-intelligence
- Fetch: https://www.unesco.org/en/tags/artificial-intelligence
- WebSearch: site:unesco.org artificial intelligence（過去1週間でフィルタ）
- WebSearch: site:unesco.org "AI" policy OR governance OR ethics（過去1週間でフィルタ）

### 日本語レポート保存先
weekly_reports/ai/YYYY-MM-DD_unesco_ai_weekly.md

### 日本語レポートタイトル
# ユネスコ AIウィークリーレポート YYYY-MM-DD

### 英語レポート保存先
weekly_reports/ai/YYYY-MM-DD_unesco_ai_weekly_en.md

### 英語レポートタイトル
# UNESCO AI Weekly Report YYYY-MM-DD

---

## テーマ2: 人権

### 検索
- Fetch: https://www.unesco.org/en/human-rights
- Fetch: https://www.unesco.org/en/tags/human-rights
- WebSearch: site:unesco.org human rights（過去1週間でフィルタ）
- WebSearch: site:unesco.org "human rights" policy OR declaration OR education（過去1週間でフィルタ）

### 日本語レポート保存先
weekly_reports/human_rights/YYYY-MM-DD_unesco_human_rights_weekly.md

### 日本語レポートタイトル
# ユネスコ 人権ウィークリーレポート YYYY-MM-DD

### 英語レポート保存先
weekly_reports/human_rights/YYYY-MM-DD_unesco_human_rights_weekly_en.md

### 英語レポートタイトル
# UNESCO Human Rights Weekly Report YYYY-MM-DD

---

## テーマ3: 環境

### 検索
- Fetch: https://www.unesco.org/en/ecology-environment
- Fetch: https://www.unesco.org/en/tags/environment
- WebSearch: site:unesco.org environment OR ecology（過去1週間でフィルタ）
- WebSearch: site:unesco.org "climate change" OR "biodiversity" OR "sustainability"（過去1週間でフィルタ）

### 日本語レポート保存先
weekly_reports/environment/YYYY-MM-DD_unesco_environment_weekly.md

### 日本語レポートタイトル
# ユネスコ 環境ウィークリーレポート YYYY-MM-DD

### 英語レポート保存先
weekly_reports/environment/YYYY-MM-DD_unesco_environment_weekly_en.md

### 英語レポートタイトル
# UNESCO Environment Weekly Report YYYY-MM-DD

---

## 各レポートの作成手順

1. 過去7日間に公開されたアイテムをすべて収集する。
   各アイテムについてタイトル・公開日・URL・2〜3文の要約を記録する。

2. 日本語Markdownレポートを以下の構成で書く:
   - タイトル（上記の指定タイトル、YYYY-MM-DDを実際の日付に置換）
   - `## 概要` — その週の活動のエグゼクティブサマリー
   - `## [記事タイトル]` — 各アイテムのセクション（日付・要約・情報源リンク付き）
   - `## 情報源` — 全情報源URLのリスト
   - 新着情報がない場合はその旨を記載する

3. 英語Markdownレポートを以下の構成で書く:
   - タイトル（上記の指定タイトル、YYYY-MM-DDを実際の日付に置換）
   - `## Overview` — エグゼクティブサマリー
   - `## [Article Title]` — 各アイテムのセクション（日付・要約・情報源リンク付き）
   - `## Sources` — 全情報源URLのリスト
   - 新着情報がない場合はその旨を英語で記載する

4. ディレクトリが存在しない場合は作成し、両ファイルを保存する。

---

## 6本のレポートをすべて書き終えたら、以下のコマンドで1つのコミットにまとめてプッシュする:

git config user.email "claude-agent@anthropic.com"
git config user.name "Claude Agent"
git add weekly_reports/
git commit -m "Add UNESCO weekly reports YYYY-MM-DD (AI / Human Rights / Environment) [JA + EN]"
git push origin main

（YYYY-MM-DDは実際の日付に置換）
```

---

## 5. よくある注意点

| 状況 | 対処 |
|------|------|
| `unesco.org` に直接アクセスすると403/503エラー | 時間をおいて再取得する。本文を確認できない記事は、検索結果の要約やタイトルから推測して書かない（`CLAUDE.md` の品質基準2） |
| 特定記事の公開日が不明 | 「〇〇年〇月（今週）」と注記して掲載する |
| 新着情報が見つからないテーマがある | 「今週は新着情報は確認できませんでした」と日英両方で記載する |
| ディレクトリが存在しない | `mkdir -p` で作成してから保存する |
| 公開後に誤りが見つかった | 原稿を修正し、末尾に訂正の注記を追記する。HTML は自動で作り直される |
| サイトに新しいレポートが出ない | GitHub の「Actions」タブで build-weekly の結果と警告を確認する（ファイル名・タイトル行の誤りが多い） |

---

## 6. 公開までの流れ（参考）

```
Claude が weekly_reports/ に push
  → build-weekly.yml が起動し HTML を生成・コミット（数十秒〜数分）
    → GitHub Pages の pages-build-deployment がサイトに反映
```
