#!/usr/bin/env python3
"""
日本籍米国株式アクティブ投信パフォーマンス検証
統計分析メインスクリプト

依頼概要：
- アクティブ全体の平均 vs パッシブ
- アクティブ上位50％の平均 vs パッシブ
- 統計的検定とロバストネス分析
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')


class FundPerformanceAnalyzer:
    """ファンドパフォーマンス分析クラス"""
    
    def __init__(self, base_date: str, data_dir: str = "../data"):
        """
        初期化
        
        Parameters:
        -----------
        base_date : str
            基準日（YYYY-MM-DD形式）
        data_dir : str
            データディレクトリパス
        """
        self.base_date = pd.to_datetime(base_date)
        self.data_dir = Path(data_dir)
        self.analysis_period_months = 36
        
        # データ格納用
        self.fund_attributes = None
        self.monthly_returns = None
        self.analysis_results = {}
        
    def load_data(self):
        """データファイルの読み込み"""
        print("=" * 80)
        print("データ読み込み開始")
        print("=" * 80)
        
        # ファンド属性データ
        attr_path = self.data_dir / "fund_attributes.csv"
        if not attr_path.exists():
            raise FileNotFoundError(f"ファンド属性データが見つかりません: {attr_path}")
        
        self.fund_attributes = pd.read_csv(attr_path)
        print(f"✓ ファンド属性データ読み込み完了: {len(self.fund_attributes)} ファンド")
        
        # 月次リターンデータ
        returns_path = self.data_dir / "monthly_returns.csv"
        if not returns_path.exists():
            raise FileNotFoundError(f"月次リターンデータが見つかりません: {returns_path}")
        
        self.monthly_returns = pd.read_csv(returns_path)
        self.monthly_returns['month_end_date'] = pd.to_datetime(self.monthly_returns['month_end_date'])
        print(f"✓ 月次リターンデータ読み込み完了: {len(self.monthly_returns)} レコード")
        
        return self
    
    def validate_and_clean_data(self):
        """データ品質チェックとクレンジング"""
        print("\n" + "=" * 80)
        print("データ品質チェックとクレンジング")
        print("=" * 80)
        
        # 基準日から36か月前の開始日を計算
        end_date = self.base_date
        start_date = end_date - pd.DateOffset(months=self.analysis_period_months - 1)
        
        print(f"分析期間: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}")
        
        # 期間内のリターンデータをフィルタ
        self.monthly_returns = self.monthly_returns[
            (self.monthly_returns['month_end_date'] >= start_date) &
            (self.monthly_returns['month_end_date'] <= end_date)
        ]
        
        # 各ファンドの月次データ数をカウント
        month_counts = self.monthly_returns.groupby('fund_id').size()
        
        # 36か月のデータがあるファンドのみ採用
        valid_funds = month_counts[month_counts == self.analysis_period_months].index
        excluded_funds = month_counts[month_counts < self.analysis_period_months].index
        
        print(f"\n36か月データ要件:")
        print(f"  - 条件を満たすファンド: {len(valid_funds)} 本")
        print(f"  - 除外されたファンド: {len(excluded_funds)} 本")
        
        # 除外ファンドリストを保存
        if len(excluded_funds) > 0:
            excluded_df = pd.DataFrame({
                'fund_id': excluded_funds,
                'data_months': month_counts[excluded_funds],
                'exclusion_reason': '36か月未満のトラックレコード'
            })
            excluded_df.to_csv(self.data_dir.parent / "output" / "excluded_funds_insufficient_data.csv", 
                             index=False, encoding='utf-8-sig')
        
        # 有効なファンドのみに絞り込み
        self.monthly_returns = self.monthly_returns[self.monthly_returns['fund_id'].isin(valid_funds)]
        self.fund_attributes = self.fund_attributes[self.fund_attributes['fund_id'].isin(valid_funds)]
        
        # 異常値チェック（±50%を超えるリターン）
        outliers = self.monthly_returns[
            (self.monthly_returns['monthly_return'] > 0.5) | 
            (self.monthly_returns['monthly_return'] < -0.5)
        ]
        
        if len(outliers) > 0:
            print(f"\n⚠ 異常値検出: {len(outliers)} レコード（±50%超）")
            outliers.to_csv(self.data_dir.parent / "output" / "outliers_detected.csv", 
                          index=False, encoding='utf-8-sig')
        
        print(f"\n✓ クレンジング完了")
        print(f"  - 有効ファンド数: {len(self.fund_attributes)}")
        print(f"  - 有効リターンレコード数: {len(self.monthly_returns)}")
        
        return self
    
    def calculate_annualized_returns(self):
        """3年年率リターン（CAGR）の計算"""
        print("\n" + "=" * 80)
        print("3年年率リターン（CAGR）計算")
        print("=" * 80)
        
        results = []
        
        for fund_id in self.fund_attributes['fund_id']:
            fund_returns = self.monthly_returns[
                self.monthly_returns['fund_id'] == fund_id
            ].sort_values('month_end_date')
            
            if len(fund_returns) != self.analysis_period_months:
                continue
            
            # 幾何平均による年率リターン計算
            # R_ann = (∏(1 + r_t))^(12/36) - 1
            monthly_returns = fund_returns['monthly_return'].values
            cumulative_return = np.prod(1 + monthly_returns)
            annualized_return = cumulative_return ** (12 / self.analysis_period_months) - 1
            
            # ファンド属性を取得
            fund_attr = self.fund_attributes[self.fund_attributes['fund_id'] == fund_id].iloc[0]
            
            results.append({
                'fund_id': fund_id,
                'fund_name': fund_attr['fund_name'],
                'fund_type': fund_attr['fund_type'],
                'currency_hedge': fund_attr['currency_hedge'],
                'expense_ratio': fund_attr['expense_ratio'],
                'aum_latest': fund_attr['aum_latest'],
                'annualized_return_3y': annualized_return,
                'cumulative_return_3y': cumulative_return - 1
            })
        
        self.annualized_returns = pd.DataFrame(results)
        print(f"✓ {len(self.annualized_returns)} ファンドの年率リターンを計算")
        
        return self
    
    def rank_and_segment_funds(self):
        """ランキングと上位50％の抽出"""
        print("\n" + "=" * 80)
        print("ランキングと上位50％抽出")
        print("=" * 80)
        
        # ヘッジ区分ごとに処理
        for hedge_status in ['なし', 'あり']:
            print(f"\n【為替ヘッジ: {hedge_status}】")
            
            # アクティブファンドのみ抽出
            active_funds = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'アクティブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ].copy()
            
            if len(active_funds) == 0:
                print(f"  ⚠ アクティブファンドが存在しません")
                continue
            
            # 降順にソート
            active_funds = active_funds.sort_values('annualized_return_3y', ascending=False).reset_index(drop=True)
            active_funds['rank'] = active_funds.index + 1
            
            # 上位50％の閾値
            top_50_count = int(np.ceil(0.5 * len(active_funds)))
            active_funds['is_top_50'] = active_funds['rank'] <= top_50_count
            
            print(f"  - アクティブファンド総数: {len(active_funds)}")
            print(f"  - 上位50％本数: {top_50_count}")
            print(f"  - 上位50％閾値リターン: {active_funds.iloc[top_50_count - 1]['annualized_return_3y']:.4f}")
            
            # パッシブファンド（S&P500連動）
            passive_funds = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'パッシブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]
            
            print(f"  - パッシブファンド数: {len(passive_funds)}")
            
            # 結果を保存
            key = f"hedge_{hedge_status}"
            self.analysis_results[key] = {
                'active_funds': active_funds,
                'passive_funds': passive_funds,
                'top_50_count': top_50_count
            }
        
        return self
    
    def calculate_aggregate_statistics(self):
        """集計統計量の計算"""
        print("\n" + "=" * 80)
        print("集計統計量計算")
        print("=" * 80)
        
        summary_results = []
        
        for hedge_status in ['なし', 'あり']:
            key = f"hedge_{hedge_status}"
            
            if key not in self.analysis_results:
                continue
            
            data = self.analysis_results[key]
            active_funds = data['active_funds']
            passive_funds = data['passive_funds']
            
            if len(active_funds) == 0 or len(passive_funds) == 0:
                continue
            
            print(f"\n【為替ヘッジ: {hedge_status}】")
            
            # アクティブ全体
            active_all_equal_weight = active_funds['annualized_return_3y'].mean()
            active_all_aum_weight = np.average(
                active_funds['annualized_return_3y'],
                weights=active_funds['aum_latest']
            )
            
            # アクティブ上位50％
            top_50_funds = active_funds[active_funds['is_top_50']]
            active_top50_equal_weight = top_50_funds['annualized_return_3y'].mean()
            active_top50_aum_weight = np.average(
                top_50_funds['annualized_return_3y'],
                weights=top_50_funds['aum_latest']
            )
            
            # パッシブ
            passive_equal_weight = passive_funds['annualized_return_3y'].mean()
            passive_aum_weight = np.average(
                passive_funds['annualized_return_3y'],
                weights=passive_funds['aum_latest']
            )
            
            # 超過リターン
            excess_all_equal = active_all_equal_weight - passive_equal_weight
            excess_all_aum = active_all_aum_weight - passive_aum_weight
            excess_top50_equal = active_top50_equal_weight - passive_equal_weight
            excess_top50_aum = active_top50_aum_weight - passive_aum_weight
            
            summary_results.append({
                'currency_hedge': hedge_status,
                'weighting': '等金額',
                'active_all_mean': active_all_equal_weight,
                'active_top50_mean': active_top50_equal_weight,
                'passive_mean': passive_equal_weight,
                'excess_all': excess_all_equal,
                'excess_top50': excess_top50_equal
            })
            
            summary_results.append({
                'currency_hedge': hedge_status,
                'weighting': 'AUM加重',
                'active_all_mean': active_all_aum_weight,
                'active_top50_mean': active_top50_aum_weight,
                'passive_mean': passive_aum_weight,
                'excess_all': excess_all_aum,
                'excess_top50': excess_top50_aum
            })
            
            print(f"  等金額平均:")
            print(f"    - アクティブ全体: {active_all_equal_weight:.4f} ({active_all_equal_weight*100:.2f}%)")
            print(f"    - アクティブ上位50%: {active_top50_equal_weight:.4f} ({active_top50_equal_weight*100:.2f}%)")
            print(f"    - パッシブ: {passive_equal_weight:.4f} ({passive_equal_weight*100:.2f}%)")
            print(f"    - 超過リターン（全体）: {excess_all_equal:.4f} ({excess_all_equal*100:.2f}%)")
            print(f"    - 超過リターン（上位50%）: {excess_top50_equal:.4f} ({excess_top50_equal*100:.2f}%)")
        
        self.summary_statistics = pd.DataFrame(summary_results)
        
        return self
    
    def perform_statistical_tests(self):
        """統計的検定の実行"""
        print("\n" + "=" * 80)
        print("統計的検定")
        print("=" * 80)
        
        test_results = []
        
        for hedge_status in ['なし', 'あり']:
            key = f"hedge_{hedge_status}"
            
            if key not in self.analysis_results:
                continue
            
            data = self.analysis_results[key]
            active_funds = data['active_funds']
            passive_funds = data['passive_funds']
            
            if len(active_funds) == 0 or len(passive_funds) == 0:
                continue
            
            print(f"\n【為替ヘッジ: {hedge_status}】")
            
            # アクティブ全体 vs パッシブ
            active_all_returns = active_funds['annualized_return_3y'].values
            passive_returns = passive_funds['annualized_return_3y'].values
            
            # t検定
            t_stat_all, p_value_all = stats.ttest_ind(active_all_returns, passive_returns)
            
            # Cohen's d（効果量）
            pooled_std_all = np.sqrt(
                ((len(active_all_returns) - 1) * np.var(active_all_returns, ddof=1) +
                 (len(passive_returns) - 1) * np.var(passive_returns, ddof=1)) /
                (len(active_all_returns) + len(passive_returns) - 2)
            )
            cohens_d_all = (np.mean(active_all_returns) - np.mean(passive_returns)) / pooled_std_all
            
            # Mann-Whitney U検定
            u_stat_all, p_value_mw_all = stats.mannwhitneyu(
                active_all_returns, passive_returns, alternative='two-sided'
            )
            
            print(f"\n  アクティブ全体 vs パッシブ:")
            print(f"    - t検定: t={t_stat_all:.4f}, p={p_value_all:.4f}")
            print(f"    - Cohen's d: {cohens_d_all:.4f}")
            print(f"    - Mann-Whitney: U={u_stat_all:.2f}, p={p_value_mw_all:.4f}")
            
            test_results.append({
                'currency_hedge': hedge_status,
                'comparison': 'アクティブ全体 vs パッシブ',
                't_statistic': t_stat_all,
                'p_value_ttest': p_value_all,
                'cohens_d': cohens_d_all,
                'u_statistic': u_stat_all,
                'p_value_mannwhitney': p_value_mw_all,
                'significant_5pct': p_value_all < 0.05
            })
            
            # アクティブ上位50% vs パッシブ
            top_50_returns = active_funds[active_funds['is_top_50']]['annualized_return_3y'].values
            
            t_stat_top50, p_value_top50 = stats.ttest_ind(top_50_returns, passive_returns)
            
            pooled_std_top50 = np.sqrt(
                ((len(top_50_returns) - 1) * np.var(top_50_returns, ddof=1) +
                 (len(passive_returns) - 1) * np.var(passive_returns, ddof=1)) /
                (len(top_50_returns) + len(passive_returns) - 2)
            )
            cohens_d_top50 = (np.mean(top_50_returns) - np.mean(passive_returns)) / pooled_std_top50
            
            u_stat_top50, p_value_mw_top50 = stats.mannwhitneyu(
                top_50_returns, passive_returns, alternative='two-sided'
            )
            
            print(f"\n  アクティブ上位50% vs パッシブ:")
            print(f"    - t検定: t={t_stat_top50:.4f}, p={p_value_top50:.4f}")
            print(f"    - Cohen's d: {cohens_d_top50:.4f}")
            print(f"    - Mann-Whitney: U={u_stat_top50:.2f}, p={p_value_mw_top50:.4f}")
            
            test_results.append({
                'currency_hedge': hedge_status,
                'comparison': 'アクティブ上位50% vs パッシブ',
                't_statistic': t_stat_top50,
                'p_value_ttest': p_value_top50,
                'cohens_d': cohens_d_top50,
                'u_statistic': u_stat_top50,
                'p_value_mannwhitney': p_value_mw_top50,
                'significant_5pct': p_value_top50 < 0.05
            })
        
        self.test_results = pd.DataFrame(test_results)
        
        return self
    
    def save_results(self, output_dir: str = "../output"):
        """結果の保存"""
        print("\n" + "=" * 80)
        print("結果保存")
        print("=" * 80)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 年率リターン一覧
        self.annualized_returns.to_csv(
            output_path / "annualized_returns_3y.csv",
            index=False, encoding='utf-8-sig'
        )
        print(f"✓ 年率リターン一覧保存: annualized_returns_3y.csv")
        
        # 集計統計量
        self.summary_statistics.to_csv(
            output_path / "summary_statistics.csv",
            index=False, encoding='utf-8-sig'
        )
        print(f"✓ 集計統計量保存: summary_statistics.csv")
        
        # 統計検定結果
        self.test_results.to_csv(
            output_path / "statistical_tests.csv",
            index=False, encoding='utf-8-sig'
        )
        print(f"✓ 統計検定結果保存: statistical_tests.csv")
        
        # ヘッジ区分別の詳細ランキング
        for hedge_status in ['なし', 'あり']:
            key = f"hedge_{hedge_status}"
            if key in self.analysis_results:
                active_funds = self.analysis_results[key]['active_funds']
                filename = f"ranking_active_hedge_{hedge_status}.csv"
                active_funds.to_csv(
                    output_path / filename,
                    index=False, encoding='utf-8-sig'
                )
                print(f"✓ ランキング保存（ヘッジ{hedge_status}）: {filename}")
        
        print(f"\n✓ すべての結果を {output_path} に保存しました")
        
        return self


def main():
    """メイン実行関数"""
    
    # 基準日の設定（ここを変更してください）
    BASE_DATE = "2024-10-31"  # 例: 2024年10月末
    
    print("\n")
    print("=" * 80)
    print("日本籍米国株式アクティブ投信パフォーマンス検証")
    print("=" * 80)
    print(f"基準日: {BASE_DATE}")
    print(f"分析期間: 過去36か月")
    print("=" * 80)
    
    try:
        # 分析実行
        analyzer = FundPerformanceAnalyzer(base_date=BASE_DATE)
        
        analyzer.load_data() \
                .validate_and_clean_data() \
                .calculate_annualized_returns() \
                .rank_and_segment_funds() \
                .calculate_aggregate_statistics() \
                .perform_statistical_tests() \
                .save_results()
        
        print("\n" + "=" * 80)
        print("分析完了")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
