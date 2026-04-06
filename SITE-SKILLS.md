# UNESCOサイト構築スキルまとめ

作成日: 2026年4月5日
対象: `/Users/ishiiwahei/git/UNESCO/` 以下のサイト全体

---

## 1. サイト設計・構造管理

### フォルダ構成
```
UNESCO/
├── index.html               # 日本語トップページ
├── ai.html                  # AI記事一覧
├── environment.html         # 環境記事一覧
├── human-rights.html        # 人権記事一覧
├── resources.html           # 学習資料ページ
├── style.css                # 共通スタイル
├── images/                  # 画像フォルダ
├── posts/                   # 日本語記事
├── archive/
│   └── index.html           # 日本語アーカイブ
├── en/                      # 英語版（日本語版と並列）
│   ├── index.html
│   ├── ai.html
│   ├── environment.html
│   ├── human-rights.html
│   ├── resources.html
│   ├── posts/               # 英語記事
│   └── archive/
│       └── index.html       # 英語アーカイブ
├── reference/               # 参照資料（PDF・TXTなど）
├── _ai-content/             # AIテーマ作業フォルダ
│   └── CLAUDE.md
├── _environment-content/    # 環境テーマ作業フォルダ
│   └── CLAUDE.md
├── _human-rights-content/   # 人権テーマ作業フォルダ
│   └── CLAUDE.md
└── _link-check/             # リンク整合性チェック用フォルダ
    └── CLAUDE.md
```

### 日英バイリンガル構造のルール
- 日本語版はルート直下、英語版は `en/` フォルダ以下に配置
- CSSは共通（英語版は `../style.css`、英語記事は `../../style.css`）
- 画像は共通（英語版から `../images/` で参照）
- 言語切替リンク: 日本語版に `en/index.html`、英語版に `../index.html` を設置

---

## 2. 相対パスの早見表

| ファイルの場所 | style.css | トップページ | 記事フォルダ |
|---|---|---|---|
| ルート直下 (`*.html`) | `style.css` | `index.html` | `posts/` |
| `posts/*.html` | `../style.css` | `../index.html` | （同階層） |
| `en/*.html` | `../style.css` | `index.html` | `posts/` |
| `en/posts/*.html` | `../../style.css` | `../index.html` | （同階層） |
| `archive/index.html` | `../style.css` | `../index.html` | `../posts/` |
| `en/archive/index.html` | `../../style.css` | `../index.html` | `../posts/` |

---

## 3. 新しい記事を追加するときの手順

### ステップ1: 記事HTMLを作成
- 日本語: `posts/記事ファイル名.html`
- 英語: `en/posts/記事ファイル名.html`（同じファイル名を使う）

### ステップ2: テーマ別一覧ページに追加
- 対象: `ai.html` / `environment.html` / `human-rights.html`
- 英語版: `en/ai.html` / `en/environment.html` / `en/human-rights.html`
- 一覧の **先頭**（最新順）に追加する

### ステップ3: トップページの Top News セクションに追加
- `index.html` の `<section class="top-news">` 内に `<article class="news-article">` ブロックを追加
- `en/index.html` にも同様に英語版ブロックを追加
- **最新記事が一番上**になるよう順序を管理する
- 記事が増えた場合は古い記事を下へ移動し、複数記事を並べて表示できる

#### Top News の記事ブロック（日本語版テンプレート）
```html
<article class="news-article">
    <h3><a href="posts/ファイル名.html">記事タイトル</a></h3>
    <p class="article-meta">YYYY年M月D日 | テーマ, 教育</p>
    <p class="article-summary">
        記事の要約文（2〜3文程度）
    </p>
    <a href="posts/ファイル名.html" class="read-more">続きを読む &raquo;</a>
</article>
```

#### Top News の記事ブロック（英語版テンプレート）
```html
<article class="news-article">
    <h3><a href="posts/ファイル名.html">Article Title</a></h3>
    <p class="article-meta">Month D, YYYY | Theme, Education</p>
    <p class="article-summary">
        Summary of the article (2–3 sentences).
    </p>
    <a href="posts/ファイル名.html" class="read-more">Read More &raquo;</a>
</article>
```

### ステップ4: トップページのサイドバーを更新
- `index.html` の「最新記事」ウィジェット（最新順、上から追加）
- `en/index.html` の「Latest Articles」ウィジェット（同様）

### ステップ5: アーカイブページに追加
- `archive/index.html` の該当月のリストに追加（最新順）
- `en/archive/index.html` にも同様に追加

---

## 4. コンテンツ作成のワークフロー

```
① referenceフォルダのPDF・TXTを参照
      ↓
② _ai-content/ などのタスクフォルダにMarkdownで下書き作成
   （日本語・英語を1ファイルにまとめる）
      ↓
③ オーナーが確認・修正・意見を追記
      ↓
④ OKが出たらHTMLファイルに反映
      ↓
⑤ 記事一覧・トップ・アーカイブを更新
```

### 下書きファイルの命名規則
```
_ai-content/draft-テーマ-YYYY-MM.md
_environment-content/draft-テーマ-YYYY-MM.md
_human-rights-content/draft-テーマ-YYYY-MM.md
```

---

## 5. リンク整合性チェックのポイント

定期的に以下を確認する（`_link-check/` タスクを使用）:

1. **ファイル対応確認** — 日本語版に存在するHTMLに対応する英語版があるか
2. **パス誤り** — `../posts/` と `posts/` の混在（特に `en/` 内のファイル）
3. **翻訳漏れ** — 英語版ページに日本語テキストが残っていないか
4. **言語切替リンク** — 日↔英の切替リンクが正しく機能するか
5. **アーカイブ更新漏れ** — 新記事がアーカイブに登録されているか

### よくあるミスと対処
| ミス | 原因 | 対処 |
|---|---|---|
| `en/ai.html` から記事が開かない | `../posts/` と書いてしまう | `posts/` に修正（`en/posts/` を指す） |
| CSSが当たらない | パスの階層ミス | 上の早見表を参照 |
| アーカイブに記事が出ない | 追加忘れ | 記事追加のステップ4を実施 |

---

## 6. CLAUDE.mdによるタスク管理

各 `_xxx-content/` フォルダの `CLAUDE.md` に以下を記載している:
- 作業の目的
- 情報源の優先順位（ユネスコ資料を主軸）
- 記事の方針
- 作業フロー
- 下書き・HTMLの保存場所

**使い方**: 「`_ai-content` のタスクを進めてください」と指示するだけで、Claude がCLAUDE.md を読んで方針を把握した上で作業する。

---

## 7. 今後の作業予定（未作成ページ）

両バージョン共通で以下が未作成:

| ページ | 日本語 | 英語 |
|---|---|---|
| サイト紹介 | `about.html` | `en/about.html` |
| アーカイブ（AI） | `archive-ai.html` | `en/archive-ai.html` |
| アーカイブ（人権） | `archive-human-rights.html` | `en/archive-human-rights.html` |
| アーカイブ（環境） | `archive-environment.html` | `en/archive-environment.html` |
