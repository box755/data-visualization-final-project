from flask import request
from flask_restful import Resource
from flask import current_app
import pandas as pd

from api.reports.data import get_country_mapping
from commons import parser


class CountryExpenditureBreakdownResource(Resource):
    """
    國家旅遊消費結構分析 API
    分析總消費中，旅遊消費 vs 交通消費的佔比
    """

    def get(self, country_code):
        # 載入消費數據
        path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_expenditure_10_2025.csv'

        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {'error': f'無法讀取數據檔案: {str(e)}'}, 500

        print("=" * 60)
        print(f"DEBUG: CountryExpenditureBreakdownResource - {country_code}")

        # 獲取參數
        year = parser.parse(request.args.get('year'), cast=int, default=2019)

        # 反向查找國家名稱
        country_mapping = get_country_mapping()
        reverse_mapping = {v: k for k, v in country_mapping.items()}
        country_name = reverse_mapping.get(country_code)

        if not country_name:
            return {
                'error': f'Country code {country_code} not found',
                'country_code': country_code
            }, 404

        print(f"國家: {country_name} ({country_code})")
        print(f"年份: {year}")

        # 篩選該國家和年份的數據
        df_country = df[
            (df['reporter_area_label'] == country_name) &
            (df['partner_area_label'] == 'World') &
            (df['year'] == year)
            ].copy()

        if len(df_country) == 0:
            return {
                'error': f'No data for {country_name} in {year}',
                'country': country_name,
                'country_code': country_code,
                'year': year
            }, 404

        print(f"\n找到 {len(df_country)} 行數據")

        # 提取三種消費類型
        expenditure_data = {}

        for _, row in df_country.iterrows():
            indicator = row['indicator_code']
            value = pd.to_numeric(row['value'], errors='coerce')

            if pd.notna(value):
                expenditure_data[indicator] = {
                    'value': float(value),
                    'label': row['indicator_label'],
                    'unit': row.get('unit', 'million US dollars')
                }

        print(f"\n可用指標:")
        for code, data in expenditure_data.items():
            print(f"  {code}: ${data['value']:,.0f}M")

        # 判斷數據可用性
        has_total = 'INBD_EXPD_BPAY_TOTL_VSTR' in expenditure_data
        has_travel = 'INBD_EXPD_BPAY_TRVL_VSTR' in expenditure_data
        has_transport = 'INBD_EXPD_BPAY_PSTR_VSTR' in expenditure_data

        # 計算消費結構
        breakdown = None
        calculation_method = None

        # 方法 1: 有總額、旅遊、交通 - 最理想
        if has_total and has_travel and has_transport:
            total = expenditure_data['INBD_EXPD_BPAY_TOTL_VSTR']['value']
            travel = expenditure_data['INBD_EXPD_BPAY_TRVL_VSTR']['value']
            transport = expenditure_data['INBD_EXPD_BPAY_PSTR_VSTR']['value']
            other = total - travel - transport

            breakdown = {
                'travel': travel,
                'transport': transport,
                'other': max(0, other)  # 確保不為負數
            }
            calculation_method = 'total_breakdown'

        # 方法 2: 有總額和交通，推算旅遊
        elif has_total and has_transport:
            total = expenditure_data['INBD_EXPD_BPAY_TOTL_VSTR']['value']
            transport = expenditure_data['INBD_EXPD_BPAY_PSTR_VSTR']['value']
            travel = total - transport

            breakdown = {
                'travel': max(0, travel),
                'transport': transport,
                'other': 0
            }
            calculation_method = 'total_minus_transport'

        # 方法 3: 有旅遊和交通，推算總額
        elif has_travel and has_transport:
            travel = expenditure_data['INBD_EXPD_BPAY_TRVL_VSTR']['value']
            transport = expenditure_data['INBD_EXPD_BPAY_PSTR_VSTR']['value']

            breakdown = {
                'travel': travel,
                'transport': transport,
                'other': 0
            }
            calculation_method = 'travel_plus_transport'

        # 無法計算結構
        else:
            return {
                'error': 'Insufficient data for breakdown analysis',
                'country': country_name,
                'country_code': country_code,
                'year': year,
                'available_indicators': list(expenditure_data.keys()),
                'debug': {
                    'has_total': has_total,
                    'has_travel': has_travel,
                    'has_transport': has_transport
                }
            }, 404

        # 計算百分比
        total_calculated = sum(breakdown.values())
        percentages = {
            key: (value / total_calculated * 100) if total_calculated > 0 else 0
            for key, value in breakdown.items()
        }

        # 準備返回數據
        categories = []

        if breakdown['travel'] > 0:
            categories.append({
                'name': '旅遊消費',
                'name_en': 'Travel Expenditure',
                'value': breakdown['travel'],
                'percentage': percentages['travel'],
                'color': '#0ea5e9',
                'description': '住宿、餐飲、購物、當地交通等'
            })

        if breakdown['transport'] > 0:
            categories.append({
                'name': '國際交通',
                'name_en': 'International Transport',
                'value': breakdown['transport'],
                'percentage': percentages['transport'],
                'color': '#f59e0b',
                'description': '國際機票、船票、跨國車票等'
            })

        if breakdown['other'] > 0:
            categories.append({
                'name': '其他消費',
                'name_en': 'Other Expenditure',
                'value': breakdown['other'],
                'percentage': percentages['other'],
                'color': '#6b7280',
                'description': '其他未分類消費'
            })

        print(f"\n✅ 消費結構分析:")
        print(f"  計算方法: {calculation_method}")
        print(f"  旅遊消費: ${breakdown['travel']:,.0f}M ({percentages['travel']:.1f}%)")
        print(f"  國際交通: ${breakdown['transport']:,.0f}M ({percentages['transport']:.1f}%)")
        if breakdown['other'] > 0:
            print(f"  其他消費: ${breakdown['other']:,.0f}M ({percentages['other']:.1f}%)")
        print("=" * 60)

        return {
            'country': country_name,
            'country_code': country_code,
            'year': year,
            'data': {
                'categories': categories,
                'total': total_calculated,
                'currency': 'million US dollars'
            },
            'metadata': {
                'calculation_method': calculation_method,
                'available_indicators': list(expenditure_data.keys()),
                'data_quality': 'complete' if calculation_method == 'total_breakdown' else 'estimated'
            }
        }