# フェーズ1：要件定義・設計
WP	名称	目的	主な成果物
WP1-1	機能要件定義	システムの全機能と制約を明確化	機能要件一覧（v2表） __close__
WP1-2	非機能要件定義	応答時間、精度、信頼性、倫理など定義	非機能要件定義書 __close__
WP1-3	システム構成設計	Geminiを中心としたモジュール構成を定義	構成図・データフロー図（DFD）__close__
WP1-4	API仕様設計	各機能の入出力形式、Gemini連携I/F仕様	API仕様書（OpenAPI形式推奨）
# フェーズ2：コアAIモジュール構築
WP	名称	目的	使用技術・API	入力	出力
WP2-1	対話理解モジュール	ユーザー発話をテキスト／音声から解析	Gemini API（LLM）＋ Whisper API（音声→テキスト）＋ MeCab/SudachiPy	音声 or テキスト	意図（Intent）・感情・主張構造 __close__
WP2-2	論争解析モジュール	双方の発言を比較・分類・論点化	Gemini（自然言語推論）＋ BERT分類	双方発言ログ	論点リスト＋対立関係図（JSON形式） __close__
WP2-3	法令知識ベース連携	関連法条文を検索・要約	e-Gov法令API / OpenLaw API	抽出論点	関連条文・要約文
WP2-4	過失割合算出モジュール	双方行動を定量評価（AI学習）	Gemini API + scikit-learn モデル	論点＋行動ログ	過失割合（例：夫60%、妻40%）
WP2-5	折衷案生成モジュール	中立的和解案を生成	Gemini生成API + 感情制御プロンプト	双方主張＋過失割合	折衷提案文（テキスト／音声）
# フェーズ3：感情・倫理処理層
WP	名称	目的	使用技術/API	入力	出力
WP3-1	感情分析・中和モジュール	感情的文面を検出し中立文へ変換	Gemini + Emotion Lexicon + BERT感情分類	テキスト	トーン修正版
WP3-2	倫理フィルタリングモジュール	不適切発言・差別・政治宗教発言除去	Gemini＋独自ポリシーフィルタ	応答候補	安全フィルタ済テキスト
WP3-3	倫理ルールベース更新機能	倫理ルールの自動チューニング	Python + JSONルールDB	学習結果	更新ルールファイル
# フェーズ4：音声・UIインタフェース層
WP	名称	目的	使用技術/API	入力	出力
WP4-1	音声認識・変換機能	音声入力を自然言語化	Whisper API / Google Speech-to-Text	音声	テキスト
WP4-2	音声合成機能	折衷案や説明を自然音声で返す	VoiceVox / OpenAI TTS	テキスト	音声出力（wav/mp3）
WP4-3	UI/UX設計モジュール	Web上で論争・提案を体験可能に	React + TailwindCSS + Node.js	対話イベント	表示UI＋グラフ出力
WP4-4	感情ビジュアル化機能	対話時の感情・過失割合を可視化	Chart.js / D3.js	感情＋過失割合	可視化チャート
# フェーズ5：セキュリティ・データ層
WP	名称	目的	使用技術	入力	出力
WP5-1	ログ保存・匿名化機能	対話履歴を暗号化保存	MongoDB + AES-256 + JWT	対話データ	暗号化ログ
WP5-2	ユーザー認証・アクセス管理	認証と利用制限	Firebase Auth / OAuth2	ログイン情報	セッショントークン
WP5-3	法令データ同期機能	e-Gov APIの法令更新を定期取得	Cron + Python + e-Gov API	更新情報	ローカル法令DB更新
WP5-4	バックアップ・障害復旧	安定稼働のための復旧体制構築	AWS S3 / Lambda	システム状態	バックアップファイル
# フェーズ6：評価・学習・改善
WP	名称	目的	使用技術/API	入力	出力
WP6-1	利用データ分析モジュール	提案結果・利用傾向を統計処理	Python + Pandas + Plotly	ログDB	レポート
WP6-2	AI性能チューニング	Geminiプロンプト最適化／Fine-tuning	Gemini API + RLHF手法	過去応答	改良モデルプロンプト
WP6-3	ABテストモジュール	提案アルゴリズム比較検証	Flask API + Gemini	テストケース	精度比較表
# フェーズ7：展開・運用
WP	名称	目的	使用技術	成果物
WP7-1	デプロイメント構築	本番環境の構築・CI/CD整備	Docker + Kubernetes + GitHub Actions	本番稼働環境
WP7-2	モニタリング・ログ監視	稼働状況・エラー監視	Prometheus + Grafana	稼働レポート
WP7-3	継続学習とモデル更新	新しいデータで継続学習	Gemini API + AutoML	定期更新モデル


