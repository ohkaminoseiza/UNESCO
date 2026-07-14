# UNESCO ウィークリーレポート自動生成システム ガイド

作成日: 2026-07-14  
対象リポジトリ: `ohkaminoseiza/UNESCO`

---

## 1. システム全体の構成

このサイトは、毎週日曜日に以下の4つの仕組みが連携して自動更新されます。

```
Claude (AI)
  → GitHub リポジトリ (weekly_reports/)
    → GitHub Pages (自動公開)
      → weekly-news.js (ブラウザで読み込み・表示)
```

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

### GitHub Pages
- `main` ブランチへの `git push` を検知して自動でサイトを更新する
- カスタムのYAMLファイルは不要。GitHub組み込みの `pages-build-deployment` ワークフローが動く
- HTMLファイルはそのまま公開される（ビルド処理なし）

### `weekly-news.js`
- 訪問者がページを開いた際にブラウザ上で動作する
- GitHub API（`api.github.com`）でファイル一覧を取得し、最新のMarkdownを読み込む
- ページの言語（`lang` 属性）に応じて日本語版・英語版を自動選択して表示する

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
| `unesco.org` に直接アクセスすると403エラー | WebSearchの結果を使って情報を収集する（直接FetchはできないことがあるためWebSearch優先） |
| 特定記事の公開日が不明 | 「〇〇年〇月（今週）」と注記して掲載する |
| 新着情報が見つからないテーマがある | 「今週は新着情報は確認できませんでした」と日英両方で記載する |
| ディレクトリが存在しない | `mkdir -p` で作成してから保存する |

---

## 6. GitHub Pages の仕組み（参考）

カスタムのGitHub Actions YAMLファイルは不要です。
`main` ブランチへの `git push` だけで、GitHub組み込みの `pages-build-deployment` ワークフローが自動的にサイトを更新します。

```
git push → GitHub Pages が検知 → pages-build-deployment 起動 → サイト反映
```
