from flask import request
from flask_restful import Resource
import numpy as np
from flask import current_app
import pandas as pd

from api.reports.data import get_country_mapping
from commons import parser


class WorldMapAvgSpendingResource(Resource):
    """
    世界地圖平均每人次消費數據 API
    計算公式：總消費額 ÷ 遊客人次
    """

    def get(self):
        # 載入兩個數據檔案
        tourist_path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_arrivals_by_region_10_2025.csv'
        expenditure_path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_expenditure_10_2025.csv'

        try:
            df_tourist = pd.read_csv(tourist_path)
            df_expenditure = pd.read_csv(expenditure_path)
        except Exception as e:
            return {'error': f'無法讀取數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print("DEBUG: WorldMapAvgSpendingResource")

        # 篩選條件
        year = parser.parse(request.args.get('year'), cast=int, default=2019)
        print(f"\n請求年份: {year}")

        # ========== 1. 處理遊客人次數據 ==========

        df_tourist_year = df_tourist[df_tourist['year'] == year].copy()
        print(f"\n遊客數據（{year}年）: {len(df_tourist_year)} 行")

        # 遊客指標優先級
        tourist_indicators = [
            'INBD_TRIP_AREA_TOTL_TOUR',
            'INBD_TRIP_AREA_TOUR_ABRD',
            'INBD_TRIP_REGN_TOUR',
        ]

        df_tourist_world = df_tourist_year[df_tourist_year['partner_area_label'] == 'World'].copy()
        df_tourist_filtered = df_tourist_world[df_tourist_world['indicator_code'].isin(tourist_indicators)].copy()

        if df_tourist_filtered.empty:
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'message': 'No tourist data available'}
            }

        # 轉換數值（千人）
        df_tourist_filtered['tourist_count'] = pd.to_numeric(df_tourist_filtered['value'], errors='coerce')
        df_tourist_filtered = df_tourist_filtered.dropna(subset=['tourist_count'])

        # 每個國家選擇優先級最高的指標
        tourist_priority = {
            'INBD_TRIP_AREA_TOTL_TOUR': 1,
            'INBD_TRIP_AREA_TOUR_ABRD': 2,
            'INBD_TRIP_REGN_TOUR': 3,
        }
        df_tourist_filtered['priority'] = df_tourist_filtered['indicator_code'].map(tourist_priority)
        df_tourist_filtered = df_tourist_filtered.sort_values(['reporter_area_label', 'priority'])
        df_tourists = df_tourist_filtered.groupby('reporter_area_label', as_index=False).first()
        df_tourists = df_tourists[['reporter_area_label', 'tourist_count']]

        print(f"遊客數據處理後: {len(df_tourists)} 個國家")

        # ========== 2. 處理消費數據 ==========

        df_expenditure_year = df_expenditure[df_expenditure['year'] == year].copy()
        print(f"消費數據（{year}年）: {len(df_expenditure_year)} 行")

        # 消費指標優先級
        expenditure_indicators = [
            'INBD_EXPD_BPAY_TOTL_VSTR',
            'INBD_EXPD_BPAY_TRVL_VSTR',
            'INBD_EXPD_BPAY_PSTR_VSTR',
        ]

        df_expd_world = df_expenditure_year[df_expenditure_year['partner_area_label'] == 'World'].copy()
        df_expd_filtered = df_expd_world[df_expd_world['indicator_code'].isin(expenditure_indicators)].copy()

        if df_expd_filtered.empty:
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'message': 'No expenditure data available'}
            }

        # 轉換數值（百萬美元）
        df_expd_filtered['expenditure'] = pd.to_numeric(df_expd_filtered['value'], errors='coerce')
        df_expd_filtered = df_expd_filtered.dropna(subset=['expenditure'])

        # 每個國家選擇優先級最高的指標
        expd_priority = {
            'INBD_EXPD_BPAY_TOTL_VSTR': 1,
            'INBD_EXPD_BPAY_TRVL_VSTR': 2,
            'INBD_EXPD_BPAY_PSTR_VSTR': 3,
        }
        df_expd_filtered['priority'] = df_expd_filtered['indicator_code'].map(expd_priority)
        df_expd_filtered = df_expd_filtered.sort_values(['reporter_area_label', 'priority'])
        df_expenditures = df_expd_filtered.groupby('reporter_area_label', as_index=False).first()
        df_expenditures = df_expenditures[['reporter_area_label', 'expenditure']]

        print(f"消費數據處理後: {len(df_expenditures)} 個國家")

        # ========== 3. 合併數據並計算平均消費 ==========

        df_merged = pd.merge(
            df_tourists,
            df_expenditures,
            on='reporter_area_label',
            how='inner'
        )

        print(f"\n合併後有完整數據的國家: {len(df_merged)} 個")

        if df_merged.empty:
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'message': 'No countries with both tourist and expenditure data'}
            }

        # 計算平均每人次消費
        # 公式：(消費額百萬美元 × 1,000,000) ÷ (遊客千人 × 1,000) = 消費額 ÷ 遊客千人 × 1,000
        df_merged['avg_spending'] = (df_merged['expenditure'] / df_merged['tourist_count']) * 1000

        print(f"\n平均消費統計:")
        print(df_merged['avg_spending'].describe())

        # 移除異常值（例如：消費過高或過低）
        df_merged = df_merged[df_merged['avg_spending'] > 0]
        df_merged = df_merged[df_merged['avg_spending'] < 100000]  # 移除超過 10 萬美元的異常值

        print(f"移除異常值後: {len(df_merged)} 個國家")

        # ISO 映射
        country_mapping = get_country_mapping()
        df_merged['iso3'] = df_merged['reporter_area_label'].map(country_mapping)

        # 移除未映射的國家
        unmapped = df_merged[df_merged['iso3'].isna()]['reporter_area_label'].tolist()
        if unmapped:
            print(f"\n⚠️ 未映射的國家 ({len(unmapped)} 個): {unmapped[:5]}")

        df_final = df_merged.dropna(subset=['iso3']).copy()
        df_final = df_final.sort_values('avg_spending', ascending=False)

        print(f"\n✅ 最終有效國家數: {len(df_final)}")

        # 🔍 檢查中國
        china_data = df_final[df_final['iso3'] == 'CHN']
        if len(china_data) > 0:
            rank = list(df_final['iso3']).index('CHN') + 1
            print(f"\n✅ 中國數據:")
            print(f"   排名: 第 {rank} 名")
            print(f"   遊客: {china_data.iloc[0]['tourist_count']:,.0f} 千人")
            print(f"   消費: ${china_data.iloc[0]['expenditure']:,.0f}M")
            print(f"   平均: ${china_data.iloc[0]['avg_spending']:,.2f} / 人次")

        if len(df_final) > 0:
            print(f"\n🏆 Top 10 平均消費國家:")
            for i, (idx, row) in enumerate(df_final.head(10).iterrows(), 1):
                print(f"  {i:2d}. {row['iso3']:3s} | {row['reporter_area_label']:40s} | ${row['avg_spending']:,.2f} / 人次")

        print("=" * 60)

        # 返回數據
        map_data = {
            'countries': [str(x) for x in df_final['iso3'].tolist()],
            'country_names': [str(x) for x in df_final['reporter_area_label'].tolist()],
            'values': [float(x) for x in df_final['avg_spending'].tolist()]
        }

        stats = {
            'total_countries': int(len(df_final)),
            'avg_spending_mean': float(df_final['avg_spending'].mean()),
            'avg_spending_median': float(df_final['avg_spending'].median()),
            'max_country': str(df_final.iloc[0]['reporter_area_label']) if len(df_final) > 0 else None,
            'max_value': float(df_final.iloc[0]['avg_spending']) if len(df_final) > 0 else 0
        }

        return {
            'year': int(year),
            'data': map_data,
            'stats': stats
        }