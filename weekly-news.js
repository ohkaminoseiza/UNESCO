/**
 * Weekly News Widget
 * GitHub上のweekly_reportsディレクトリから最新のウィークリーレポートを取得し、
 * サイドバーに「最新ニュース」として表示するスクリプト
 *
 * ファイル命名規則:
 *   日本語版: {date}_unesco_{topic}_weekly.md
 *   英語版:   {date}_unesco_{topic}_weekly_en.md
 *
 * 例:
 *   weekly_reports/ai/2026-05-10_unesco_ai_weekly.md     ← 日本語版
 *   weekly_reports/ai/2026-05-10_unesco_ai_weekly_en.md  ← 英語版
 */

(function () {
    'use strict';

    const GITHUB_API_BASE = 'https://api.github.com/repos/ohkaminoseiza/UNESCO/contents/weekly_reports';
    const GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/ohkaminoseiza/UNESCO/main/weekly_reports';

    // カテゴリ定義（フォルダ名 → 表示名）
    const CATEGORIES = {
        ai: { ja: 'AI', en: 'AI', icon: '🤖', color: '#5a67d8' },
        human_rights: { ja: '人権', en: 'Human Rights', icon: '⚖️', color: '#d69e2e' },
        environment: { ja: '環境', en: 'Environment', icon: '🌿', color: '#38a169' }
    };

    // 言語検出
    const lang = document.documentElement.lang === 'en' ? 'en' : 'ja';

    const LABELS = {
        ja: {
            title: '📰 ウィークリーニュース',
            loading: '読み込み中...',
            error: 'ニュースを取得できませんでした',
            close: '閉じる',
            sources: '情報源',
            overview: '概要',
            archive: '📂 過去のニュースを見る »'
        },
        en: {
            title: '📰 Weekly News',
            loading: 'Loading...',
            error: 'Failed to load news',
            close: 'Close',
            sources: 'Sources',
            overview: 'Overview',
            archive: '📂 View News Archive »'
        }
    };

    const labels = LABELS[lang];

    /**
     * GitHub APIからフォルダ内のファイル一覧を取得
     * 同一フォルダ内のファイル名で日英を区別:
     *   日本語版: *_weekly.md (末尾が _en.md でないもの)
     *   英語版:   *_weekly_en.md
     */
    async function fetchFileList(category) {
        const apiPath = `${GITHUB_API_BASE}/${category}`;
        const rawPath = `${GITHUB_RAW_BASE}/${category}`;

        try {
            const response = await fetch(apiPath);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const files = await response.json();
            return files
                .filter(f => {
                    if (!f.name.endsWith('.md')) return false;
                    // 英語版サイト → _en.md ファイルのみ
                    // 日本語版サイト → _en.md 以外のファイルのみ
                    const isEnglishFile = f.name.endsWith('_en.md');
                    return lang === 'en' ? isEnglishFile : !isEnglishFile;
                })
                .map(f => ({
                    name: f.name,
                    category: category,
                    date: f.name.match(/^(\d{4}-\d{2}-\d{2})/)?.[1] || '',
                    url: `${rawPath}/${f.name}`
                }))
                .sort((a, b) => b.date.localeCompare(a.date));
        } catch (e) {
            console.error(`Failed to fetch ${category} (${lang}):`, e);
            return [];
        }
    }

    /**
     * 全カテゴリのファイル一覧を取得し、日付でグループ化
     */
    async function fetchAllReports() {
        const allFiles = [];
        const promises = Object.keys(CATEGORIES).map(async (cat) => {
            const files = await fetchFileList(cat);
            allFiles.push(...files);
        });
        await Promise.all(promises);

        // 日付でグループ化
        const grouped = {};
        allFiles.forEach(file => {
            if (!grouped[file.date]) {
                grouped[file.date] = [];
            }
            grouped[file.date].push(file);
        });

        // 日付降順でソート
        const sortedDates = Object.keys(grouped).sort((a, b) => b.localeCompare(a));
        return { grouped, sortedDates };
    }

    /**
     * Markdownファイルの内容を取得
     */
    async function fetchMarkdownContent(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.text();
    }

    /**
     * 簡易Markdownパーサー（HTMLに変換）
     */
    function parseMarkdown(md) {
        let html = md
            // コードブロック（先に処理）
            .replace(/```[\s\S]*?```/g, match => {
                const code = match.replace(/```\w*\n?/g, '').replace(/```/g, '');
                return `<pre><code>${escapeHtml(code)}</code></pre>`;
            })
            // 見出し
            .replace(/^### (.+)$/gm, '<h4>$1</h4>')
            .replace(/^## (.+)$/gm, '<h3 class="weekly-news-h3">$1</h3>')
            .replace(/^# (.+)$/gm, '<h2 class="weekly-news-h2">$1</h2>')
            // 水平線
            .replace(/^---+$/gm, '<hr class="weekly-news-hr">')
            // 太字
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // リンク
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
            // リスト項目
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            // 段落
            .replace(/\n\n/g, '</p><p>')
            // 改行
            .replace(/\n/g, '<br>');

        // li要素をulで囲む
        html = html.replace(/((?:<li>.*?<\/li><br>?)+)/g, '<ul>$1</ul>');
        html = html.replace(/<br><\/ul>/g, '</ul>');
        html = html.replace(/<ul><br>/g, '<ul>');

        return `<div class="weekly-news-content"><p>${html}</p></div>`;
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /**
     * 日付を表示形式に変換
     */
    function formatDate(dateStr) {
        const [year, month, day] = dateStr.split('-');
        if (lang === 'ja') {
            return `${year}年${parseInt(month)}月${parseInt(day)}日`;
        }
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[parseInt(month) - 1]} ${parseInt(day)}, ${year}`;
    }

    /**
     * モーダルを作成
     */
    function createModal() {
        const overlay = document.createElement('div');
        overlay.id = 'weekly-news-overlay';
        overlay.innerHTML = `
            <div class="weekly-news-modal">
                <div class="weekly-news-modal-header">
                    <h3 id="weekly-news-modal-title"></h3>
                    <button class="weekly-news-close-btn" aria-label="${labels.close}">&times;</button>
                </div>
                <div class="weekly-news-modal-body" id="weekly-news-modal-body">
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // 閉じるボタン
        overlay.querySelector('.weekly-news-close-btn').addEventListener('click', closeModal);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });

        // ESCキーで閉じる
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    }

    function openModal(title, content) {
        const overlay = document.getElementById('weekly-news-overlay');
        document.getElementById('weekly-news-modal-title').textContent = title;
        document.getElementById('weekly-news-modal-body').innerHTML = content;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        const overlay = document.getElementById('weekly-news-overlay');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * カテゴリレポートをクリックしたときの処理
     */
    async function handleReportClick(file) {
        const catInfo = CATEGORIES[file.category];
        const catName = catInfo[lang];
        const title = `${catInfo.icon} ${catName} - ${formatDate(file.date)}`;

        openModal(title, `<p style="text-align:center; padding: 40px 0; color:#718096;">${labels.loading}</p>`);

        try {
            const md = await fetchMarkdownContent(file.url);
            const html = parseMarkdown(md);
            document.getElementById('weekly-news-modal-body').innerHTML = html;
        } catch (e) {
            document.getElementById('weekly-news-modal-body').innerHTML =
                `<p style="text-align:center; padding: 40px 0; color:#e53e3e;">${labels.error}</p>`;
        }
    }

    /**
     * サイドバーにウィジェットを構築
     */
    function buildWidget(data) {
        const { grouped, sortedDates } = data;

        const widget = document.createElement('div');
        widget.className = 'widget weekly-news-widget';
        widget.innerHTML = `<h3 class="widget-title">${labels.title}</h3>`;

        const list = document.createElement('div');
        list.className = 'weekly-news-list';

        // 約2か月分（9週）まで表示
        const twoMonthsAgo = new Date();
        twoMonthsAgo.setMonth(twoMonthsAgo.getMonth() - 2);
        const cutoffDate = twoMonthsAgo.toISOString().slice(0, 10);

        const displayDates = sortedDates.filter(date => date >= cutoffDate);
        const hasOlderDates = sortedDates.length > displayDates.length;

        displayDates.forEach(date => {
            const dateGroup = document.createElement('div');
            dateGroup.className = 'weekly-news-date-group';

            const dateLabel = document.createElement('div');
            dateLabel.className = 'weekly-news-date-label';
            dateLabel.textContent = formatDate(date);
            dateGroup.appendChild(dateLabel);

            const items = document.createElement('div');
            items.className = 'weekly-news-items';

            grouped[date].forEach(file => {
                const catInfo = CATEGORIES[file.category];
                const item = document.createElement('a');
                item.className = 'weekly-news-item';
                item.href = '#';
                item.setAttribute('data-category', file.category);
                item.innerHTML = `
                    <span class="weekly-news-icon">${catInfo.icon}</span>
                    <span class="weekly-news-cat-name">${catInfo[lang]}</span>
                `;
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    handleReportClick(file);
                });
                items.appendChild(item);
            });

            dateGroup.appendChild(items);
            list.appendChild(dateGroup);
        });

        widget.appendChild(list);

        // アーカイブへのリンクを追加（常に表示）
        const archiveLink = document.createElement('div');
        archiveLink.className = 'weekly-news-archive-link';
        const archivePath = lang === 'en' ? 'en/weekly-news-archive.html' : 'weekly-news-archive.html';
        // 英語版ページからの相対パス補正
        const isSubDir = window.location.pathname.includes('/en/');
        const href = isSubDir && lang === 'en' ? 'weekly-news-archive.html' : archivePath;
        archiveLink.innerHTML = `<a href="${href}">${labels.archive}</a>`;
        widget.appendChild(archiveLink);

        return widget;
    }

    /**
     * ローディング中のプレースホルダーウィジェットを表示
     */
    function buildLoadingWidget() {
        const widget = document.createElement('div');
        widget.className = 'widget weekly-news-widget';
        widget.id = 'weekly-news-loading-widget';
        widget.innerHTML = `
            <h3 class="widget-title">${labels.title}</h3>
            <div class="weekly-news-loading">
                <div class="weekly-news-spinner"></div>
                <p>${labels.loading}</p>
            </div>
        `;
        return widget;
    }

    /**
     * CSSスタイルを注入
     */
    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* ===== Weekly News Widget ===== */
            .weekly-news-widget {
                border-top: 3px solid #2c5282;
                background: linear-gradient(to bottom, #f7fafc, #ffffff);
            }

            .weekly-news-loading {
                text-align: center;
                padding: 20px 0;
                color: #718096;
            }

            .weekly-news-spinner {
                width: 24px;
                height: 24px;
                border: 3px solid #e2e8f0;
                border-top-color: #2c5282;
                border-radius: 50%;
                margin: 0 auto 10px;
                animation: weekly-news-spin 0.8s linear infinite;
            }

            @keyframes weekly-news-spin {
                to { transform: rotate(360deg); }
            }

            .weekly-news-date-group {
                margin-bottom: 14px;
                padding-bottom: 14px;
                border-bottom: 1px dashed #e2e8f0;
            }

            .weekly-news-date-group:last-child {
                margin-bottom: 0;
                padding-bottom: 0;
                border-bottom: none;
            }

            .weekly-news-date-label {
                font-size: 0.82rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 8px;
                letter-spacing: 0.02em;
            }

            .weekly-news-items {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
            }

            .weekly-news-item {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                padding: 4px 10px;
                background: #ebf8ff;
                border: 1px solid #bee3f8;
                border-radius: 20px;
                font-size: 0.8rem;
                color: #2c5282;
                text-decoration: none !important;
                transition: all 0.2s ease;
                cursor: pointer;
            }

            .weekly-news-item:hover {
                background: #2c5282;
                color: #ffffff !important;
                border-color: #2c5282;
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(44, 82, 130, 0.3);
                text-decoration: none !important;
            }

            .weekly-news-item:hover .weekly-news-cat-name {
                color: #ffffff;
            }

            .weekly-news-icon {
                font-size: 0.9rem;
            }

            .weekly-news-cat-name {
                font-weight: 500;
                transition: color 0.2s ease;
            }

            /* ===== Archive Link ===== */
            .weekly-news-archive-link {
                margin-top: 16px;
                padding-top: 14px;
                border-top: 1px dashed #e2e8f0;
                text-align: center;
            }

            .weekly-news-archive-link a {
                display: inline-block;
                font-size: 0.82rem;
                font-weight: 600;
                color: #2c5282;
                text-decoration: none;
                padding: 6px 16px;
                border: 1px solid #bee3f8;
                border-radius: 6px;
                background: #ebf8ff;
                transition: all 0.2s ease;
            }

            .weekly-news-archive-link a:hover {
                background: #2c5282;
                color: #ffffff;
                border-color: #2c5282;
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(44, 82, 130, 0.3);
            }

            /* ===== Modal Overlay ===== */
            #weekly-news-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(4px);
                z-index: 10000;
                justify-content: center;
                align-items: flex-start;
                padding: 40px 20px;
                overflow-y: auto;
            }

            #weekly-news-overlay.active {
                display: flex;
            }

            .weekly-news-modal {
                background: #ffffff;
                border-radius: 12px;
                max-width: 800px;
                width: 100%;
                max-height: 85vh;
                display: flex;
                flex-direction: column;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: weekly-news-modal-in 0.3s ease;
            }

            @keyframes weekly-news-modal-in {
                from {
                    opacity: 0;
                    transform: translateY(-20px) scale(0.98);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            .weekly-news-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 28px;
                border-bottom: 1px solid #e2e8f0;
                background: linear-gradient(135deg, #ebf8ff, #f7fafc);
                border-radius: 12px 12px 0 0;
            }

            .weekly-news-modal-header h3 {
                margin: 0;
                font-size: 1.15rem;
                color: #2d3748;
            }

            .weekly-news-close-btn {
                background: none;
                border: none;
                font-size: 1.8rem;
                color: #a0aec0;
                cursor: pointer;
                padding: 0 4px;
                line-height: 1;
                transition: color 0.2s ease;
            }

            .weekly-news-close-btn:hover {
                color: #e53e3e;
            }

            .weekly-news-modal-body {
                padding: 28px;
                overflow-y: auto;
                line-height: 1.8;
                color: #333;
            }

            /* ===== Modal Content Styling ===== */
            .weekly-news-content h2.weekly-news-h2 {
                font-size: 1.3rem;
                color: #2d3748;
                margin: 0 0 16px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid #2c5282;
            }

            .weekly-news-content h3.weekly-news-h3 {
                font-size: 1.1rem;
                color: #2c5282;
                margin: 24px 0 12px 0;
                padding-left: 12px;
                border-left: 3px solid #2c5282;
            }

            .weekly-news-content h4 {
                font-size: 1rem;
                color: #4a5568;
                margin: 16px 0 8px 0;
            }

            .weekly-news-content hr.weekly-news-hr {
                border: none;
                border-top: 1px solid #e2e8f0;
                margin: 24px 0;
            }

            .weekly-news-content a {
                color: #2c5282;
                text-decoration: underline;
                word-break: break-all;
            }

            .weekly-news-content a:hover {
                color: #4299e1;
            }

            .weekly-news-content ul {
                padding-left: 20px;
                margin: 12px 0;
            }

            .weekly-news-content li {
                margin-bottom: 6px;
                line-height: 1.6;
            }

            .weekly-news-content strong {
                color: #2d3748;
            }

            .weekly-news-content pre {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px;
                overflow-x: auto;
                font-size: 0.85rem;
            }

            /* ===== Responsive ===== */
            @media screen and (max-width: 768px) {
                #weekly-news-overlay {
                    padding: 20px 10px;
                }

                .weekly-news-modal {
                    max-height: 90vh;
                }

                .weekly-news-modal-header {
                    padding: 16px 20px;
                }

                .weekly-news-modal-body {
                    padding: 20px;
                }

                .weekly-news-modal-header h3 {
                    font-size: 1rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * 初期化
     */
    async function init() {
        injectStyles();
        createModal();

        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        // ローディングウィジェットを最新記事の上に挿入
        const loadingWidget = buildLoadingWidget();
        sidebar.insertBefore(loadingWidget, sidebar.firstChild);

        try {
            const data = await fetchAllReports();
            const newsWidget = buildWidget(data);

            // ローディングウィジェットを実際のウィジェットに置換
            loadingWidget.replaceWith(newsWidget);
        } catch (e) {
            console.error('Weekly news widget error:', e);
            loadingWidget.innerHTML = `
                <h3 class="widget-title">${labels.title}</h3>
                <p style="color: #718096; font-size: 0.85rem; text-align:center;">${labels.error}</p>
            `;
        }
    }

    // DOMの準備ができたら実行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
