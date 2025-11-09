#!/usr/bin/env python3
"""
サンプルデータ生成スクリプト

公開データの収集が困難な場合に、分析フレームワークの動作確認用の
サンプルデータを生成します。

実際のファンドパフォーマンスに基づいたリアリスティックなデータを生成します。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 乱数シードの設定（再現性のため）
np.random.seed(42)

def generate_fund_attributes():
    """
    ファンド属性データを生成する
    
    Returns:
        pd.DataFrame: ファンド属性データ
    """
    # アクティブファンド（ヘッジなし）
    active_no_hedge = []
    for i in range(10):
        active_no_hedge.append({
            'fund_id': f'ACT_NH_{i+1:03d}',
            'fund_name': f'米国株式アクティブファンド{i+1}（為替ヘッジなし）',
            'management_company': f'運用会社{(i % 5) + 1}',
            'inception_date': (datetime(2020, 1, 1) - timedelta(days=np.random.randint(365, 3650))).strftime('%Y-%m-%d'),
            'share_class': 'A',
            'currency_hedge': 'なし',
            'benchmark': 'S&P500指数（円換算ベース）',
            'expense_ratio': round(np.random.uniform(0.5, 1.8), 2),
            'aum_latest': round(np.random.uniform(1000, 50000), 2),
            'fund_type': 'アクティブ',
            'is_index_fund': False,
            'investment_style': np.random.choice(['成長', 'バリュー', 'ブレンド']),
            'is_theme_fund': False,
            'is_leveraged': False,
            'is_fund_of_funds': False,
            'status': '運用中',
            'redemption_date': '',
            'inclusion_reason': '米国株式アクティブファンド、36か月以上のトラックレコードあり'
        })
    
    # アクティブファンド（ヘッジあり）
    active_hedge = []
    for i in range(10):
        active_hedge.append({
            'fund_id': f'ACT_H_{i+1:03d}',
            'fund_name': f'米国株式アクティブファンド{i+1}（為替ヘッジあり）',
            'management_company': f'運用会社{(i % 5) + 1}',
            'inception_date': (datetime(2020, 1, 1) - timedelta(days=np.random.randint(365, 3650))).strftime('%Y-%m-%d'),
            'share_class': 'A',
            'currency_hedge': 'あり',
            'benchmark': 'S&P500指数（円ヘッジベース）',
            'expense_ratio': round(np.random.uniform(0.7, 2.0), 2),
            'aum_latest': round(np.random.uniform(1000, 50000), 2),
            'fund_type': 'アクティブ',
            'is_index_fund': False,
            'investment_style': np.random.choice(['成長', 'バリュー', 'ブレンド']),
            'is_theme_fund': False,
            'is_leveraged': False,
            'is_fund_of_funds': False,
            'status': '運用中',
            'redemption_date': '',
            'inclusion_reason': '米国株式アクティブファンド、36か月以上のトラックレコードあり'
        })
    
    # パッシブファンド（ヘッジなし）
    passive_no_hedge = []
    for i in range(3):
        passive_no_hedge.append({
            'fund_id': f'PAS_NH_{i+1:03d}',
            'fund_name': f'米国株式インデックスファンド{i+1}（為替ヘッジなし）',
            'management_company': f'運用会社{(i % 3) + 1}',
            'inception_date': (datetime(2020, 1, 1) - timedelta(days=np.random.randint(365, 3650))).strftime('%Y-%m-%d'),
            'share_class': 'A',
            'currency_hedge': 'なし',
            'benchmark': 'S&P500指数（円換算ベース）',
            'expense_ratio': round(np.random.uniform(0.05, 0.3), 2),
            'aum_latest': round(np.random.uniform(10000, 100000), 2),
            'fund_type': 'パッシブ',
            'is_index_fund': True,
            'investment_style': 'ブレンド',
            'is_theme_fund': False,
            'is_leveraged': False,
            'is_fund_of_funds': False,
            'status': '運用中',
            'redemption_date': '',
            'inclusion_reason': 'S&P500連動パッシブファンド、36か月以上のトラックレコードあり'
        })
    
    # パッシブファンド（ヘッジあり）
    passive_hedge = []
    for i in range(3):
        passive_hedge.append({
            'fund_id': f'PAS_H_{i+1:03d}',
            'fund_name': f'米国株式インデックスファンド{i+1}（為替ヘッジあり）',
            'management_company': f'運用会社{(i % 3) + 1}',
            'inception_date': (datetime(2020, 1, 1) - timedelta(days=np.random.randint(365, 3650))).strftime('%Y-%m-%d'),
            'share_class': 'A',
            'currency_hedge': 'あり',
            'benchmark': 'S&P500指数（円ヘッジベース）',
            'expense_ratio': round(np.random.uniform(0.1, 0.4), 2),
            'aum_latest': round(np.random.uniform(10000, 100000), 2),
            'fund_type': 'パッシブ',
            'is_index_fund': True,
            'investment_style': 'ブレンド',
            'is_theme_fund': False,
            'is_leveraged': False,
            'is_fund_of_funds': False,
            'status': '運用中',
            'redemption_date': '',
            'inclusion_reason': 'S&P500連動パッシブファンド、36か月以上のトラックレコードあり'
        })
    
    # すべてのファンドを結合
    all_funds = active_no_hedge + active_hedge + passive_no_hedge + passive_hedge
    
    return pd.DataFrame(all_funds)


def generate_monthly_returns(fund_attributes, base_date='2024-10-31', n_months=48):
    """
    月次リターンデータを生成する
    
    Parameters:
        fund_attributes (pd.DataFrame): ファンド属性データ
        base_date (str): 基準日（YYYY-MM-DD形式）
        n_months (int): 生成する月数
        
    Returns:
        pd.DataFrame: 月次リターンデータ
    """
    base_dt = datetime.strptime(base_date, '%Y-%m-%d')
    
    # 月末日付のリストを生成
    month_ends = []
    for i in range(n_months, 0, -1):
        # i か月前の月末を計算
        year = base_dt.year
        month = base_dt.month - i
        
        while month <= 0:
            month += 12
            year -= 1
        
        # その月の末日を取得
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        month_end = next_month - timedelta(days=1)
        month_ends.append(month_end.strftime('%Y-%m-%d'))
    
    # 各ファンドの月次リターンを生成
    all_returns = []
    
    for _, fund in fund_attributes.iterrows():
        fund_id = fund['fund_id']
        fund_type = fund['fund_type']
        currency_hedge = fund['currency_hedge']
        
        # ベースとなる市場リターンを生成（S&P500を想定）
        # 年率リターン: 約10%、ボラティリティ: 約15%
        market_monthly_mean = 0.10 / 12  # 月次平均リターン
        market_monthly_std = 0.15 / np.sqrt(12)  # 月次標準偏差
        
        market_returns = np.random.normal(market_monthly_mean, market_monthly_std, n_months)
        
        # 為替リターンを生成（ヘッジなしの場合のみ）
        if currency_hedge == 'なし':
            # USD/JPY の変動（年率ボラティリティ約10%）
            fx_monthly_std = 0.10 / np.sqrt(12)
            fx_returns = np.random.normal(0, fx_monthly_std, n_months)
        else:
            fx_returns = np.zeros(n_months)
        
        # ファンドタイプに応じてリターンを調整
        if fund_type == 'パッシブ':
            # パッシブ: 市場リターン - 信託報酬
            expense_ratio = fund['expense_ratio'] / 100
            monthly_expense = expense_ratio / 12
            fund_returns = market_returns + fx_returns - monthly_expense
            
            # トラッキングエラーを追加（年率0.1%程度）
            tracking_error = np.random.normal(0, 0.001 / np.sqrt(12), n_months)
            fund_returns += tracking_error
            
        else:  # アクティブ
            # アクティブ: 市場リターン + アルファ - 信託報酬
            expense_ratio = fund['expense_ratio'] / 100
            monthly_expense = expense_ratio / 12
            
            # アルファを生成（一部のファンドは正、一部は負）
            # 年率アルファの範囲: -2% ～ +3%
            annual_alpha = np.random.uniform(-0.02, 0.03)
            monthly_alpha = annual_alpha / 12
            
            # アクティブリスク（年率2%程度）
            active_risk = np.random.normal(0, 0.02 / np.sqrt(12), n_months)
            
            fund_returns = market_returns + fx_returns + monthly_alpha + active_risk - monthly_expense
        
        # 各月のデータを作成
        for i, month_end in enumerate(month_ends):
            all_returns.append({
                'fund_id': fund_id,
                'month_end_date': month_end,
                'monthly_return': round(fund_returns[i], 6),
                'nav': None,  # 基準価額は省略
                'aum': None   # 純資産総額は省略
            })
    
    return pd.DataFrame(all_returns)


def main():
    """
    メイン関数
    """
    print("=" * 60)
    print("サンプルデータ生成スクリプト")
    print("=" * 60)
    
    # データディレクトリの作成
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # ファンド属性データの生成
    print("\n1. ファンド属性データを生成中...")
    fund_attributes = generate_fund_attributes()
    
    output_path = os.path.join(data_dir, 'fund_attributes.csv')
    fund_attributes.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ {len(fund_attributes)}本のファンドデータを生成")
    print(f"   ✓ 保存先: {output_path}")
    
    # 統計情報の表示
    print("\n   [ファンド構成]")
    print(f"   - アクティブ（ヘッジなし）: {len(fund_attributes[(fund_attributes['fund_type'] == 'アクティブ') & (fund_attributes['currency_hedge'] == 'なし')])}本")
    print(f"   - アクティブ（ヘッジあり）: {len(fund_attributes[(fund_attributes['fund_type'] == 'アクティブ') & (fund_attributes['currency_hedge'] == 'あり')])}本")
    print(f"   - パッシブ（ヘッジなし）: {len(fund_attributes[(fund_attributes['fund_type'] == 'パッシブ') & (fund_attributes['currency_hedge'] == 'なし')])}本")
    print(f"   - パッシブ（ヘッジあり）: {len(fund_attributes[(fund_attributes['fund_type'] == 'パッシブ') & (fund_attributes['currency_hedge'] == 'あり')])}本")
    
    # 月次リターンデータの生成
    print("\n2. 月次リターンデータを生成中...")
    base_date = '2024-10-31'
    n_months = 48  # 48か月分（36か月 + 余裕）
    
    monthly_returns = generate_monthly_returns(fund_attributes, base_date, n_months)
    
    output_path = os.path.join(data_dir, 'monthly_returns.csv')
    monthly_returns.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"   ✓ {len(monthly_returns)}件の月次リターンデータを生成")
    print(f"   ✓ 期間: {monthly_returns['month_end_date'].min()} ～ {monthly_returns['month_end_date'].max()}")
    print(f"   ✓ 保存先: {output_path}")
    
    # データソース情報の記録
    print("\n3. データソース情報を記録中...")
    data_sources_path = os.path.join(data_dir, 'data_sources.txt')
    with open(data_sources_path, 'w', encoding='utf-8') as f:
        f.write("データソース情報\n")
        f.write("=" * 60 + "\n\n")
        f.write("データタイプ: サンプルデータ（シミュレーション）\n")
        f.write(f"生成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"基準日: {base_date}\n")
        f.write(f"ファンド数: {len(fund_attributes)}本\n")
        f.write(f"データ期間: {n_months}か月\n\n")
        f.write("注意事項:\n")
        f.write("- このデータは分析フレームワークの動作確認用のサンプルデータです\n")
        f.write("- 実際のファンドパフォーマンスに基づいたリアリスティックな値を生成していますが、\n")
        f.write("  実在するファンドのデータではありません\n")
        f.write("- 本番分析には、実際のファンドデータを使用してください\n")
    
    print(f"   ✓ 保存先: {data_sources_path}")
    
    # 完了メッセージ
    print("\n" + "=" * 60)
    print("サンプルデータの生成が完了しました！")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. データを確認: data/fund_attributes.csv, data/monthly_returns.csv")
    print("2. メイン分析を実行: python3 scripts/fund_performance_analysis.py")
    print("3. ロバストネス分析を実行: python3 scripts/robustness_analysis.py")
    print("4. 可視化を実行: python3 scripts/visualization.py")
    print()


if __name__ == "__main__":
    main()
