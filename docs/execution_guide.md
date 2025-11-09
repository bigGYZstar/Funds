# 実行手順書

## 分析フレームワーク実行ガイド

このドキュメントでは、ファンドパフォーマンス検証フレームワークの具体的な実行手順を説明します。

---

## 前提条件

### 1. 環境確認

```bash
# Pythonバージョン確認（3.11以上推奨）
python3 --version

# 必要なパッケージのインストール
pip3 install pandas numpy scipy matplotlib
```

### 2. ディレクトリ移動

```bash
cd /home/ubuntu/fund_analysis
```

---

## データ準備

### ステップ1: データファイルの配置

`data/`ディレクトリに以下の2つのCSVファイルを配置してください。

#### 必須ファイル

1. **fund_attributes.csv** - ファンド基本属性データ
2. **monthly_returns.csv** - 月次リターンデータ

#### テンプレートファイル

参考として以下のテンプレートファイルが用意されています。

- `data/fund_attributes_template.csv`
- `data/monthly_returns_template.csv`

実際のデータは、これらのテンプレートと同じフォーマットで作成してください。

### ステップ2: データ品質チェック

データファイルを配置したら、以下を確認してください。

**fund_attributes.csv:**
- すべての必須カラムが存在するか
- `fund_type`が「アクティブ」または「パッシブ」か
- `currency_hedge`が「あり」または「なし」か
- 日付形式が「YYYY-MM-DD」か

**monthly_returns.csv:**
- `fund_id`が`fund_attributes.csv`と一致するか
- 月次リターンが小数表記か（例: 5% → 0.05）
- 日付形式が「YYYY-MM-DD」か
- 各ファンドに36か月以上のデータがあるか

---

## 分析実行

### ステップ3: 基準日の設定

`scripts/fund_performance_analysis.py`を開き、`BASE_DATE`を編集します。

```python
# 基準日の設定（この月末を終点とする過去36か月が分析対象）
BASE_DATE = "2024-10-31"  # 例: 2024年10月末
```

### ステップ4: メイン分析の実行

```bash
cd scripts
python3 fund_performance_analysis.py
```

**実行時間の目安**: 数十ファンドで数秒～数分

**出力ファイル（`output/`ディレクトリ）:**

| ファイル名 | 内容 |
|-----------|------|
| `annualized_returns_3y.csv` | 全ファンドの3年年率リターン一覧 |
| `summary_statistics.csv` | 集計統計量（等金額・AUM加重） |
| `statistical_tests.csv` | 統計検定結果（t検定、Mann-Whitney、効果量） |
| `ranking_active_hedge_なし.csv` | アクティブファンドランキング（ヘッジなし） |
| `ranking_active_hedge_あり.csv` | アクティブファンドランキング（ヘッジあり） |
| `excluded_funds_insufficient_data.csv` | 除外ファンドリスト（36か月未満） |
| `outliers_detected.csv` | 異常値検出リスト（±50%超） |

### ステップ5: ロバストネス分析の実行

```bash
python3 robustness_analysis.py
```

**実行時間の目安**: 数十ファンドで数秒～数分

**出力ファイル（`output/`ディレクトリ）:**

| ファイル名 | 内容 |
|-----------|------|
| `rolling_36month_analysis.csv` | ローリング36か月分析の詳細結果 |
| `rolling_analysis_summary.csv` | ローリング分析のサマリー統計 |

### ステップ6: 可視化の実行

```bash
python3 visualization.py
```

**実行時間の目安**: 数秒～数十秒

**出力ファイル（`output/`ディレクトリ）:**

| ファイル名 | 内容 |
|-----------|------|
| `histogram_returns_hedge_なし.png` | リターン分布ヒストグラム（ヘッジなし） |
| `histogram_returns_hedge_あり.png` | リターン分布ヒストグラム（ヘッジあり） |
| `boxplot_returns_hedge_なし.png` | 箱ひげ図（ヘッジなし） |
| `boxplot_returns_hedge_あり.png` | 箱ひげ図（ヘッジあり） |
| `rolling_excess_returns_hedge_なし.png` | ローリング超過リターン推移（ヘッジなし） |
| `rolling_excess_returns_hedge_あり.png` | ローリング超過リターン推移（ヘッジあり） |
| `comparison_bar_chart.png` | 比較バーチャート |

---

## 結果の確認

### 主要な確認ポイント

#### 1. 集計統計量（summary_statistics.csv）

```bash
# CSVファイルを確認
cat ../output/summary_statistics.csv
```

**確認項目:**
- アクティブ上位50％の平均リターンがパッシブを上回っているか
- 超過リターン（`excess_top50`）の大きさ
- 等金額平均とAUM加重平均の差異

#### 2. 統計検定結果（statistical_tests.csv）

