from flask import request
from flask_restful import Resource
import numpy as np
from flask import current_app
import pandas as pd

from api.reports.data import get_country_mapping
from commons import parser


class WorldMapDataResource(Resource):
    """
    世界地圖遊客流量數據 API - 顯示各國指定年份的總入境遊客數
    """

    def get(self):
        # 載入原始數據
        path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_arrivals_by_region_10_2025.csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {
                'error': f'無法讀取數據檔案: {str(e)}'
            }, 500

        print("=" * 60)
        print("DEBUG: WorldMapDataResource")
        print(f"原始數據行數: {len(df)}")

        # 篩選條件
        year = parser.parse(request.args.get('year'), cast=int, default=2023)
        print(f"\n請求年份: {year}")

        # 只取指定年份的數據
        df_year = df[df['year'] == year].copy()
        print(f"\n{year} 年的總數據行數: {len(df_year)}")

        if len(df_year) == 0:
            available_years = sorted(df['year'].unique().tolist())
            return {
                'year': year,
                'metric': 'tourist_count',
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0, 'total_tourists': 0, 'avg_tourists': 0, 'max_country': None, 'max_value': 0},
                'debug': {'message': f'No data for year {year}', 'available_years': available_years}
            }

        print(f"\n{year} 年的 indicator_code 分布:")
        print(df_year['indicator_code'].value_counts())

        # ========== 關鍵：選擇優先級最高的單一指標 ==========

        # 指標優先級（從高到低）
        indicator_priority = [
            'INBD_TRIP_AREA_TOTL_TOUR',  # 1. 總入境遊客（最優先）
            'INBD_TRIP_AREA_TOUR_ABRD',  # 2. 入境遊客（按地區）
            'INBD_TRIP_REGN_TOUR',       # 3. 區域入境遊客
        ]

        selected_indicator = None
        df_filtered = pd.DataFrame()

        # 按優先級選擇第一個存在的指標
        for indicator in indicator_priority:
            temp_df = df_year[
                (df_year['indicator_code'] == indicator) &
                (df_year['partner_area_label'] == 'World')
                ]

            if len(temp_df) > 0:
                selected_indicator = indicator
                df_filtered = temp_df.copy()
                print(f"\n✅ 使用指標: {indicator}")
                print(f"   符合條件的數據行數: {len(df_filtered)}")
                break

        # 如果沒有 'World' 數據，嘗試不限制 partner
        if df_filtered.empty:
            print("\n⚠️  沒有 'World' 數據，嘗試其他 partner")
            for indicator in indicator_priority:
                temp_df = df_year[df_year['indicator_code'] == indicator]

                if len(temp_df) > 0:
                    selected_indicator = indicator
                    # 按國家分組，取最大值（避免重複）
                    df_filtered = temp_df.groupby('reporter_area_label', as_index=False).agg({
                        'value': 'max'  # 取最大值
                    })
                    df_filtered['indicator_code'] = indicator
                    print(f"\n✅ 使用指標: {indicator} (無 World 限制)")
                    print(f"   分組後的國家數: {len(df_filtered)}")
                    break

        if df_filtered.empty:
            print("\n❌ 沒有可用的遊客數據")
            available_indicators = df_year['indicator_code'].unique().tolist()
            return {
                'year': year,
                'metric': 'tourist_count',
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0, 'total_tourists': 0, 'avg_tourists': 0, 'max_country': None, 'max_value': 0},
                'debug': {
                    'message': 'No suitable indicator found',
                    'available_indicators': available_indicators,
                    'tried_indicators': indicator_priority
                }
            }

        print(f"\n篩選後的數據樣本:")
        print(df_filtered[['reporter_area_label', 'indicator_code', 'value']].head(10))

        # 轉換數值（千人 -> 人）
        df_filtered['value'] = pd.to_numeric(df_filtered['value'], errors='coerce') * 1000

        # 移除 NaN
        df_filtered = df_filtered.dropna(subset=['value'])

        print(f"\n轉換數值後: {len(df_filtered)} 行")

        # ========== 關鍵：確保每個國家只有一條記錄 ==========

        # 如果同一個國家有多條記錄，只取第一條（或最大值）
        df_grouped = df_filtered.groupby('reporter_area_label', as_index=False).agg({
            'value': 'first'  # 只取第一個值（因為已經是 World 的總數）
        })

        print(f"\n去重後的國家數: {len(df_grouped)}")
        print(f"\n數值統計:")
        print(df_grouped['value'].describe())
        print(f"\n數值範圍: {df_grouped['value'].min():,.0f} ~ {df_grouped['value'].max():,.0f}")

        # 獲取國家映射
        country_mapping = get_country_mapping()

        # 添加 ISO-3 代碼
        df_grouped['iso3'] = df_grouped['reporter_area_label'].map(country_mapping)

        print(f"\n映射前: {len(df_grouped)} 個國家")
        print(f"映射後: {df_grouped['iso3'].notna().sum()} 個國家有 ISO 代碼")

        # 顯示未映射的國家（前 10 個）
        unmapped = df_grouped[df_grouped['iso3'].isna()]['reporter_area_label'].tolist()
        if len(unmapped) > 0:
            print(f"\n⚠️ 未映射的國家 ({len(unmapped)} 個):")
            for country in unmapped[:10]:
                print(f"  - {country}")

        # 移除沒有 ISO 代碼的國家
        df_final = df_grouped.dropna(subset=['iso3']).copy()

        # 移除異常值（0 或負數）
        df_final = df_final[df_final['value'] > 0]

        print(f"\n✅ 最終國家數: {len(df_final)}")

        # 排序
        df_final = df_final.sort_values('value', ascending=False)

        if len(df_final) > 0:
            print(f"\n🏆 Top 10 國家:")
            top10 = df_final.head(10)
            for idx, row in top10.iterrows():
                tourists = int(row['value'])
                print(f"  {row['iso3']:3s} | {row['reporter_area_label']:40s} | {tourists:15,} 人")

        print("=" * 60)

        # 轉換為前端格式
        map_data = {
            'countries': [str(x) for x in df_final['iso3'].tolist()],
            'country_names': [str(x) for x in df_final['reporter_area_label'].tolist()],
            'values': [float(x) for x in df_final['value'].tolist()]
        }

        # 統計資訊
        if len(df_final) > 0:
            total_tourists = float(df_final['value'].sum())
            avg_tourists = float(df_final['value'].mean())
            max_value = float(df_final['value'].max())
            max_country = str(df_final.iloc[0]['reporter_area_label'])
        else:
            total_tourists = avg_tourists = max_value = 0
            max_country = None

        stats = {
            'total_countries': int(len(df_final)),
            'total_tourists': int(total_tourists),
            'avg_tourists': int(avg_tourists),
            'max_country': max_country,
            'max_value': int(max_value),
            'indicator_used': selected_indicator
        }

        return {
            'year': int(year),
            'metric': 'tourist_count',
            'data': map_data,
            'stats': stats
        }