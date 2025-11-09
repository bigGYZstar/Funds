#!/usr/bin/env python3
"""
可視化スクリプト
- ヒストグラム
- 箱ひげ図
- ローリング超過リターン推移
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
plt.rcParams['axes.unicode_minus'] = False


class FundVisualization:
    """ファンドパフォーマンス可視化クラス"""
    
    def __init__(self, output_dir: str = "../output"):
        """初期化"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # データ読み込み
        self.annualized_returns = None
        self.rolling_results = None
        
    def load_results(self):
        """分析結果の読み込み"""
        print("=" * 80)
        print("可視化: 分析結果読み込み")
        print("=" * 80)
        
        # 年率リターン
        returns_path = self.output_dir / "annualized_returns_3y.csv"
        if returns_path.exists():
            self.annualized_returns = pd.read_csv(returns_path)
            print(f"✓ 年率リターンデータ読み込み完了")
        else:
            print(f"⚠ 年率リターンデータが見つかりません: {returns_path}")
        
        # ローリング分析結果
        rolling_path = self.output_dir / "rolling_36month_analysis.csv"
        if rolling_path.exists():
            self.rolling_results = pd.read_csv(rolling_path)
            self.rolling_results['window_end'] = pd.to_datetime(self.rolling_results['window_end'])
            print(f"✓ ローリング分析結果読み込み完了")
        else:
            print(f"⚠ ローリング分析結果が見つかりません: {rolling_path}")
        
        return self
    
    def plot_return_distribution_histogram(self):
        """年率リターン分布のヒストグラム"""
        if self.annualized_returns is None:
            print("⚠ 年率リターンデータがありません")
            return self
        
        print("\n" + "=" * 80)
        print("ヒストグラム作成")
        print("=" * 80)
        
        for hedge_status in ['なし', 'あり']:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            fig.suptitle(f'3年年率リターン分布（為替ヘッジ: {hedge_status}）', 
                        fontsize=16, fontweight='bold')
            
            # アクティブファンド
            active_data = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'アクティブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]['annualized_return_3y'] * 100
            
            # パッシブファンド
            passive_data = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'パッシブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]['annualized_return_3y'] * 100
            
            if len(active_data) == 0:
                print(f"  ⚠ アクティブファンドデータなし（ヘッジ{hedge_status}）")
                plt.close(fig)
                continue
            
            # アクティブのヒストグラム
            axes[0].hist(active_data, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
            axes[0].axvline(active_data.mean(), color='red', linestyle='--', linewidth=2, 
                          label=f'平均: {active_data.mean():.2f}%')
            axes[0].axvline(active_data.median(), color='green', linestyle='--', linewidth=2,
                          label=f'中央値: {active_data.median():.2f}%')
            axes[0].set_xlabel('3年年率リターン (%)', fontsize=12)
            axes[0].set_ylabel('ファンド数', fontsize=12)
            axes[0].set_title('アクティブファンド', fontsize=14)
            axes[0].legend()
            axes[0].grid(alpha=0.3)
            
            # パッシブの参照線を追加
            if len(passive_data) > 0:
                axes[0].axvline(passive_data.mean(), color='orange', linestyle=':', linewidth=2,
                              label=f'パッシブ平均: {passive_data.mean():.2f}%')
                axes[0].legend()
            
            # 比較ヒストグラム
            axes[1].hist(active_data, bins=20, alpha=0.5, color='steelblue', 
                        label=f'アクティブ (n={len(active_data)})', edgecolor='black')
            if len(passive_data) > 0:
                axes[1].hist(passive_data, bins=10, alpha=0.5, color='orange',
                           label=f'パッシブ (n={len(passive_data)})', edgecolor='black')
            axes[1].set_xlabel('3年年率リターン (%)', fontsize=12)
            axes[1].set_ylabel('ファンド数', fontsize=12)
            axes[1].set_title('アクティブ vs パッシブ', fontsize=14)
            axes[1].legend()
            axes[1].grid(alpha=0.3)
            
            plt.tight_layout()
            filename = f"histogram_returns_hedge_{hedge_status}.png"
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ ヒストグラム保存（ヘッジ{hedge_status}）: {filename}")
        
        return self
    
    def plot_boxplot(self):
        """箱ひげ図"""
        if self.annualized_returns is None:
            print("⚠ 年率リターンデータがありません")
            return self
        
        print("\n" + "=" * 80)
        print("箱ひげ図作成")
        print("=" * 80)
        
        for hedge_status in ['なし', 'あり']:
            # データ抽出
            active_data = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'アクティブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]['annualized_return_3y'] * 100
            
            passive_data = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'パッシブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]['annualized_return_3y'] * 100
            
            if len(active_data) == 0:
                print(f"  ⚠ アクティブファンドデータなし（ヘッジ{hedge_status}）")
                continue
            
            # 箱ひげ図
            fig, ax = plt.subplots(figsize=(10, 6))
            
            data_to_plot = [active_data]
            labels = ['アクティブ']
            
            if len(passive_data) > 0:
                data_to_plot.append(passive_data)
                labels.append('パッシブ')
            
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                           showmeans=True, meanline=True)
            
            # 色設定
            colors = ['steelblue', 'orange']
            for patch, color in zip(bp['boxes'], colors[:len(data_to_plot)]):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            ax.set_ylabel('3年年率リターン (%)', fontsize=12)
            ax.set_title(f'3年年率リターン分布（為替ヘッジ: {hedge_status}）', 
                        fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            filename = f"boxplot_returns_hedge_{hedge_status}.png"
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ 箱ひげ図保存（ヘッジ{hedge_status}）: {filename}")
        
        return self
    
    def plot_rolling_excess_returns(self):
        """ローリング超過リターン推移"""
        if self.rolling_results is None:
            print("⚠ ローリング分析結果がありません")
            return self
        
        print("\n" + "=" * 80)
        print("ローリング超過リターン推移グラフ作成")
        print("=" * 80)
        
        for hedge_status in ['なし', 'あり']:
            data = self.rolling_results[self.rolling_results['currency_hedge'] == hedge_status]
            
            if len(data) == 0:
                print(f"  ⚠ データなし（ヘッジ{hedge_status}）")
                continue
            
            fig, axes = plt.subplots(2, 1, figsize=(14, 10))
            fig.suptitle(f'ローリング36か月超過リターン推移（為替ヘッジ: {hedge_status}）',
                        fontsize=16, fontweight='bold')
            
            # 等金額平均
            axes[0].plot(data['window_end'], data['excess_all_equal'] * 100,
                        marker='o', label='アクティブ全体 vs パッシブ', linewidth=2)
            axes[0].plot(data['window_end'], data['excess_top50_equal'] * 100,
                        marker='s', label='アクティブ上位50% vs パッシブ', linewidth=2)
            axes[0].axhline(0, color='black', linestyle='--', linewidth=1)
            axes[0].set_ylabel('超過リターン (%, 等金額平均)', fontsize=12)
            axes[0].set_title('等金額平均', fontsize=14)
            axes[0].legend()
            axes[0].grid(alpha=0.3)
            
            # AUM加重平均
            axes[1].plot(data['window_end'], data['excess_all_aum'] * 100,
                        marker='o', label='アクティブ全体 vs パッシブ', linewidth=2, color='C2')
            axes[1].plot(data['window_end'], data['excess_top50_aum'] * 100,
                        marker='s', label='アクティブ上位50% vs パッシブ', linewidth=2, color='C3')
            axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
            axes[1].set_xlabel('ウィンドウ終了月', fontsize=12)
            axes[1].set_ylabel('超過リターン (%, AUM加重平均)', fontsize=12)
            axes[1].set_title('AUM加重平均', fontsize=14)
            axes[1].legend()
            axes[1].grid(alpha=0.3)
            
            plt.tight_layout()
            filename = f"rolling_excess_returns_hedge_{hedge_status}.png"
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ ローリング超過リターン推移保存（ヘッジ{hedge_status}）: {filename}")
        
        return self
    
    def plot_top50_comparison(self):
        """上位50%とパッシブの比較バーチャート"""
        if self.annualized_returns is None:
            print("⚠ 年率リターンデータがありません")
            return self
        
        print("\n" + "=" * 80)
        print("上位50%比較バーチャート作成")
        print("=" * 80)
        
        summary_data = []
        
        for hedge_status in ['なし', 'あり']:
            active_funds = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'アクティブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]
            
            passive_funds = self.annualized_returns[
                (self.annualized_returns['fund_type'] == 'パッシブ') &
                (self.annualized_returns['currency_hedge'] == hedge_status)
            ]
            
            if len(active_funds) == 0 or len(passive_funds) == 0:
                continue
            
            # 上位50%
            active_sorted = active_funds.sort_values('annualized_return_3y', ascending=False)
            top_50_count = int(np.ceil(0.5 * len(active_sorted)))
            top_50_funds = active_sorted.iloc[:top_50_count]
            
            summary_data.append({
                'hedge': hedge_status,
                'category': 'アクティブ全体',
                'return': active_funds['annualized_return_3y'].mean() * 100
            })
            summary_data.append({
                'hedge': hedge_status,
                'category': 'アクティブ上位50%',
                'return': top_50_funds['annualized_return_3y'].mean() * 100
            })
            summary_data.append({
                'hedge': hedge_status,
                'category': 'パッシブ',
                'return': passive_funds['annualized_return_3y'].mean() * 100
            })
        
        if len(summary_data) == 0:
            print("  ⚠ 比較データなし")
            return self
        
        summary_df = pd.DataFrame(summary_data)
        
        # バーチャート
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('3年年率リターン比較', fontsize=16, fontweight='bold')
        
        for idx, hedge_status in enumerate(['なし', 'あり']):
            data = summary_df[summary_df['hedge'] == hedge_status]
            
            if len(data) == 0:
                continue
            
            ax = axes[idx]
            bars = ax.bar(data['category'], data['return'], 
                         color=['steelblue', 'darkblue', 'orange'],
                         alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # 値ラベル
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}%',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.set_ylabel('3年年率リターン (%)', fontsize=12)
            ax.set_title(f'為替ヘッジ: {hedge_status}', fontsize=14)
            ax.grid(axis='y', alpha=0.3)
            ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        filename = "comparison_bar_chart.png"
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 比較バーチャート保存: {filename}")
        
        return self


def main():
    """メイン実行関数"""
    
    print("\n")
    print("=" * 80)
    print("可視化スクリプト実行")
    print("=" * 80)
    
    try:
        viz = FundVisualization()
        
        viz.load_results() \
           .plot_return_distribution_histogram() \
           .plot_boxplot() \
           .plot_rolling_excess_returns() \
           .plot_top50_comparison()
        
        print("\n" + "=" * 80)
        print("可視化完了")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