```bash
# CSVファイルを確認
cat ../output/statistical_tests.csv
```

**確認項目:**
- p値（`p_value_ttest`）が0.05未満か（統計的に有意）
- 効果量（`cohens_d`）の大きさ
  - 小: 0.2
  - 中: 0.5
  - 大: 0.8以上
- Mann-Whitney検定の結果も一致しているか

#### 3. ローリング分析（rolling_36month_analysis.csv）

```bash
# 最初の10行を確認
head -n 10 ../output/rolling_36month_analysis.csv
```

**確認項目:**
- 超過リターンが複数のウィンドウで一貫しているか
- 時期によって結果が大きく変動していないか

---

## トラブルシューティング

### エラー1: "ファイルが見つかりません"

**エラーメッセージ:**
```
FileNotFoundError: ファンド属性データが見つかりません: ../data/fund_attributes.csv
```

**解決策:**
1. `data/`ディレクトリに`fund_attributes.csv`が存在するか確認
2. ファイル名のスペルミスがないか確認
3. 相対パスが正しいか確認（`scripts/`から実行している場合）

### エラー2: "データ期間が不足しています"

**エラーメッセージ:**
```
ValueError: データ期間が不足しています（必要: 36か月、実際: 24か月）
```

**解決策:**
1. `monthly_returns.csv`に36か月以上のデータがあるか確認
2. 基準日（`BASE_DATE`）を調整して、データ期間内に収める

### エラー3: "KeyError: 'fund_type'"

**エラーメッセージ:**
```
KeyError: 'fund_type'
```

**解決策:**
1. `fund_attributes.csv`に`fund_type`カラムが存在するか確認
2. カラム名のスペルミスがないか確認（大文字小文字も区別されます）

### 警告: "アクティブファンドデータなし"

**警告メッセージ:**
```
⚠ アクティブファンドデータなし（ヘッジあり）
```

**原因:**
- 該当するヘッジ区分のアクティブファンドがデータに含まれていない

**対処:**
- 正常な動作です。該当ヘッジ区分のファンドがない場合はスキップされます。

---

## 一括実行スクリプト

すべての分析を一括で実行したい場合は、以下のシェルスクリプトを使用できます。

### run_all.sh の作成

```bash
#!/bin/bash
# 一括実行スクリプト

echo "=========================================="
echo "ファンドパフォーマンス検証フレームワーク"
echo "=========================================="

cd /home/ubuntu/fund_analysis/scripts

echo ""
echo "ステップ1: メイン分析実行"
python3 fund_performance_analysis.py
if [ $? -ne 0 ]; then
    echo "❌ メイン分析でエラーが発生しました"
    exit 1
fi

echo ""
echo "ステップ2: ロバストネス分析実行"
python3 robustness_analysis.py
if [ $? -ne 0 ]; then
    echo "❌ ロバストネス分析でエラーが発生しました"
    exit 1
fi

echo ""
echo "ステップ3: 可視化実行"
python3 visualization.py
if [ $? -ne 0 ]; then
    echo "❌ 可視化でエラーが発生しました"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ すべての分析が完了しました"
echo "=========================================="
echo ""
echo "結果は output/ ディレクトリに保存されています"
```

### 実行方法

```bash
# 実行権限を付与
chmod +x run_all.sh

# 実行
./run_all.sh
```

---

## 検算方法

### 手計算による検証

依頼書の検収条件に従い、ランダムに選んだファンドで手計算検算を行います。

#### 例: SAMPLE001の3年年率リターン検算

**月次リターンデータ（36か月分）:**
```
r_1 = 0.0523, r_2 = -0.0123, ..., r_36 = -0.0345
```

**計算式:**
```
累積リターン = (1 + r_1) × (1 + r_2) × ... × (1 + r_36)
年率リターン = 累積リターン^(12/36) - 1
```

**Pythonでの検算:**
```python
import numpy as np

monthly_returns = [0.0523, -0.0123, 0.0456, ...]  # 36個
cumulative = np.prod([1 + r for r in monthly_returns])
annualized = cumulative ** (12 / 36) - 1
print(f"年率リターン: {annualized:.4f} ({annualized * 100:.2f}%)")
```

**出力ファイルとの照合:**
```bash
# annualized_returns_3y.csvでSAMPLE001を検索
grep "SAMPLE001" ../output/annualized_returns_3y.csv
```

計算結果が一致すれば検算合格です。

---

## 次のステップ

分析が完了したら、以下のレポート作成に進みます。

1. **エグゼクティブサマリー**の作成（2～4ページ）
2. **本編レポート**の作成（詳細分析結果）
3. **データ辞書**の作成
4. **再現性資料**の作成

これらのドキュメント作成については、別途指示があればサポートいたします。

---

**最終更新**: 2025年11月9日
