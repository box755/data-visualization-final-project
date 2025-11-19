import pandas as pd
from flask import current_app


def get_tourism_data():
    """
    Load UN Tourism dataset and prepare for reports.
    載入聯合國旅遊數據集
    """
    path = current_app.config['BASE_DIR'] / 'data/UN_Tourism_inbound_arrivals_by_region_10_2025.csv'

    # 載入數據集
    df = pd.read_csv(path)

    print("=" * 60)
    print("DEBUG: 數據載入")
    print(f"總行數: {len(df)}")
    print(f"欄位: {df.columns.tolist()}")
    print(f"\n前 5 行:")
    print(df.head())
    print(f"\nindicator_code 唯一值:")
    print(df['indicator_code'].unique())
    print(f"\n年份範圍: {df['year'].min()} - {df['year'].max()}")
    print("=" * 60)

    # 只保留需要的欄位
    df = df[['reporter_area_code', 'reporter_area_label', 'year', 'value', 'indicator_code']]

    # 轉換數值欄位（千人轉換為人）
    df['value'] = pd.to_numeric(df['value'], errors='coerce') * 1000

    # 刪除無效值
    df = df.dropna()

    return df


def get_indicator_mapping():
    """
    指標代碼映射
    """
    return {
        'INBD_TRIP_PRPS_BNSS_TOUR': '商務旅遊',
        'INBD_TRIP_AREA_TOUR_ABRD': '入境遊客',
        'INBD_TRIP_PRPS_LEIS_TOUR': '休閒旅遊',
        'INBD_TRIP_PRPS_OTHR_TOUR': '其他目的',
    }


