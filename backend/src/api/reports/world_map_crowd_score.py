from flask import request
from flask_restful import Resource
import numpy as np
from flask import current_app
import pandas as pd

from api.reports.data import get_country_mapping
from commons import parser


class WorldMapCrowdScoreResource(Resource):
    """
    世界地圖旅遊擁擠程度 API
    計算公式：擁擠度分數 = 該國旅客量 / 全球最大旅客量 × 100
    """

    def get(self):
        # 載入遊客數據
        path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_arrivals_by_region_10_2025.csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {'error': f'無法讀取數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print("DEBUG: WorldMapCrowdScoreResource")
        print(f"原始數據行數: {len(df)}")

        # 篩選條件
        year = parser.parse(request.args.get('year'), cast=int, default=2019)
        print(f"\n請求年份: {year}")

        # 只取指定年份
        df_year = df[df['year'] == year].copy()
        print(f"\n{year} 年的總數據行數: {len(df_year)}")

        if len(df_year) == 0:
            available_years = sorted(df['year'].unique().tolist())
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'available_years': available_years}
            }

        print(f"\n所有 indicator_code:")
        print(df_year['indicator_code'].value_counts())

        # ========== 處理遊客人次數據 ==========

        # 遊客指標優先級
        tourist_indicators = [
            'INBD_TRIP_AREA_TOTL_TOUR',
            'INBD_TRIP_AREA_TOUR_ABRD',
            'INBD_TRIP_REGN_TOUR',
        ]

        # 只看 World 數據
        df_world = df_year[df_year['partner_area_label'] == 'World'].copy()
        df_filtered = df_world[df_world['indicator_code'].isin(tourist_indicators)].copy()

        if df_filtered.empty:
            print("\n❌ 沒有可用的遊客數據")
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'message': 'No tourist data available'}
            }

        # 轉換數值（千人 -> 人）
        df_filtered['tourist_count'] = pd.to_numeric(df_filtered['value'], errors='coerce') * 1000
        df_filtered = df_filtered.dropna(subset=['tourist_count'])

        print(f"\n轉換數值後: {len(df_filtered)} 行")

        # 每個國家選擇優先級最高的指標
        tourist_priority = {
            'INBD_TRIP_AREA_TOTL_TOUR': 1,
            'INBD_TRIP_AREA_TOUR_ABRD': 2,
            'INBD_TRIP_REGN_TOUR': 3,
        }
        df_filtered['priority'] = df_filtered['indicator_code'].map(tourist_priority)
        df_filtered = df_filtered.sort_values(['reporter_area_label', 'priority'])
        df_tourists = df_filtered.groupby('reporter_area_label', as_index=False).first()

        print(f"\n去重後: {len(df_tourists)} 個國家")

        max_tourists = df_tourists['tourist_count'].max()
        min_tourists = df_tourists['tourist_count'].min()

        print(f"\n全球旅客量範圍:")
        print(f"  最大: {max_tourists:,.0f} 人")
        print(f"  最小: {min_tourists:,.0f} 人")

        max_country = df_tourists[df_tourists['tourist_count'] == max_tourists].iloc[0]
        min_country = df_tourists[df_tourists['tourist_count'] == min_tourists].iloc[0]

        print(f"\n最擁擠國家: {max_country['reporter_area_label']} ({max_tourists:,.0f} 人)")
        print(f"最少遊客國家: {min_country['reporter_area_label']} ({min_tourists:,.0f} 人)")

        # 使用 Min-Max Normalization 計算擁擠度分數（0-100）
        # Formula: (X - X_min) / (X_max - X_min) × 100
        df_tourists['crowd_score'] = ((df_tourists['tourist_count'] - min_tourists) /
                                      (max_tourists - min_tourists)) * 100

        print(f"\n擁擠度分數統計:")
        print(df_tourists['crowd_score'].describe())

        # 移除異常值
        df_tourists = df_tourists[df_tourists['crowd_score'] > 0]

        # ISO 映射
        country_mapping = get_country_mapping()
        df_tourists['iso3'] = df_tourists['reporter_area_label'].map(country_mapping)

        # 移除未映射的國家
        unmapped = df_tourists[df_tourists['iso3'].isna()]['reporter_area_label'].tolist()
        if unmapped:
            print(f"\n⚠️ 未映射的國家 ({len(unmapped)} 個): {unmapped[:5]}")

        df_final = df_tourists.dropna(subset=['iso3']).copy()
        df_final = df_final.sort_values('crowd_score', ascending=False)

        print(f"\n✅ 最終有效國家數: {len(df_final)}")

        # 🔍 檢查中國
        china_data = df_final[df_final['iso3'] == 'CHN']
        if len(china_data) > 0:
            rank = list(df_final['iso3']).index('CHN') + 1
            print(f"\n✅ 中國數據:")
            print(f"   排名: 第 {rank} 名")
            print(f"   遊客: {china_data.iloc[0]['tourist_count']:,.0f} 人")
            print(f"   擁擠度: {china_data.iloc[0]['crowd_score']:.2f} / 100")

        if len(df_final) > 0:
            print(f"\n🏆 Top 10 最擁擠國家:")
            for i, (idx, row) in enumerate(df_final.head(10).iterrows(), 1):
                print(f"  {i:2d}. {row['iso3']:3s} | {row['reporter_area_label']:40s} | "
                      f"{row['crowd_score']:5.2f} / 100 ({row['tourist_count']:,.0f} 人)")

        print("=" * 60)

        # 返回數據
        map_data = {
            'countries': [str(x) for x in df_final['iso3'].tolist()],
            'country_names': [str(x) for x in df_final['reporter_area_label'].tolist()],
            'values': [float(x) for x in df_final['crowd_score'].tolist()],
            'tourist_counts': [float(x) for x in df_final['tourist_count'].tolist()]
        }

        stats = {
            'total_countries': int(len(df_final)),
            'max_country': str(df_final.iloc[0]['reporter_area_label']) if len(df_final) > 0 else None,
            'max_tourists': int(df_final.iloc[0]['tourist_count']) if len(df_final) > 0 else 0,
            'max_crowd_score': float(df_final.iloc[0]['crowd_score']) if len(df_final) > 0 else 0,
            'avg_crowd_score': float(df_final['crowd_score'].mean()),
            'median_crowd_score': float(df_final['crowd_score'].median())
        }

        return {
            'year': int(year),
            'data': map_data,
            'stats': stats
        }