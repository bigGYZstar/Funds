# コントリビューションガイド

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます。

## コーディング規約

### Python スタイルガイド

このプロジェクトは **PEP 8** スタイルガイドに準拠しています。

**主要な規約:**

- **インデント**: スペース4つ
- **行の長さ**: 最大120文字（推奨は79文字）
- **命名規則**:
  - クラス名: `PascalCase`（例: `FundPerformanceAnalyzer`）
  - 関数名・変数名: `snake_case`（例: `calculate_annualized_returns`）
  - 定数: `UPPER_SNAKE_CASE`（例: `BASE_DATE`）
- **docstring**: すべての関数とクラスに記述
- **型ヒント**: 可能な限り使用を推奨

**例:**

```python
def calculate_annualized_returns(
    monthly_returns: pd.Series,
    period_months: int = 36
) -> float:
    """
    月次リターンから年率リターンを計算する
    
    Parameters:
    -----------
    monthly_returns : pd.Series
        月次リターンの系列
    period_months : int
        計算期間（月数）
        
    Returns:
    --------
    float
        年率リターン
    """
    cumulative = np.prod(1 + monthly_returns)
    return cumulative ** (12 / period_months) - 1
```

### コード品質

**必須チェック:**

- [ ] コードは動作確認済み
- [ ] docstringが記述されている
- [ ] 変数名が意味を持っている
- [ ] 複雑なロジックにはコメントがある
- [ ] エラーハンドリングが適切

## コミット規約

### コミットメッセージフォーマット

```
<type>: <subject>

<body>

<footer>
```

### Type（必須）

- **feat**: 新機能の追加
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: コードの意味に影響しない変更（空白、フォーマット等）
- **refactor**: バグ修正や機能追加を伴わないコード変更
- **test**: テストの追加・修正
- **chore**: ビルドプロセスやツールの変更

### Subject（必須）

- 50文字以内
- 現在形で記述
- 先頭は小文字
- 末尾にピリオドを付けない

### Body（任意）

- 72文字で折り返し
- 何を変更したか、なぜ変更したかを説明

### Footer（任意）

- Issue番号を参照（例: `Closes #123`）

### 例

```
feat: ローリング36か月分析機能を追加

起点を1か月ずつずらしたローリング分析により、
超過リターンの安定性を確認できるようにした。

- RobustnessAnalyzerクラスを新規作成
- 最低12ウィンドウの制約を追加
- 等金額・AUM加重の両方で計算

Closes #5
```

## ブランチ戦略

### メインブランチ

- **main**: 本番環境用の安定版
- **develop**: 開発用ブランチ（統合テスト済み）

### フィーチャーブランチ

新機能やバグ修正は、以下の命名規則でブランチを作成してください。

```
<type>/<issue-number>-<short-description>
```

**例:**

- `feat/10-add-confidence-interval`
- `fix/15-handle-missing-data`
- `docs/20-update-readme`

### ワークフロー

1. **Issue作成**: 作業内容をIssueとして登録
2. **ブランチ作成**: `develop`から新しいブランチを作成
3. **開発**: コミット規約に従って開発
4. **プルリクエスト**: `develop`へのPRを作成
5. **レビュー**: コードレビューを受ける
6. **マージ**: 承認後にマージ

## プルリクエストガイドライン

### PRテンプレート

```markdown
## 概要
<!-- 変更内容の概要を記述 -->

## 変更内容
<!-- 具体的な変更内容をリスト形式で記述 -->
- 
- 

## 関連Issue
<!-- 関連するIssue番号を記述 -->
Closes #

## テスト
<!-- 実施したテストを記述 -->
- [ ] 単体テスト実施
- [ ] 手動テスト実施
- [ ] サンプルデータで動作確認

## スクリーンショット（該当する場合）
<!-- 可視化の変更がある場合はスクリーンショットを添付 -->

## チェックリスト
- [ ] コードはPEP 8に準拠している
- [ ] docstringを記述した
- [ ] READMEを更新した（必要な場合）
- [ ] テストを実施した
```

### レビュー基準

**承認条件:**

- [ ] コードが正しく動作する
- [ ] コーディング規約に準拠している
- [ ] 適切なエラーハンドリングがある
- [ ] ドキュメントが更新されている
- [ ] テストが実施されている

## ディレクトリ構造

```
Funds/
├── README.md                          # プロジェクト概要
├── CONTRIBUTING.md                    # このファイル
├── ARCHITECTURE.md                    # アーキテクチャ設計
├── data_requirements.md               # データ要件定義
├── data/                              # データディレクトリ
│   ├── fund_attributes_template.csv  # ファンド属性テンプレート
│   └── monthly_returns_template.csv  # 月次リターンテンプレート
├── scripts/                           # 分析スクリプト
│   ├── fund_performance_analysis.py  # メイン分析
│   ├── robustness_analysis.py        # ロバストネス分析
│   └── visualization.py              # 可視化
├── output/                            # 出力ディレクトリ
├── docs/                              # ドキュメント
│   ├── execution_guide.md            # 実行手順書
│   └── framework_overview.md         # フレームワーク概要
└── tests/                             # テストコード
```

## 開発環境セットアップ

### 必要な環境

- Python 3.11以上
- Git 2.0以上

### セットアップ手順

```bash
# リポジトリのクローン
git clone https://github.com/bigGYZstar/Funds.git
cd Funds

# 仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

## テスト

### 単体テスト

```bash
# pytest実行
pytest tests/

# カバレッジ付き実行
pytest --cov=scripts tests/
```

### 手動テスト

サンプルデータで分析を実行し、結果を確認してください。

```bash
cd scripts
python3 fund_performance_analysis.py
```

## 質問・サポート

質問や提案がある場合は、GitHubのIssuesで気軽にお尋ねください。

---

**ありがとうございます！**

あなたの貢献がこのプロジェクトをより良いものにします。