def get_country_mapping():
    """
    完整的國家代碼映射表（ISO-3 代碼）
    """
    mapping = {
        # A
        'Albania': 'ALB',
        'Algeria': 'DZA',
        'American Samoa': 'ASM',
        'Andorra': 'AND',
        'Angola': 'AGO',
        'Anguilla': 'AIA',
        'Antigua and Barbuda': 'ATG',
        'Argentina': 'ARG',
        'Armenia': 'ARM',
        'Aruba': 'ABW',
        'Australia': 'AUS',
        'Austria': 'AUT',
        'Azerbaijan': 'AZE',

        # B
        'Bahamas': 'BHS',
        'Bahrain': 'BHR',
        'Bangladesh': 'BGD',
        'Barbados': 'BRB',
        'Belarus': 'BLR',
        'Belgium': 'BEL',
        'Belize': 'BLZ',
        'Benin': 'BEN',
        'Bermuda': 'BMU',
        'Bhutan': 'BTN',
        'Bolivia (Plurinational State of)': 'BOL',
        'Bonaire': 'BES',
        'Bosnia and Herzegovina': 'BIH',
        'Botswana': 'BWA',
        'Brazil': 'BRA',
        'British Virgin Islands': 'VGB',
        'Brunei Darussalam': 'BRN',
        'Bulgaria': 'BGR',
        'Burkina Faso': 'BFA',
        'Burundi': 'BDI',

        # C
        'Cambodia': 'KHM',
        'Canada': 'CAN',
        'Cayman Islands': 'CYM',
        'Central African Republic': 'CAF',
        'Chad': 'TCD',
        'Chile': 'CHL',
        'China': 'CHN',
        'Taiwan Province of China': 'TWN',
        'China, Hong Kong Special Administrative Region': 'HKG',
        'Colombia': 'COL',
        'Comoros': 'COM',
        'Congo': 'COG',
        'Democratic Republic of the Congo': 'COD',
        'Cook Islands': 'COK',
        'Costa Rica': 'CRI',
        'Croatia': 'HRV',
        'Cuba': 'CUB',
        'Curaçao': 'CUW',
        'Cyprus': 'CYP',
        'Czech Republic': 'CZE',
        'Côte d\'Ivoire': 'CIV',

        # D
        'Denmark': 'DNK',
        'Djibouti': 'DJI',
        'Dominica': 'DMA',
        'Dominican Republic': 'DOM',

        # E
        'Ecuador': 'ECU',
        'Egypt': 'EGY',
        'El Salvador': 'SLV',
        'Eritrea': 'ERI',
        'Estonia': 'EST',
        'Eswatini': 'SWZ',
        'Ethiopia': 'ETH',

        # F
        'Fiji': 'FJI',
        'Finland': 'FIN',
        'France': 'FRA',
        'French Guiana': 'GUF',
        'French Polynesia': 'PYF',

        # G
        'Gabon': 'GAB',
        'Gambia': 'GMB',
        'Georgia': 'GEO',
        'Germany': 'DEU',
        'Ghana': 'GHA',
        'Greece': 'GRC',
        'Grenada': 'GRD',
        'Guadeloupe': 'GLP',
        'Guam': 'GUM',
        'Guatemala': 'GTM',
        'Guinea': 'GIN',
        'Guinea-Bissau': 'GNB',
        'Guyana': 'GUY',

        # H
        'Haiti': 'HTI',
        'Honduras': 'HND',
        'Hungary': 'HUN',

        # I
        'India': 'IND',
        'Indonesia': 'IDN',
        'Iran (Islamic Republic of)': 'IRN',
        'Ireland': 'IRL',
        'Israel': 'ISR',
        'Italy': 'ITA',

        # J
        'Jamaica': 'JAM',
        'Japan': 'JPN',
        'Jordan': 'JOR',

        # K
        'Kazakhstan': 'KAZ',
        'Kenya': 'KEN',
        'Kiribati': 'KIR',
        'Kuwait': 'KWT',
        'Kyrgyzstan': 'KGZ',
        'Republic of Korea': 'KOR',

        # L
        'Lao People\'s Democratic Republic': 'LAO',
        'Latvia': 'LVA',
        'Lesotho': 'LSO',
        'Libya': 'LBY',
        'Lithuania': 'LTU',
        'Luxembourg': 'LUX',

        # M
        'Madagascar': 'MDG',
        'Malawi': 'MWI',
        'Malaysia': 'MYS',
        'Maldives': 'MDV',
        'Mali': 'MLI',
        'Malta': 'MLT',
        'Marshall Islands': 'MHL',
        'Martinique': 'MTQ',
        'Mauritius': 'MUS',
        'Mexico': 'MEX',
        'Micronesia (Federated States of)': 'FSM',
        'Monaco': 'MCO',
        'Mongolia': 'MNG',
        'Montserrat': 'MSR',
        'Morocco': 'MAR',
        'Mozambique': 'MOZ',
        'Myanmar': 'MMR',

        # N
        'Namibia': 'NAM',
        'Nepal': 'NPL',
        'Netherlands (Kingdom of the)': 'NLD',
        'New Caledonia': 'NCL',
        'New Zealand': 'NZL',
        'Nicaragua': 'NIC',
        'Niger': 'NER',
        'Niue': 'NIU',
        'Northern Mariana Islands': 'MNP',
        'Norway': 'NOR',

        # O
        'Oman': 'OMN',

        # P
        'Pakistan': 'PAK',
        'Palau': 'PLW',
        'State of Palestine': 'PSE',
        'Panama': 'PAN',
        'Papua New Guinea': 'PNG',
        'Paraguay': 'PRY',
        'Peru': 'PER',
        'Philippines': 'PHL',
        'Poland': 'POL',
        'Portugal': 'PRT',

        # R
        'Romania': 'ROU',
        'Russian Federation': 'RUS',
        'Rwanda': 'RWA',
        'Réunion': 'REU',

        # S
        'Saint Kitts and Nevis': 'KNA',
        'Saint Lucia': 'LCA',
        'Saint Vincent and the Grenadines': 'VCT',
        'Samoa': 'WSM',
        'San Marino': 'SMR',
        'Sao Tome and Principe': 'STP',
        'Saudi Arabia': 'SAU',
        'Senegal': 'SEN',
        'Seychelles': 'SYC',
        'Sierra Leone': 'SLE',
        'Singapore': 'SGP',
        'Slovenia': 'SVN',
        'Solomon Islands': 'SLB',
        'South Africa': 'ZAF',
        'Spain': 'ESP',
        'Sri Lanka': 'LKA',
        'Sudan': 'SDN',
        'Suriname': 'SUR',
        'Sweden': 'SWE',
        'Switzerland': 'CHE',
        'Syrian Arab Republic': 'SYR',

        # T
        'Tajikistan': 'TJK',
        'Thailand': 'THA',
        'Togo': 'TGO',
        'Tonga': 'TON',
        'Trinidad and Tobago': 'TTO',
        'Turkey': 'TUR',
        'Türkiye': 'TUR',
        'Turkmenistan': 'TKM',
        'Turks and Caicos Islands': 'TCA',
        'Tuvalu': 'TUV',

        # U
        'Uganda': 'UGA',
        'Ukraine': 'UKR',
        'United Arab Emirates': 'ARE',
        'United Kingdom of Great Britain and Northern Ireland': 'GBR',
        'United Republic of Tanzania': 'TZA',
        'United States of America': 'USA',
        'Uruguay': 'URY',
        'Uzbekistan': 'UZB',

        # V
        'Vanuatu': 'VUT',
        'Venezuela (Bolivarian Republic of)': 'VEN',
        'Viet Nam': 'VNM',

        # Z
        'Zambia': 'ZMB',
        'Zimbabwe': 'ZWE'
    }

    return mapping


def get_available_years():
    """
    獲取數據中所有可用的年份
    """
    df = get_tourism_data()
    return sorted(df['year'].unique().tolist())


def get_available_countries():
    """
    獲取數據中所有可用的國家
    """
    df = get_tourism_data()
    return sorted(df['reporter_area_label'].unique().tolist())


def get_available_indicators():
    """
    獲取數據中所有可用的指標
    """
    df = get_tourism_data()
    return df['indicator_code'].unique().tolist()