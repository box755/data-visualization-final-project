from flask import request
from flask_restful import Resource
import numpy as np
from flask import current_app
import pandas as pd

from api.reports.data import get_country_mapping
from commons import parser


class WorldMapExpenditureResource(Resource):
    """
    世界地圖遊客消費數據 API
    """

    def get(self):
        # 載入消費數據
        path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_expenditure_10_2025.csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {'error': f'無法讀取消費數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print("DEBUG: WorldMapExpenditureResource")
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
                'stats': {'total_countries': 0, 'total_expenditure': 0},
                'debug': {'available_years': available_years}
            }

        print(f"\n所有 indicator_code:")
        print(df_year['indicator_code'].value_counts())

        # ========== 新策略：合併多個消費指標 ==========

        # 消費相關指標（按優先級）
        expenditure_indicators = [
            'INBD_EXPD_BPAY_TOTL_VSTR',  # 總消費
            'INBD_EXPD_BPAY_TRVL_VSTR',  # 旅遊消費 ✅ 中國用這個
            'INBD_EXPD_BPAY_PSTR_VSTR',  # 客運交通消費
        ]

        # 只篩選 World 數據
        df_world = df_year[df_year['partner_area_label'] == 'World'].copy()
        print(f"\n只看 'World' 數據: {len(df_world)} 行")

        # 篩選所有消費相關的指標
        df_expenditure = df_world[df_world['indicator_code'].isin(expenditure_indicators)].copy()
        print(f"消費相關指標的數據: {len(df_expenditure)} 行")

        if df_expenditure.empty:
            print("\n❌ 沒有可用的消費數據")
            return {
                'year': year,
                'data': {'countries': [], 'country_names': [], 'values': []},
                'stats': {'total_countries': 0},
                'debug': {'available_indicators': df_year['indicator_code'].unique().tolist()}
            }

        # 轉換數值
        df_expenditure['value'] = pd.to_numeric(df_expenditure['value'], errors='coerce')
        df_expenditure = df_expenditure.dropna(subset=['value'])

        print(f"\n轉換數值後: {len(df_expenditure)} 行")

        # ========== 關鍵：每個國家選擇優先級最高的指標 ==========

        # 為每個指標添加優先級
        indicator_priority = {
            'INBD_EXPD_BPAY_TOTL_VSTR': 1,  # 最優先
            'INBD_EXPD_BPAY_TRVL_VSTR': 2,
            'INBD_EXPD_BPAY_PSTR_VSTR': 3,
        }

        df_expenditure['priority'] = df_expenditure['indicator_code'].map(indicator_priority)

        # 按國家和優先級排序，每個國家只保留優先級最高的指標
        df_expenditure = df_expenditure.sort_values(['reporter_area_label', 'priority'])
        df_grouped = df_expenditure.groupby('reporter_area_label', as_index=False).first()

        print(f"\n每個國家選擇最優指標後: {len(df_grouped)} 個國家")

        # 🔍 檢查使用的指標分布
        print(f"\n使用的指標分布:")
        print(df_grouped['indicator_code'].value_counts())

        # 🔍 檢查中國
        china_data = df_grouped[df_grouped['reporter_area_label'] == 'China']
        if len(china_data) > 0:
            print(f"\n✅ 中國數據:")
            print(f"   使用指標: {china_data.iloc[0]['indicator_code']}")
            print(f"   消費額: ${china_data.iloc[0]['value']:,.0f}M")
        else:
            print("\n❌ 沒有中國數據")

        # ISO 映射
        country_mapping = get_country_mapping()
        df_grouped['iso3'] = df_grouped['reporter_area_label'].map(country_mapping)

        # 移除未映射的國家
        unmapped = df_grouped[df_grouped['iso3'].isna()]['reporter_area_label'].tolist()
        if unmapped:
            print(f"\n⚠️ 未映射的國家 ({len(unmapped)} 個):")
            for i, country in enumerate(unmapped[:10], 1):
                print(f"  {i}. {country}")

        df_final = df_grouped.dropna(subset=['iso3']).copy()
        df_final = df_final[df_final['value'] > 0]
        df_final = df_final.sort_values('value', ascending=False)

        print(f"\n✅ 最終有效國家數: {len(df_final)}")

        # 🔍 最終檢查中國
        china_final = df_final[df_final['iso3'] == 'CHN']
        if len(china_final) > 0:
            rank = list(df_final['iso3']).index('CHN') + 1
            print(f"\n✅✅✅ 中國在最終結果中!")
            print(f"   排名: 第 {rank} 名")
            print(f"   消費額: ${china_final.iloc[0]['value']:,.0f}M")
        else:
            print(f"\n❌ 中國不在最終結果中")

        if len(df_final) > 0:
            print(f"\n🏆 Top 10 消費國家:")
            for i, (idx, row) in enumerate(df_final.head(10).iterrows(), 1):
                print(f"  {i:2d}. {row['iso3']:3s} | {row['reporter_area_label']:40s} | ${row['value']:,.0f}M")

        print("=" * 60)

        # 返回數據
        map_data = {
            'countries': [str(x) for x in df_final['iso3'].tolist()],
            'country_names': [str(x) for x in df_final['reporter_area_label'].tolist()],
            'values': [float(x) for x in df_final['value'].tolist()]
        }

        stats = {
            'total_countries': int(len(df_final)),
            'total_expenditure': int(df_final['value'].sum()) if len(df_final) > 0 else 0,
            'avg_expenditure': int(df_final['value'].mean()) if len(df_final) > 0 else 0,
            'max_country': str(df_final.iloc[0]['reporter_area_label']) if len(df_final) > 0 else None,
            'max_value': int(df_final.iloc[0]['value']) if len(df_final) > 0 else 0
        }

        return {
            'year': int(year),
            'data': map_data,
            'stats': stats
        }