# layout.py
from dash import dcc, html

# 変数選択オプションの定義
variable_options = {
    # 生徒候補
    "男女20-39歳": "age_20_39",
    "男女小4-中3_10-14歳": "age_10_14",
    "男20-39歳": "male_age_20_39",
    "女20-39歳": "female_age_20_39",
    "男小4-中3_10-14歳": "male_age_10_14",
    "女小4-中3_10-14歳": "female_age_10_14",
    
    # 総人口関連
    "総人口": "population_total",
    "男性": "male_total",
    "女性": "female_total",

    # 年齢別
    "10歳未満": "age_under_10",
    "10-19歳": "age_10_19",
    "20-29歳": "age_20_29",
    "30-39歳": "age_30_39",
    "40-49歳": "age_40_49",
    "50-59歳": "age_50_59",
    "60-69歳": "age_60_69",
    "70-74歳": "age_70_74",
    "75歳以上": "age_over_75",

    # 男性の年齢別
    "男性 10歳未満": "male_age_under_10",
    "男性 10-19歳": "male_age_10_19",
    "男性 20-29歳": "male_age_20_29",
    "男性 30-39歳": "male_age_30_39",
    "男性 40-49歳": "male_age_40_49",
    "男性 50-59歳": "male_age_50_59",
    "男性 60-69歳": "male_age_60_69",
    "男性 70-74歳": "male_age_70_74",
    "男性 75歳以上": "male_age_over_75",

    # 女性の年齢別
    "女性 10歳未満": "female_age_under_10",
    "女性 10-19歳": "female_age_10_19",
    "女性 20-29歳": "female_age_20_29",
    "女性 30-39歳": "female_age_30_39",
    "女性 40-49歳": "female_age_40_49",
    "女性 50-59歳": "female_age_50_59",
    "女性 60-69歳": "female_age_60_69",
    "女性 70-74歳": "female_age_70_74",
    "女性 75歳以上": "female_age_over_75"
}

# レイアウト構成
layout = html.Div([
    html.Div([
        html.Div(style={'height': '20px'}),

        # 自治体選択ドロップダウン
        dcc.Dropdown(
            id='city_selection',
            options=[
                {'label': '東大阪市', 'value': 'higashiosaka'},
                {'label': '大東市', 'value': 'daitou'},
                {'label': '東大阪市＆大東市', 'value': 'higashiosaka_daitou'}

                # 他の自治体を追加する場合はここに追加
            ],
            value='higashiosaka',  # デフォルト値を設定
            placeholder="▼選択してください",
            style={'width': '100%'}
        ),

        html.Div(style={'height': '10px'}),

        # 変数選択ドロップダウン（総人口・男性・女性・年齢別を含む）
        dcc.Dropdown(
            id='variable',
            options=[{'label': k, 'value': v} for k, v in variable_options.items()],
            value='age_20_39',  # デフォルト値を設定
            placeholder="▼選択してください",
            style={'width': '100%'}
        ),

        html.Div(style={'height': '10px'}),

        # バープロット
        dcc.Graph(id='barPlot', style={'height': '600px'})
    ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),

    # 地図表示部分
    html.Div([
        dcc.Graph(id='mapPlot', style={'height': '750px', 'width': '100%'})
    ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'})
])
