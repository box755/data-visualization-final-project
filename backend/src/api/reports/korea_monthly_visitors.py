from flask import request
from flask_restful import Resource
from flask import current_app
import pandas as pd

from commons import parser


class KoreaMonthlyVisitorsResource(Resource):
    """
    韓國每月遊客數量 API
    返回指定年份的每月遊客數據（按國家聚合）
    """

    def get(self):
        # 載入韓國月度數據
        path = current_app.config['BASE_DIR'] / 'data/country_data/Enter_korea_by_age(KOREA).csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {'error': f'無法讀取數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print("DEBUG: KoreaMonthlyVisitorsResource")
        print(f"原始數據行數: {len(df)}")
        print(f"列名: {df.columns.tolist()}")
        print(f"前 5 行:\n{df.head()}")

        # 解析 date 列（格式：YYYY-M）
        df[['Year', 'Month']] = df['date'].str.split('-', expand=True)
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Month'] = pd.to_numeric(df['Month'], errors='coerce')

        # 移除解析失敗的行
        df = df.dropna(subset=['Year', 'Month', 'visitor'])
        df['Year'] = df['Year'].astype(int)
        df['Month'] = df['Month'].astype(int)
        df['visitor'] = pd.to_numeric(df['visitor'], errors='coerce')

        print(f"\n解析後數據行數: {len(df)}")
        print(f"年份範圍: {df['Year'].min()} - {df['Year'].max()}")
        print(f"唯一國家數: {df['nation'].nunique()}")

        # 獲取請求參數
        year = parser.parse(request.args.get('year'), cast=int, default=None)

        # 如果指定年份，只返回該年份數據
        if year:
            df_year = df[df['Year'] == year].copy()
            print(f"\n篩選年份 {year}: {len(df_year)} 行")

            if len(df_year) == 0:
                available_years = sorted(df['Year'].unique().tolist())
                return {
                    'year': year,
                    'data': {'months': [], 'values': []},
                    'stats': {'total_visitors': 0, 'avg_visitors': 0},
                    'debug': {
                        'message': f'No data for year {year}',
                        'available_years': available_years
                    }
                }, 404
        else:
            # 如果沒有指定年份，返回最新一年的數據
            latest_year = int(df['Year'].max())
            df_year = df[df['Year'] == latest_year].copy()
            year = latest_year
            print(f"\n未指定年份，返回最新年份 {year}: {len(df_year)} 行")

        # ⭐ 關鍵：按月份聚合所有國家的遊客數
        df_monthly = df_year.groupby('Month').agg({
            'visitor': 'sum'
        }).reset_index()

        print(f"\n按月聚合後:")
        print(df_monthly)

        # 創建月份名稱映射
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        df_monthly['MonthName'] = df_monthly['Month'].map(month_names)

        # 按月份排序
        df_monthly = df_monthly.sort_values('Month')

        if len(df_monthly) == 0:
            return {
                'year': year,
                'data': {'months': [], 'values': []},
                'stats': {'total_visitors': 0, 'avg_visitors': 0},
                'debug': {
                    'message': f'No valid data for year {year}'
                }
            }, 404

        # 計算統計數據
        total_visitors = int(df_monthly['visitor'].sum())
        avg_visitors = int(df_monthly['visitor'].mean())
        max_month = df_monthly.loc[df_monthly['visitor'].idxmax()]
        min_month = df_monthly.loc[df_monthly['visitor'].idxmin()]

        # 計算同比增長率（如果有前一年數據）
        changes = []
        if year > df['Year'].min():
            df_prev_year = df[df['Year'] == (year - 1)].copy()
            if len(df_prev_year) > 0:
                df_prev_monthly = df_prev_year.groupby('Month').agg({
                    'visitor': 'sum'
                }).reset_index()

                for _, row in df_monthly.iterrows():
                    month = row['Month']
                    current_value = row['visitor']

                    prev_row = df_prev_monthly[df_prev_monthly['Month'] == month]
                    if not prev_row.empty:
                        prev_value = prev_row.iloc[0]['visitor']
                        change = ((current_value - prev_value) / prev_value * 100) if prev_value > 0 else 0
                        changes.append(round(change, 1))
                    else:
                        changes.append(0)
            else:
                changes = [0] * len(df_monthly)
        else:
            changes = [0] * len(df_monthly)

        # 準備返回數據
        data = {
            'months': df_monthly['MonthName'].tolist(),
            'month_numbers': df_monthly['Month'].tolist(),
            'values': df_monthly['visitor'].astype(int).tolist(),
            'changes': changes
        }

        stats = {
            'year': int(year),
            'total_visitors': total_visitors,
            'avg_visitors': avg_visitors,
            'max_month': {
                'month': str(max_month['MonthName']),
                'month_number': int(max_month['Month']),
                'value': int(max_month['visitor'])
            },
            'min_month': {
                'month': str(min_month['MonthName']),
                'month_number': int(min_month['Month']),
                'value': int(min_month['visitor'])
            },
            'available_years': sorted(df['Year'].unique().astype(int).tolist())
        }

        print(f"\n✅ {year} 年統計:")
        print(f"  總遊客數: {total_visitors:,}")
        print(f"  平均每月: {avg_visitors:,}")
        print(f"  最高月份: {max_month['MonthName']} ({max_month['visitor']:,.0f})")
        print(f"  最低月份: {min_month['MonthName']} ({min_month['visitor']:,.0f})")
        print("=" * 60)

        return {
            'country': 'South Korea',
            'country_code': 'KOR',
            'year': year,
            'data': data,
            'stats': stats
        }