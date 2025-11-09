# クイックスタートガイド

このガイドでは、サンプルデータを使用して分析フレームワークをすぐに実行する方法を説明します。

---

## 前提条件

- Python 3.11以上
- Git

---

## 5分でできる分析実行

### ステップ1: リポジトリのクローン

```bash
git clone https://github.com/bigGYZstar/Funds.git
cd Funds
```

### ステップ2: 依存パッケージのインストール

```bash
pip3 install -r requirements.txt
```

### ステップ3: サンプルデータの生成

```bash
python3 scripts/generate_sample_data.py
```

**出力例:**
```
============================================================
サンプルデータ生成スクリプト
============================================================

1. ファンド属性データを生成中...
   ✓ 26本のファンドデータを生成
   ✓ 保存先: ../data/fund_attributes.csv

   [ファンド構成]
   - アクティブ（ヘッジなし）: 10本
   - アクティブ（ヘッジあり）: 10本
   - パッシブ（ヘッジなし）: 3本
   - パッシブ（ヘッジあり）: 3本

2. 月次リターンデータを生成中...
   ✓ 1248件の月次リターンデータを生成
   ✓ 期間: 2020-11-30 ～ 2024-10-31
   ✓ 保存先: ../data/monthly_returns.csv

3. データソース情報を記録中...
   ✓ 保存先: ../data/data_sources.txt

============================================================
サンプルデータの生成が完了しました！
============================================================
```

### ステップ4: メイン分析の実行

```bash
cd scripts
python3 fund_performance_analysis.py
```

**出力例:**
```
============================================================
ファンドパフォーマンス分析
============================================================

基準日: 2024-10-31
分析期間: 36か月（2021-11-30 ～ 2024-10-31）

1. データ読み込み中...
   ✓ ファンド属性: 26本
   ✓ 月次リターン: 1248件

2. データクレンジング中...
   ✓ 36か月要件を満たすファンド: 26本
   ✓ 除外ファンド: 0本

3. 年率リターン計算中...
   ✓ 3年年率リターン（CAGR）を計算

4. ランキングと上位50%抽出中...
   ✓ アクティブ（ヘッジなし）: 10本 → 上位5本
   ✓ アクティブ（ヘッジあり）: 10本 → 上位5本

5. 集計統計量計算中...
   ✓ 等金額平均を計算
   ✓ AUM加重平均を計算

6. 統計検定実行中...
   ✓ t検定を実行
   ✓ Mann-Whitney検定を実行
   ✓ 効果量（Cohen's d）を計算

7. 結果保存中...
   ✓ annualized_returns_3y.csv
   ✓ summary_statistics.csv
   ✓ statistical_tests.csv
   ✓ ranking_active_hedge_なし.csv
   ✓ ranking_active_hedge_あり.csv

============================================================
分析が完了しました！
============================================================
```

### ステップ5: ロバストネス分析の実行

```bash
python3 robustness_analysis.py
```

### ステップ6: 可視化の実行

```bash
python3 visualization.py
```

### ステップ7: 結果の確認

```bash
cd ../output
ls -lh
```

**生成されるファイル:**
- `annualized_returns_3y.csv`: 全ファンドの年率リターン
- `summary_statistics.csv`: 集計統計量
- `statistical_tests.csv`: 統計検定結果
- `ranking_active_hedge_*.csv`: ランキング
- `rolling_36month_analysis.csv`: ローリング分析詳細
- `rolling_analysis_summary.csv`: ローリング分析サマリー
- `histogram_returns_hedge_*.png`: ヒストグラム
- `boxplot_returns_hedge_*.png`: 箱ひげ図
- `rolling_excess_returns_hedge_*.png`: ローリング超過リターン推移
- `comparison_bar_chart.png`: 比較バーチャート

---

## 本番データでの実行

サンプルデータで動作確認ができたら、実際のファンドデータで分析を実行してください。

### データ準備

1. `data/fund_attributes.csv`を実際のデータで置き換え
2. `data/monthly_returns.csv`を実際のデータで置き換え
3. データ仕様は`data_requirements.md`を参照

### 基準日の変更

`scripts/fund_performance_analysis.py`の`BASE_DATE`変数を編集:

```python
BASE_DATE = "2024-12-31"  # 例: 2024年12月31日基準
```

### 再実行

```bash
cd scripts
python3 fund_performance_analysis.py
python3 robustness_analysis.py
python3 visualization.py
```

---

## トラブルシューティング

### エラー: ModuleNotFoundError

**原因**: 依存パッケージがインストールされていない

**解決策**:
```bash
pip3 install -r requirements.txt
```

### エラー: FileNotFoundError

**原因**: データファイルが存在しない

**解決策**:
```bash
# サンプルデータを生成
python3 scripts/generate_sample_data.py
```

### エラー: 36か月要件を満たさない

**原因**: データ期間が不足している

**解決策**:
- `generate_sample_data.py`の`n_months`を増やす
- または、実際のデータで36か月以上のデータを用意

---

## 次のステップ

1. **結果の解釈**: `output/summary_statistics.csv`と`output/statistical_tests.csv`を確認
2. **レポート作成**: エグゼクティブサマリーと本編レポートを作成
3. **GitHubへのコミット**: 結果をリポジトリにコミット

---

## さらに詳しく

- **完全なドキュメント**: `README.md`
- **データ要件**: `data_requirements.md`
- **実行手順**: `docs/execution_guide.md`
- **アーキテクチャ**: `ARCHITECTURE.md`
- **AI実行用プロンプト**: `docs/AI_EXECUTION_PROMPT.md`

---

**質問やサポートが必要な場合は、GitHubのIssuesでお問い合わせください。**