**Gemini の位置づけ（中核モジュール**

Gemini は riri システムの「中枢AI（脳）」として以下の役割を担います：

フェーズ	役割	出力形式
対話理解（WP2-1）	意図・感情・文脈抽出	JSON {intent, emotion, topics}
論争解析（WP2-2）	対立構造のマッピング	JSON {issue_map, arguments}
折衷案生成（WP2-5）	法的・心理的にバランスした提案	テキスト {proposal_text}
感情制御（WP3-1）	中立トーン再構成	テキスト {neutralized_text}
学習改善（WP6-2）	プロンプト最適化・行動学習	JSON {prompt_revision}








# ワークパッケージ構成（優先度＋依存関係付き詳細分割） ―
# フェーズ1：要件定義・全体設計（最優先）
WP	名称	内容	優先度	依存関係	主要成果物
WP1-1	機能要件定義	機能一覧・入出力整理	🔴P1	―	機能要件仕様書
WP1-2	非機能要件定義	性能・倫理・可用性など設定	🔴P1	WP1-1	非機能要件仕様書
WP1-3	システム構成設計	Geminiを中枢とする構成図作成	🔴P1	WP1-1, WP1-2	システム構成図（DFD）
WP1-4	API仕様設計	各機能モジュール間のI/F定義（JSONスキーマ含む）	🟠P2	WP1-3	API仕様書（OpenAPI形式）
WP1-5	法令データ要件定義	利用範囲・対象法令・同期頻度定義	🟠P2	WP1-1	法令DB仕様書
# フェーズ2：AI中核モジュール構築（最重要段階）
2.1 対話理解系
WP	名称	内容	優先度	依存関係	主なAPI／技術
WP2-1	入力解析（音声→テキスト）	Whisper・Google STTで音声変換	🔴P1	WP1-4	Whisper API
WP2-2	意図・感情抽出	Gemini + MeCabによる文解析	🔴P1	WP2-1	Gemini API, SudachiPy
WP2-3	主張構造化	発話を主張・根拠・要求に分類	🟠P2	WP2-2	Gemini構造解析Prompt
2.2 論争解析系
WP	名称	内容	優先度	依存関係	主なAPI／技術
WP2-4	論点マッピング	双方発言から対立軸を抽出	🔴P1	WP2-3	Gemini + BERT自然言語推論
WP2-5	立場比較	各発言の感情傾向・法的妥当性比較	🟠P2	WP2-4	Gemini論理比較Prompt
WP2-6	過失割合推定	学習済MLモデルで責任分担算出	🔴P1	WP2-4	scikit-learn + Gemini補助計算
2.3 法令・知識連携系
WP	名称	内容	優先度	依存関係	主なAPI／技術
WP2-7	法令検索	e-Gov APIによる法条文取得	🟡P3	WP1-5	e-Gov API
WP2-8	条文要約	Geminiで法令を一般語に変換	🟡P3	WP2-7	Gemini Summarizer
WP2-9	判例学習	判例データから過失割合の学習セット構築	🟢P4	WP2-6	scikit-learn, pandas
2.4 折衷案生成系
WP	名称	内容	優先度	依存関係	主なAPI／技術
WP2-10	折衷案生成	Geminiで中立的提案文を生成	🔴P1	WP2-6, WP2-8	Gemini生成API
WP2-11	感情調整	感情トーンを中立化	🟠P2	WP2-10	Gemini感情プロンプト
WP2-12	最終提案統合	提案文・過失・法令を統合して出力	🔴P1	WP2-10, WP2-11	JSON出力モジュール
# フェーズ3：感情・倫理制御層（AIガバナンス）
WP	名称	内容	優先度	依存関係	技術
WP3-1	感情フィルタリング	感情的・攻撃的表現を削除	🔴P1	WP2-2	Gemini + Emotion Lexicon
WP3-2	倫理監視・制御	差別・宗教・政治・暴力ワード除去	🔴P1	WP3-1	Gemini + JSONルールDB
WP3-3	倫理ルール自動更新	フィードバックに基づくルール強化	🟡P3	WP3-2	Pythonルール生成器
# フェーズ4：UI/UX & 音声レイヤ
WP	名称	内容	優先度	依存関係	技術／API
WP4-1	音声出力	提案文を自然音声化	🟡P3	WP2-12	VoiceVox / OpenAI TTS
WP4-2	WebチャットUI	対話・法令表示・可視化	🟠P2	WP2-12	React + TailwindCSS
WP4-3	感情可視化	感情や過失割合をグラフで表示	🟢P4	WP2-6	Chart.js / D3.js
WP4-4	対話履歴閲覧	ユーザーが自分の過去論争を確認	🟢P4	WP5-1	React + MongoDB接続
# フェーズ5：セキュリティ・データ管理
WP	名称	内容	優先度	依存関係	技術
WP5-1	対話データ暗号化	AES-256で会話ログを保護	🔴P1	WP2-12	MongoDB + AES
WP5-2	ユーザー認証	Firebase Auth / OAuth2	🟠P2	WP5-1	Firebase SDK
WP5-3	法令DB同期	e-Gov法令APIの定期取得	🟢P4	WP2-7	Cron + Python
WP5-4	障害復旧・バックアップ	冗長化・リカバリ設定	🟡P3	WP5-1	AWS Lambda / S3
# フェーズ6：学習・改善・評価
WP	名称	内容	優先度	依存関係	技術
WP6-1	精度評価	過失割合・感情精度検証	🟠P2	WP2-6	scikit-learn評価
WP6-2	Geminiプロンプト最適化	RLHF的チューニング	🟡P3	WP6-1	Gemini API
WP6-3	利用傾向分析	データ傾向可視化	🟢P4	WP5-1	Pandas + Plotly
WP6-4	ABテスト	折衷アルゴリズム比較	🟢P4	WP2-10	Flask + Gemini
# フェーズ7：展開・運用・CI/CD
WP	名称	内容	優先度	依存関係	技術
WP7-1	コンテナ構築	Dockerイメージ化	🔴P1	WP1-3, WP2-12	Docker
WP7-2	デプロイ設定	本番環境構築・CI/CD	🟠P2	WP7-1	GitHub Actions + Kubernetes
WP7-3	監視・アラート	稼働状況監視	🟢P4	WP7-2	Prometheus + Grafana
WP7-4	継続学習更新	定期的モデル更新	🟢P4	WP6-2	AutoML + Gemini
📊 優先度凡例
色	優先度	内容
🔴P1	最優先（MVP必須） — システムの根幹を構成する機能	
🟠P2	高優先 — 実用レベルで必要な要素	
🟡P3	中優先 — 運用・信頼性を高める要素	
🟢P4	拡張フェーズ — UX改善・高度化機能	
🔗 主要依存関係マップ（簡易）
WP1-* → WP2-1〜WP2-12 → WP3-* → WP4-* → WP5-* → WP6-* → WP7-*


※特に重要な直列依存：

WP2-2（意図分析） → WP2-4（論点マッピング） → WP2-6（過失割合） → WP2-10（折衷案生成）

WP5-1（暗号化） → WP5-2（認証） → WP6-3（分析）

🧾 出力仕様まとめ（主要モジュール）
モジュール	出力形式	内容例
対話解析（Gemini）	JSON	{intent, emotion, topics}
論争解析	JSON	{issue_map, argument_pairs}
過失割合推定	JSON	{husband: 0.6, wife: 0.4}
折衷案生成	TEXT	"家事の一部を夫が担当する案を提案します。"
UI出力	HTML/JSON	感情チャート・法令リンク付き出力