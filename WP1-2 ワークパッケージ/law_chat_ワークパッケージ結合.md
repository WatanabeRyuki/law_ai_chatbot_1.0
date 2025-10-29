ステップ A — プロトタイプの縦結合（MVP早期検証）

対象 WP: WP2-1（対話理解） + WP2-2（論争解析） + WP2-3（法令KB）
目的: ユーザー発話（音声/テキスト）を入力して、「論点抽出＋関連条文の要約＋簡易折衷案（テンプレ）」が帰る最小フローを動かす。
合流点（インターフェース）:

/nlu/analyze → 出力例（JSON）

{
  "session_id":"sess-001",
  "text":"夫が家事を全然しない",
  "intent":"domestic_dispute",
  "entities":[{"type":"party","text":"夫","span":[0,1]}],
  "emotion":{"label":"anger","score":0.85}
}


/dispute/analyze (WP2-2) 入力: session_id, messages[] → 出力: topics[], issue_map

/laws/search と /laws/{id}/articles/{no}/summarize（WP2-3）
受け入れ基準（MVP）:

サンプル会話3ケースで end-to-end が成功（応答時間 p95 ≤ target）

出力 JSON が契約通りであること（schema validate）
テスト: 自動化統合テスト（pytest + TestClient）でワークフローを検証。
備考: この段階では折衷案生成はテンプレート（静的）でもOK。Gemini呼び出しはモック可能。

ステップ B — 分析強化フェーズ

対象 WP: WP2-4（過失割合算出） を上の流れに追加。
合流点: /analysis/estimate_fault を呼び、WP2-2 の issue_map を渡す。
出力例:

{ "estimates":[{"party":"husband","ratio":0.60,"confidence":0.7}, ...], "model_version":"fault-v1.0" }


受け入れ基準: 過去ラベル付きの検証セットで精度（calibration・MSE・AUCなど）を満たす。
テスト: 回帰テスト + explainability 出力（SHAP等）が返ること。

ステップ C — 折衷案生成結合

対象 WP: WP2-5（折衷案生成）を統合。Geminiを本番呼び出しで使い、analysisとlegal_refsを渡して生成。
合流点: /proposal/generate が analysis_id を受けて proposals[] を返す。
受け入れ基準: 出力に references（法令ID）と confidence が含まれること。専門家1人によるサンプルレビューで妥当判定を通す。
注意: Gemini 呼び出しはコスト高・遅延あり -> キャッシュと非同期処理を使う。

ステップ D — 感情・倫理層の組み込み

対象 WP: WP3-1 / WP3-2 を Proposal の前後に挿入（感情中和はProposal生成の前に働くことが多い）。
流れ: NLU→論争解析→過失推定→感情中和（tone adjusted facts）→Proposal生成→倫理フィルタ→出力
合流点: proposal API は tone パラメータを受け取り、返却には tone_used を含む。
受け入れ基準: 感情中和後のテキストが攻撃性低下を示す（自動メトリクス + 人間評価）。

ステップ E — UI / 音声結合

対象 WP: WP4（音声／UI）を統合し、フロント→バックのEnd-to-Endを検証。
ポイント: 音声ストリーミング（Whisper）やTTSの信頼性。リアルタイム要件がある場合は非同期処理と部分応答を考慮。
受け入れ基準: E2E音声パス（録音→ASR→解析→提案→TTS）が成功すること。ユーザーテストでUX確認。

ステップ F — セキュリティ・保存・同期結合

対象 WP: WP5 系（ログ暗号化、認証、法令同期）を全体に接続。
注意: DB schema の互換性確認、削除要求（Right-to-Delete）のAPI実装、バックアップテスト。
受け入れ基準: セキュリティ監査（脆弱性スキャン）、ログの改竄検知。

ステップ G — 学習・評価・本番化

対象 WP: WP6（評価/チューニング） + WP7（デプロイ）で運用に入れる。
ポイント: モデルバージョン管理、Canary / Blue-Green deploy、SLOに従った監視。

結合時の実務ルール（契約・運用面）

API仕様（OpenAPI）を厳格化：各WPはOpenAPI定義を持ち、mock server をCIで生成してから実装を進める。

JSON Schema を共有ライブラリ化：Pydantic models を共通パッケージで管理して互換性を担保。

バージョニング：すべての主要APIは v1 等でバージョン化。互換性の壊れる変更はメジャーバージョン更新。

Feature Flags：新機能はフラグで制御し、段階的に有効化（Rollout）する。

Canary/Blue-Green：Gemini周りなど慎重にロールアウト。

契約テスト（Consumer-Driven Contract）：pact や契約テストで消費側と提供側のAPI合意を自動確認。

モックとスタブを活用：Geminiやe-Gov呼び出しは開発段階でモック可能にしておく。実APIはステージングでのみ呼ぶ。

監査ログの保存：重要出力（過失割合、提案、参照した条文ID）は必ず監査ログに記録。改竄防止措置を施す。