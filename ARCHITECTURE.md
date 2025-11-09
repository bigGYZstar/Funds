# アーキテクチャ設計

## 概要

このドキュメントでは、日本籍米国株式アクティブ投信パフォーマンス検証フレームワークのアーキテクチャ設計について説明します。

---

## システム構成

### 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    入力データ層                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ fund_attributes  │  │ monthly_returns  │            │
│  │     .csv         │  │      .csv        │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  データ処理層                            │
│  ┌──────────────────────────────────────────┐          │
│  │  FundPerformanceAnalyzer                 │          │
│  │  - load_data()                           │          │
│  │  - validate_and_clean_data()             │          │
│  │  - calculate_annualized_returns()        │          │
│  │  - rank_and_segment_funds()              │          │
│  │  - calculate_aggregate_statistics()      │          │
│  │  - perform_statistical_tests()           │          │
│  │  - save_results()                        │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  RobustnessAnalyzer                      │          │
│  │  - load_data()                           │          │
│  │  - calculate_rolling_analysis()          │          │
│  │  - save_results()                        │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   可視化層                               │
│  ┌──────────────────────────────────────────┐          │
│  │  FundVisualization                       │          │
│  │  - load_results()                        │          │
│  │  - plot_return_distribution_histogram()  │          │
│  │  - plot_boxplot()                        │          │
│  │  - plot_rolling_excess_returns()         │          │
│  │  - plot_top50_comparison()               │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   出力層                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  CSV結果     │  │  PNG画像     │  │  レポート    │ │
│  │  ファイル    │  │  ファイル    │  │  (将来実装)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## フォルダレイアウト

### ディレクトリ構造

```
Funds/
├── README.md                          # プロジェクト概要・使用方法
├── CONTRIBUTING.md                    # コントリビューションガイド
├── ARCHITECTURE.md                    # このファイル
├── data_requirements.md               # データ要件定義書
├── .gitignore                         # Git除外設定
│
├── data/                              # データディレクトリ
│   ├── fund_attributes_template.csv  # ファンド属性テンプレート
│   ├── monthly_returns_template.csv  # 月次リターンテンプレート
│   ├── fund_attributes.csv           # 実際のファンド属性（.gitignore対象）
│   ├── monthly_returns.csv           # 実際の月次リターン（.gitignore対象）
│   └── data_sources.txt              # データソース情報（.gitignore対象）
│
├── scripts/                           # 分析スクリプト
│   ├── fund_performance_analysis.py  # メイン分析スクリプト
│   ├── robustness_analysis.py        # ロバストネス分析スクリプト
│   └── visualization.py              # 可視化スクリプト
│
├── output/                            # 出力ディレクトリ（.gitignore対象）
│   ├── *.csv                         # 分析結果CSV
│   └── *.png                         # 可視化画像
│
├── docs/                              # ドキュメント
│   ├── execution_guide.md            # 実行手順書
│   └── framework_overview.md         # フレームワーク概要
│
└── tests/                             # テストコード（将来実装）
    └── test_*.py                     # 単体テスト
```

### ディレクトリの役割

| ディレクトリ | 役割 | Git管理 |
|------------|------|---------|
| `data/` | 入力データの格納 | テンプレートのみ |
| `scripts/` | 分析ロジックの実装 | すべて管理 |
| `output/` | 分析結果の出力 | 管理しない |
| `docs/` | ドキュメント | すべて管理 |
| `tests/` | テストコード | すべて管理 |

---

## 機能モジュールパターン

### 1. FundPerformanceAnalyzer（メイン分析クラス）

**責務**: ファンドパフォーマンスの統計分析

**主要メソッド:**

```python
class FundPerformanceAnalyzer:
    def __init__(self, base_date: str, data_dir: str = "../data"):
        """初期化"""
        
    def load_data(self) -> 'FundPerformanceAnalyzer':
        """データファイルの読み込み"""
        
    def validate_and_clean_data(self) -> 'FundPerformanceAnalyzer':
        """データ品質チェックとクレンジング"""
        
    def calculate_annualized_returns(self) -> 'FundPerformanceAnalyzer':
        """3年年率リターン（CAGR）の計算"""
        
    def rank_and_segment_funds(self) -> 'FundPerformanceAnalyzer':
        """ランキングと上位50％の抽出"""
        
    def calculate_aggregate_statistics(self) -> 'FundPerformanceAnalyzer':
        """集計統計量の計算"""
        
    def perform_statistical_tests(self) -> 'FundPerformanceAnalyzer':
        """統計的検定の実行"""
        
    def save_results(self, output_dir: str = "../output") -> 'FundPerformanceAnalyzer':
        """結果の保存"""
```

**設計パターン**: Fluent Interface（メソッドチェーン）

**使用例:**

