#!/usr/bin/env python3
"""
ロバストネス分析スクリプト
- ローリング36か月分析
- 起点を1か月ずつずらして超過リターンの安定性を確認
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class RobustnessAnalyzer:
    """ロバストネス分析クラス"""
    
    def __init__(self, data_dir: str = "../data"):
        """初期化"""
        self.data_dir = Path(data_dir)
        self.analysis_period_months = 36
        
        # データ格納用
        self.fund_attributes = None
        self.monthly_returns = None
        self.rolling_results = []
        
    def load_data(self):
        """データファイルの読み込み"""
        print("=" * 80)
        print("ロバストネス分析: データ読み込み")
        print("=" * 80)
        
        # ファンド属性データ
        attr_path = self.data_dir / "fund_attributes.csv"
        self.fund_attributes = pd.read_csv(attr_path)
        print(f"✓ ファンド属性データ読み込み完了: {len(self.fund_attributes)} ファンド")
        
        # 月次リターンデータ
        returns_path = self.data_dir / "monthly_returns.csv"
        self.monthly_returns = pd.read_csv(returns_path)
        self.monthly_returns['month_end_date'] = pd.to_datetime(self.monthly_returns['month_end_date'])
        print(f"✓ 月次リターンデータ読み込み完了: {len(self.monthly_returns)} レコード")
        
        return self
    
    def calculate_rolling_analysis(self, min_windows: int = 12):
        """
        ローリング36か月分析
        
        Parameters:
        -----------
        min_windows : int
            最低ウィンドウ数（デフォルト12）
        """
        print("\n" + "=" * 80)
        print(f"ローリング36か月分析（最低{min_windows}起点）")
        print("=" * 80)
        
        # 利用可能な月末日付を取得
        all_dates = sorted(self.monthly_returns['month_end_date'].unique())
        
        # 36か月以上のデータがある期間を特定
        if len(all_dates) < self.analysis_period_months:
            raise ValueError(f"データ期間が不足しています（必要: {self.analysis_period_months}か月、実際: {len(all_dates)}か月）")
        
        # ローリングウィンドウの起点を生成
        max_start_idx = len(all_dates) - self.analysis_period_months
        window_starts = list(range(0, max_start_idx + 1))
        
        if len(window_starts) < min_windows:
            print(f"⚠ 警告: ウィンドウ数が最低要件を満たしません（実際: {len(window_starts)}、要件: {min_windows}）")
        
        print(f"分析ウィンドウ数: {len(window_starts)}")
        print(f"データ期間: {all_dates[0].strftime('%Y-%m')} ～ {all_dates[-1].strftime('%Y-%m')}")
        
        # 各ウィンドウで分析
        for window_idx, start_idx in enumerate(window_starts, 1):
            end_idx = start_idx + self.analysis_period_months - 1
            window_start_date = all_dates[start_idx]
            window_end_date = all_dates[end_idx]
            
            print(f"\nウィンドウ {window_idx}/{len(window_starts)}: "
                  f"{window_start_date.strftime('%Y-%m')} ～ {window_end_date.strftime('%Y-%m')}")
            
            # 当該期間のリターンデータを抽出
            window_returns = self.monthly_returns[
                (self.monthly_returns['month_end_date'] >= window_start_date) &
                (self.monthly_returns['month_end_date'] <= window_end_date)
            ]
            
            # 36か月のデータがあるファンドのみ
            month_counts = window_returns.groupby('fund_id').size()
            valid_funds = month_counts[month_counts == self.analysis_period_months].index
            window_returns = window_returns[window_returns['fund_id'].isin(valid_funds)]
            
            # 年率リターンを計算
            annualized_returns = self._calculate_annualized_returns_for_window(window_returns)
            
            # ヘッジ区分ごとに集計
            for hedge_status in ['なし', 'あり']:
                result = self._analyze_window_by_hedge(
                    annualized_returns, hedge_status, window_start_date, window_end_date
                )
                if result:
                    self.rolling_results.append(result)
        
        self.rolling_results_df = pd.DataFrame(self.rolling_results)
        print(f"\n✓ ローリング分析完了: {len(self.rolling_results)} 結果")
        
        return self
    
    def _calculate_annualized_returns_for_window(self, window_returns):
        """ウィンドウ内の年率リターンを計算"""
        results = []
        
        for fund_id in window_returns['fund_id'].unique():
            fund_data = window_returns[window_returns['fund_id'] == fund_id].sort_values('month_end_date')
            
            if len(fund_data) != self.analysis_period_months:
                continue
            
            # 幾何平均
            monthly_rets = fund_data['monthly_return'].values
            cumulative_return = np.prod(1 + monthly_rets)
            annualized_return = cumulative_return ** (12 / self.analysis_period_months) - 1
            
            # ファンド属性
            fund_attr = self.fund_attributes[self.fund_attributes['fund_id'] == fund_id]
            if len(fund_attr) == 0:
                continue
            
            fund_attr = fund_attr.iloc[0]
            
            results.append({
                'fund_id': fund_id,
                'fund_type': fund_attr['fund_type'],
                'currency_hedge': fund_attr['currency_hedge'],
                'aum_latest': fund_attr['aum_latest'],
                'annualized_return_3y': annualized_return
            })
        
        return pd.DataFrame(results)
    
    def _analyze_window_by_hedge(self, annualized_returns, hedge_status, start_date, end_date):
        """ヘッジ区分ごとのウィンドウ分析"""
        
        # アクティブファンド
        active_funds = annualized_returns[
            (annualized_returns['fund_type'] == 'アクティブ') &
            (annualized_returns['currency_hedge'] == hedge_status)
        ]
        
        # パッシブファンド
        passive_funds = annualized_returns[
            (annualized_returns['fund_type'] == 'パッシブ') &
            (annualized_returns['currency_hedge'] == hedge_status)
        ]
        
        if len(active_funds) == 0 or len(passive_funds) == 0:
            return None
        
        # 上位50％
        active_sorted = active_funds.sort_values('annualized_return_3y', ascending=False)
        top_50_count = int(np.ceil(0.5 * len(active_sorted)))
        top_50_funds = active_sorted.iloc[:top_50_count]
        
        # 等金額平均
        active_all_mean = active_funds['annualized_return_3y'].mean()
        active_top50_mean = top_50_funds['annualized_return_3y'].mean()
        passive_mean = passive_funds['annualized_return_3y'].mean()
        
        # AUM加重平均
        active_all_aum = np.average(
            active_funds['annualized_return_3y'],
            weights=active_funds['aum_latest']
        )
        active_top50_aum = np.average(
            top_50_funds['annualized_return_3y'],
            weights=top_50_funds['aum_latest']
        )
        passive_aum = np.average(
            passive_funds['annualized_return_3y'],
            weights=passive_funds['aum_latest']
        )
        
        # 超過リターン
        excess_all_equal = active_all_mean - passive_mean
        excess_top50_equal = active_top50_mean - passive_mean
        excess_all_aum = active_all_aum - passive_aum
        excess_top50_aum = active_top50_aum - passive_aum
        
        return {
            'window_start': start_date,
            'window_end': end_date,
            'currency_hedge': hedge_status,
            'active_count': len(active_funds),
            'passive_count': len(passive_funds),
            'top_50_count': top_50_count,
            'active_all_mean_equal': active_all_mean,
            'active_top50_mean_equal': active_top50_mean,
            'passive_mean_equal': passive_mean,
            'excess_all_equal': excess_all_equal,
            'excess_top50_equal': excess_top50_equal,
            'active_all_mean_aum': active_all_aum,
            'active_top50_mean_aum': active_top50_aum,
            'passive_mean_aum': passive_aum,
            'excess_all_aum': excess_all_aum,
            'excess_top50_aum': excess_top50_aum
        }
    
    def save_results(self, output_dir: str = "../output"):
        """結果の保存"""
        print("\n" + "=" * 80)
        print("ロバストネス分析結果保存")
        print("=" * 80)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # ローリング分析結果
        self.rolling_results_df.to_csv(
            output_path / "rolling_36month_analysis.csv",
            index=False, encoding='utf-8-sig'
        )
        print(f"✓ ローリング36か月分析結果保存: rolling_36month_analysis.csv")
        
        # サマリー統計
        summary = self.rolling_results_df.groupby('currency_hedge').agg({
            'excess_all_equal': ['mean', 'std', 'min', 'max'],
            'excess_top50_equal': ['mean', 'std', 'min', 'max'],
            'excess_all_aum': ['mean', 'std', 'min', 'max'],
            'excess_top50_aum': ['mean', 'std', 'min', 'max']
        }).round(4)
        
        summary.to_csv(
            output_path / "rolling_analysis_summary.csv",
            encoding='utf-8-sig'
        )
        print(f"✓ ローリング分析サマリー保存: rolling_analysis_summary.csv")
        
        print(f"\n✓ すべての結果を {output_path} に保存しました")
        
        return self


def main():
    """メイン実行関数"""
    
    print("\n")
    print("=" * 80)
    print("ロバストネス分析（ローリング36か月）")
    print("=" * 80)
    
    try:
        analyzer = RobustnessAnalyzer()
        
        analyzer.load_data() \
                .calculate_rolling_analysis(min_windows=12) \
                .save_results()
        
        print("\n" + "=" * 80)
        print("ロバストネス分析完了")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
