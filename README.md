# 日本籍米国株式アクティブ投信パフォーマンス検証フレームワーク

## 概要

このフレームワークは、日本籍の米国株式アクティブ投資信託のパフォーマンスを統計的に検証するための完全な分析ツールセットです。

**主な機能:**
- アクティブ全体・上位50％ vs パッシブ（S&P500連動）の比較
- 統計的検定（t検定、Mann-Whitney検定、効果量）
- ロバストネス分析（ローリング36か月）
- 為替ヘッジあり/なしの分離集計
- 等金額平均とAUM加重平均の両方を計算
- 包括的な可視化（ヒストグラム、箱ひげ図、推移グラフ）

---

## ディレクトリ構造

```
fund_analysis/
├── README.md                          # このファイル
├── data_requirements.md               # データ要件定義書
├── data/                              # データディレクトリ
│   ├── fund_attributes.csv           # ファンド基本属性データ（要作成）
│   ├── monthly_returns.csv           # 月次リターンデータ（要作成）
│   └── data_sources.txt              # データソース情報（要作成）
├── scripts/                           # 分析スクリプト
│   ├── fund_performance_analysis.py  # メイン統計分析
│   ├── robustness_analysis.py        # ロバストネス分析
│   └── visualization.py              # 可視化スクリプト
├── output/                            # 出力ディレクトリ
│   ├── annualized_returns_3y.csv     # 年率リターン一覧
│   ├── summary_statistics.csv        # 集計統計量
│   ├── statistical_tests.csv         # 統計検定結果
│   ├── rolling_36month_analysis.csv  # ローリング分析結果
│   └── *.png                         # 可視化グラフ
├── docs/                              # ドキュメント
└── tests/                             # テストスクリプト
```

---

## セットアップ

### 必要な環境

- Python 3.11以上
- 必要なパッケージ: pandas, numpy, scipy, matplotlib

### パッケージインストール

```bash
pip3 install pandas numpy scipy matplotlib
```

---

## 使用方法

### ステップ1: データ準備

`data_requirements.md`を参照して、以下の2つのCSVファイルを`data/`ディレクトリに配置してください。

1. **fund_attributes.csv** - ファンド基本属性データ
2. **monthly_returns.csv** - 月次リターンデータ

### ステップ2: 基準日の設定

`scripts/fund_performance_analysis.py`の`BASE_DATE`変数を編集して、分析の基準日を設定してください。

```python
BASE_DATE = "2024-10-31"  # 例: 2024年10月末
```

### ステップ3: メイン分析の実行

```bash
cd scripts
python3 fund_performance_analysis.py
```

**出力ファイル:**
- `annualized_returns_3y.csv` - 全ファンドの3年年率リターン
- `summary_statistics.csv` - 集計統計量（等金額・AUM加重）
- `statistical_tests.csv` - 統計検定結果（t検定、Mann-Whitney、効果量）
- `ranking_active_hedge_*.csv` - ヘッジ区分別ランキング
- `excluded_funds_insufficient_data.csv` - 除外ファンドリスト

### ステップ4: ロバストネス分析の実行

```bash
python3 robustness_analysis.py
```

**出力ファイル:**
- `rolling_36month_analysis.csv` - ローリング36か月分析結果
- `rolling_analysis_summary.csv` - ローリング分析サマリー

### ステップ5: 可視化の実行

```bash
python3 visualization.py
```

**出力ファイル:**
- `histogram_returns_hedge_*.png` - リターン分布ヒストグラム
- `boxplot_returns_hedge_*.png` - 箱ひげ図
- `rolling_excess_returns_hedge_*.png` - ローリング超過リターン推移
- `comparison_bar_chart.png` - 比較バーチャート

---

## 分析仕様

### 計算方法

#### 3年年率リターン（CAGR）

月次リターンを \( r_t \)（t=1..36）とし、以下の式で計算します。

$$
R_{\text{ann}} = \left(\prod_{t=1}^{36}(1+r_t)\right)^{12/36}-1
$$

#### 上位50％の定義

各ヘッジ区分内でファンドを年率リターンの降順に並べ、上位 ⌈0.5 × N⌉ 本を上位50％とします。

#### 超過リターン