```python
analyzer = FundPerformanceAnalyzer(base_date="2024-10-31")
analyzer.load_data() \
        .validate_and_clean_data() \
        .calculate_annualized_returns() \
        .rank_and_segment_funds() \
        .calculate_aggregate_statistics() \
        .perform_statistical_tests() \
        .save_results()
```

### 2. RobustnessAnalyzer（ロバストネス分析クラス）

**責務**: ローリング36か月分析による頑健性検証

**主要メソッド:**

```python
class RobustnessAnalyzer:
    def __init__(self, data_dir: str = "../data"):
        """初期化"""
        
    def load_data(self) -> 'RobustnessAnalyzer':
        """データファイルの読み込み"""
        
    def calculate_rolling_analysis(self, min_windows: int = 12) -> 'RobustnessAnalyzer':
        """ローリング36か月分析"""
        
    def save_results(self, output_dir: str = "../output") -> 'RobustnessAnalyzer':
        """結果の保存"""
```

**設計パターン**: Fluent Interface（メソッドチェーン）

### 3. FundVisualization（可視化クラス）

**責務**: 分析結果の可視化

**主要メソッド:**

```python
class FundVisualization:
    def __init__(self, output_dir: str = "../output"):
        """初期化"""
        
    def load_results(self) -> 'FundVisualization':
        """分析結果の読み込み"""
        
    def plot_return_distribution_histogram(self) -> 'FundVisualization':
        """年率リターン分布のヒストグラム"""
        
    def plot_boxplot(self) -> 'FundVisualization':
        """箱ひげ図"""
        
    def plot_rolling_excess_returns(self) -> 'FundVisualization':
        """ローリング超過リターン推移"""
        
    def plot_top50_comparison(self) -> 'FundVisualization':
        """上位50%とパッシブの比較バーチャート"""
```

**設計パターン**: Fluent Interface（メソッドチェーン）

---

## データスキーマポリシー

### 入力データスキーマ

#### fund_attributes.csv

| カラム名 | データ型 | 必須 | 説明 |
|---------|---------|------|------|
| `fund_id` | string | ✓ | ファンドの一意識別子 |
| `fund_name` | string | ✓ | ファンド名称 |
| `management_company` | string | ✓ | 運用会社名 |
| `inception_date` | date | ✓ | 設定日（YYYY-MM-DD） |
| `share_class` | string | ✓ | シェアクラス区分 |
| `currency_hedge` | string | ✓ | 為替ヘッジ有無（"あり" or "なし"） |
| `benchmark` | string | ✓ | ベンチマーク表記 |
| `expense_ratio` | float | ✓ | 実質信託報酬率（年率％） |
| `aum_latest` | float | ✓ | 最新の純資産総額（百万円） |
| `fund_type` | string | ✓ | ファンドタイプ（"アクティブ" or "パッシブ"） |
| `is_index_fund` | boolean | ✓ | インデックスファンドか |
| `investment_style` | string |  | 投資スタイル |
| `is_theme_fund` | boolean | ✓ | テーマ特化型か |
| `is_leveraged` | boolean | ✓ | レバレッジ型か |
| `is_fund_of_funds` | boolean | ✓ | ファンド・オブ・ファンズか |
| `status` | string | ✓ | 運用状況（"運用中" or "償還済み"） |
| `redemption_date` | date |  | 償還日 |
| `inclusion_reason` | string | ✓ | 採用理由または除外理由 |

#### monthly_returns.csv

| カラム名 | データ型 | 必須 | 説明 |
|---------|---------|------|------|
| `fund_id` | string | ✓ | ファンドの一意識別子 |
| `month_end_date` | date | ✓ | 月末日付（YYYY-MM-DD） |
| `monthly_return` | float | ✓ | 月次トータルリターン（小数表記） |
| `nav` | float |  | 基準価額（円） |
| `aum` | float |  | 純資産総額（百万円） |

### 出力データスキーマ

#### annualized_returns_3y.csv

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| `fund_id` | string | ファンドの一意識別子 |
| `fund_name` | string | ファンド名称 |
| `fund_type` | string | ファンドタイプ |
| `currency_hedge` | string | 為替ヘッジ有無 |
| `expense_ratio` | float | 実質信託報酬率 |
| `aum_latest` | float | 最新の純資産総額 |
| `annualized_return_3y` | float | 3年年率リターン |
| `cumulative_return_3y` | float | 3年累積リターン |

#### summary_statistics.csv

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| `currency_hedge` | string | 為替ヘッジ区分 |
| `weighting` | string | 加重方法（"等金額" or "AUM加重"） |
| `active_all_mean` | float | アクティブ全体の平均年率リターン |
| `active_top50_mean` | float | アクティブ上位50％の平均年率リターン |
| `passive_mean` | float | パッシブの平均年率リターン |
| `excess_all` | float | アクティブ全体の超過リターン |
| `excess_top50` | float | アクティブ上位50％の超過リターン |

