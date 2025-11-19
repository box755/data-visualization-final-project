from flask import request
from flask_restful import Resource
from flask import current_app
import pandas as pd
import re

from commons import parser


class JapanMonthlyVisitorsResource(Resource):
    """
    日本每月遊客數量 API
    返回指定年份的每月遊客數據
    """

    def get(self):
        # 載入日本月度數據
        path = current_app.config['BASE_DIR'] / 'data/country_data/JTM_inbound_20251106eng(JAPAN).csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {'error': f'無法讀取數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print("DEBUG: JapanMonthlyVisitorsResource")
        print(f"原始數據行數: {len(df)}")
        print(f"列名: {df.columns.tolist()}")
        print(f"前 10 行:\n{df.head(10)}")

        # 解析 Monthly 列
        def parse_monthly(monthly_str):
            """
            解析各種格式：
            - '1997　Jan．' (年份+月份在同一格)
            - 'Feb．' (只有月份，沿用前一年)
            """
            monthly_str = str(monthly_str).strip()

            # 格式 1: 年份 + 月份 (如 "1997　Jan．")
            match_year_month = re.search(r'(\d{4}).*?([A-Za-z]{3})', monthly_str)
            if match_year_month:
                year = int(match_year_month.group(1))
                month = match_year_month.group(2)
                return year, month

            # 格式 2: 只有月份 (如 "Feb．")
            match_month = re.search(r'([A-Za-z]{3})', monthly_str)
            if match_month:
                month = match_month.group(1)
                return None, month  # 年份稍後填充

            return None, None

        # 第一次解析：提取年份和月份
        df[['Year', 'Month']] = df['Monthly '].apply(
            lambda x: pd.Series(parse_monthly(x))
        )

        # 填充缺失的年份（使用前一行的年份）
        df['Year'] = df['Year'].fillna(method='ffill')

        # 移除解析失敗的行
        df = df.dropna(subset=['Year', 'Month'])
        df['Year'] = df['Year'].astype(int)

        print(f"\n解析後數據:")
        print(df[['Monthly ', 'Year', 'Month', 'Grand Total']].head(15))
        print(f"年份範圍: {df['Year'].min()} - {df['Year'].max()}")
        print(f"可用年份: {sorted(df['Year'].unique().tolist())}")

        # 獲取請求參數
        year = parser.parse(request.args.get('year'), cast=int, default=None)

        # 如果指定年份，只返回該年份數據
        if year:
            df_filtered = df[df['Year'] == year].copy()
            print(f"\n篩選年份 {year}: {len(df_filtered)} 行")

            if len(df_filtered) == 0:
                available_years = sorted(df['Year'].unique().tolist())
                return {
                    'year': year,
                    'data': {'months': [], 'values': [], 'changes': []},
                    'stats': {'total_visitors': 0, 'avg_visitors': 0},
                    'debug': {
                        'message': f'No data for year {year}',
                        'available_years': available_years
                    }
                }, 404
        else:
            # 如果沒有指定年份，返回最新一年的數據
            latest_year = int(df['Year'].max())
            df_filtered = df[df['Year'] == latest_year].copy()
            year = latest_year
            print(f"\n未指定年份，返回最新年份 {year}: {len(df_filtered)} 行")

        # 清理數據：移除逗號和引號，轉換為數字
        df_filtered['Grand Total'] = df_filtered['Grand Total'].astype(str).str.replace('"', '').str.replace(',', '').str.strip()
        df_filtered['Grand Total'] = pd.to_numeric(df_filtered['Grand Total'], errors='coerce')

        # 處理變化率（移除百分號並轉換為數字）
        if '%Change' in df_filtered.columns:
            df_filtered['Change'] = df_filtered['%Change'].astype(str).str.rstrip('%').str.strip()
            df_filtered['Change'] = df_filtered['Change'].replace(['', 'nan'], None)
            df_filtered['Change'] = pd.to_numeric(df_filtered['Change'], errors='coerce')
        else:
            df_filtered['Change'] = None

        # 標準化月份名稱（移除句點）
        df_filtered['Month'] = df_filtered['Month'].str.replace('.', '').str.replace('．', '').str.strip()

        # 確保按月份排序
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df_filtered['MonthNum'] = df_filtered['Month'].map({m: i+1 for i, m in enumerate(month_order)})

        # 移除無法識別的月份
        df_filtered = df_filtered.dropna(subset=['MonthNum'])
        df_filtered = df_filtered.sort_values('MonthNum')

        print(f"\n處理後數據:")
        print(df_filtered[['Month', 'MonthNum', 'Grand Total', 'Change']].to_string())

        # 移除 NaN 的數據
        df_filtered = df_filtered.dropna(subset=['Grand Total'])

        if len(df_filtered) == 0:
            return {
                'year': year,
                'data': {'months': [], 'values': [], 'changes': []},
                'stats': {'total_visitors': 0, 'avg_visitors': 0},
                'debug': {
                    'message': f'No valid data for year {year}'
                }
            }, 404

        # 計算統計數據
        total_visitors = int(df_filtered['Grand Total'].sum())
        avg_visitors = int(df_filtered['Grand Total'].mean())
        max_month = df_filtered.loc[df_filtered['Grand Total'].idxmax()]
        min_month = df_filtered.loc[df_filtered['Grand Total'].idxmin()]

        # 準備返回數據
        data = {
            'months': df_filtered['Month'].tolist(),
            'month_numbers': df_filtered['MonthNum'].astype(int).tolist(),
            'values': df_filtered['Grand Total'].astype(int).tolist(),
            'changes': df_filtered['Change'].fillna(0).round(1).tolist()
        }

        stats = {
            'year': int(year),
            'total_visitors': total_visitors,
            'avg_visitors': avg_visitors,
            'max_month': {
                'month': str(max_month['Month']),
                'month_number': int(max_month['MonthNum']),
                'value': int(max_month['Grand Total'])
            },
            'min_month': {
                'month': str(min_month['Month']),
                'month_number': int(min_month['MonthNum']),
                'value': int(min_month['Grand Total'])
            },
            'available_years': sorted(df['Year'].unique().astype(int).tolist())
        }

        print(f"\n✅ {year} 年統計:")
        print(f"  總遊客數: {total_visitors:,}")
        print(f"  平均每月: {avg_visitors:,}")
        print(f"  最高月份: {max_month['Month']} ({max_month['Grand Total']:,.0f})")
        print(f"  最低月份: {min_month['Month']} ({min_month['Grand Total']:,.0f})")
        print("=" * 60)

        return {
            'country': 'Japan',
            'country_code': 'JPN',
            'year': year,
            'data': data,
            'stats': stats
        }