- **全体超過** = （アクティブ全体平均） − （パッシブ平均）
- **上位超過** = （アクティブ上位50％平均） − （パッシブ平均）

### 統計検定

1. **t検定**: アクティブとパッシブの平均差の有意性を検定
2. **Mann-Whitney U検定**: 非正規分布の場合の補完検定
3. **効果量（Cohen's d）**: 差の実質的な大きさを評価

有意水準: 5%

### ロバストネス分析

- 起点を1か月ずつずらしたローリング36か月分析（最低12起点）
- 等金額平均とAUM加重平均の両方で計算
- 超過リターンの安定性を確認

---

## データ品質要件

### 必須条件

- **36か月要件**: 基準日時点で36か月以上の連続月次データがあるファンドのみ採用
- **ヘッジ区分の分離**: 為替ヘッジあり/なしは別集合として集計
- **シェアクラス統一**: 同一運用の複数クラスは代表1クラスに統一
- **サバイバーシップ・バイアス対策**: 償還済みファンドも条件を満たせば含める

### 除外基準

- トラックレコードが36か月未満
- テーマ特化型（AI、ヘルスケア等単一テーマ）
- レバレッジ型
- オプション戦略
- ファンド・オブ・ファンズで米国株以外の配分が大きいもの

---

## 出力物の解釈

### summary_statistics.csv

| カラム | 説明 |
|--------|------|
| `currency_hedge` | 為替ヘッジ区分（"なし" or "あり"） |
| `weighting` | 加重方法（"等金額" or "AUM加重"） |
| `active_all_mean` | アクティブ全体の平均年率リターン |
| `active_top50_mean` | アクティブ上位50％の平均年率リターン |
| `passive_mean` | パッシブの平均年率リターン |
| `excess_all` | アクティブ全体の超過リターン |
| `excess_top50` | アクティブ上位50％の超過リターン |

### statistical_tests.csv

| カラム | 説明 |
|--------|------|
| `comparison` | 比較対象（"アクティブ全体 vs パッシブ" or "アクティブ上位50% vs パッシブ"） |
| `t_statistic` | t統計量 |
| `p_value_ttest` | t検定のp値 |
| `cohens_d` | 効果量（Cohen's d） |
| `u_statistic` | Mann-Whitney U統計量 |
| `p_value_mannwhitney` | Mann-Whitney検定のp値 |
| `significant_5pct` | 5%水準で有意か（TRUE/FALSE） |

---

## トラブルシューティング

### エラー: "ファンド属性データが見つかりません"

**原因**: `data/fund_attributes.csv`が存在しない

**解決策**: `data_requirements.md`を参照してデータファイルを作成し、`data/`ディレクトリに配置してください。

### エラー: "36か月未満のトラックレコード"

**原因**: 月次データが36か月に満たないファンドが含まれている

**解決策**: `output/excluded_funds_insufficient_data.csv`で除外されたファンドを確認してください。これは正常な動作です。

### 警告: "異常値検出"

**原因**: ±50%を超える月次リターンが検出された

**解決策**: `output/outliers_detected.csv`で該当レコードを確認し、データソースと照合してください。

---

## 依頼書との対応

このフレームワークは、以下の依頼書要件に完全準拠しています。

| 要件項目 | 対応状況 |
|---------|---------|
| 36か月トラックレコード要件 | ✓ 実装済み |
| ヘッジあり/なしの分離集計 | ✓ 実装済み |
| 等金額・AUM加重の両方計算 | ✓ 実装済み |
| t検定・Mann-Whitney検定 | ✓ 実装済み |
| 効果量（Cohen's d） | ✓ 実装済み |
| ローリング36か月分析 | ✓ 実装済み |
| サバイバーシップ・バイアス対策 | ✓ データ要件に明記 |
| 異常値チェック | ✓ 実装済み |
| 可視化（ヒストグラム、箱ひげ図等） | ✓ 実装済み |

---

## ライセンス

このフレームワークは統計分析専門家によって作成されました。

---

## サポート

ご不明点やエラーが発生した場合は、以下の情報をご提供ください。

1. エラーメッセージの全文
2. 使用しているPythonバージョン
3. データファイルのサンプル（最初の5行）

---

**最終更新**: 2025年11月9日