#### statistical_tests.csv

| カラム名 | データ型 | 説明 |
|---------|---------|------|
| `currency_hedge` | string | 為替ヘッジ区分 |
| `comparison` | string | 比較対象 |
| `t_statistic` | float | t統計量 |
| `p_value_ttest` | float | t検定のp値 |
| `cohens_d` | float | 効果量（Cohen's d） |
| `u_statistic` | float | Mann-Whitney U統計量 |
| `p_value_mannwhitney` | float | Mann-Whitney検定のp値 |
| `significant_5pct` | boolean | 5%水準で有意か |

### スキーマバージョニングポリシー

**原則**: スキーマの破壊的変更は許可しない

**許可される変更:**
- 新しいカラムの追加（既存カラムに影響しない）
- オプショナルカラムの追加

**禁止される変更:**
- 既存カラムの削除
- 既存カラムのデータ型変更
- 既存カラムの名前変更

**破壊的変更が必要な場合:**
1. メジャーバージョンアップを実施
2. マイグレーションスクリプトを提供
3. 旧スキーマとの互換性を一定期間維持

---

## データフロー

### 1. データ読み込みフロー

```
[CSV読み込み]
    ↓
[pandas DataFrameに変換]
    ↓
[日付カラムをdatetime型に変換]
    ↓
[データ型の検証]
    ↓
[メモリ内保持]
```

### 2. データクレンジングフロー

```
[基準日から36か月前の開始日を計算]
    ↓
[期間内のリターンデータをフィルタ]
    ↓
[各ファンドの月次データ数をカウント]
    ↓
[36か月のデータがあるファンドのみ採用]
    ↓
[除外ファンドリストを保存]
    ↓
[異常値チェック（±50%超）]
    ↓
[異常値リストを保存]
```

### 3. 計算フロー

```
[月次リターンから累積リターンを計算]
    ↓
[累積リターンから年率リターンを計算]
    ↓
[ヘッジ区分ごとにグループ化]
    ↓
[年率リターンでソート]
    ↓
[上位50%を抽出]
    ↓
[等金額平均を計算]
    ↓
[AUM加重平均を計算]
    ↓
[超過リターンを計算]
    ↓
[統計検定を実行]
```

### 4. 出力フロー

```
[DataFrame → CSV変換]
    ↓
[UTF-8 with BOMエンコーディング]
    ↓
[output/ディレクトリに保存]
    ↓
[可視化データの準備]
    ↓
[matplotlib/seabornでグラフ作成]
    ↓
[PNG形式で保存（300 DPI）]
```

---

## 依存関係

### 外部ライブラリ

| ライブラリ | バージョン | 用途 |
|-----------|-----------|------|
| pandas | ≥1.5.0 | データ処理・集計 |
| numpy | ≥1.23.0 | 数値計算 |
| scipy | ≥1.9.0 | 統計検定 |
| matplotlib | ≥3.6.0 | 可視化 |

### 依存関係グラフ

```
fund_performance_analysis.py
    ├── pandas
    ├── numpy
    └── scipy

robustness_analysis.py
    ├── pandas
    ├── numpy
    └── scipy

visualization.py
    ├── pandas
    ├── numpy
    └── matplotlib
```

---

## パフォーマンス考慮事項

### メモリ使用量

**想定データサイズ:**
- ファンド数: 100～500本
- 月次データ: 36か月 × ファンド数
- メモリ使用量: 数MB～数十MB

**最適化:**
- 不要なカラムは読み込まない
- データ型を適切に設定（float64 → float32等）
- 大規模データの場合はチャンク読み込みを検討

### 計算時間

**想定実行時間:**
- メイン分析: 数秒～数十秒
- ロバストネス分析: 数十秒～数分
- 可視化: 数秒

**ボトルネック:**
- ローリング分析のウィンドウ数が多い場合
- 可視化の画像保存

---

## セキュリティ考慮事項

### データ保護

1. **機密データの除外**: 実際のデータファイルは`.gitignore`で除外
2. **テンプレートのみ公開**: サンプルデータのみリポジトリに含める
3. **アクセス制御**: プライベートリポジトリでの運用を推奨

### コード安全性

1. **入力検証**: データ型・範囲の妥当性チェック
2. **エラーハンドリング**: 適切な例外処理
3. **ログ出力**: 処理状況の可視化

---

## 拡張性

### 将来の拡張ポイント

1. **レポート自動生成**
   - Markdown/PDFでのエグゼクティブサマリー生成
   - テンプレートエンジンの導入

2. **Web UI**
   - Streamlit/Dashによるインタラクティブダッシュボード
   - データアップロード機能

3. **API化**
   - FastAPIによるREST API提供
   - クラウドデプロイメント

4. **機械学習統合**
   - パフォーマンス予測モデル
   - リスク評価モデル

---

**最終更新**: 2025年11月9日
