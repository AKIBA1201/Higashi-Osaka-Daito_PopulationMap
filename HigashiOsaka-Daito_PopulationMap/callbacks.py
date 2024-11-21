# callbacks.py

import pandas as pd  # データ操作ライブラリ。データフレーム形式でのデータ処理や分析に使用
import plotly.express as px  # 簡易でインタラクティブなグラフ作成ツール
import plotly.graph_objects as go  # 高度にカスタマイズ可能なグラフ作成用ツール
from dash.dependencies import Output, Input  # Dashコールバックで出力（Output）と入力（Input）を定義するためのモジュール
from layout import variable_options  # 別ファイルから変数オプション（ドロップダウン選択肢など）をインポート
from data_loader import load_municipality_data  # 別ファイルから市区町村データを読み込む関数をインポート
import logging  # ログを出力するためのモジュール。デバッグや問題のトラッキングに役立つ

def register_callbacks(app): # Dashアプリケーションにコールバックを登録する関数
    @app.callback( # コールバックを定義するデコレーター
        Output('mapPlot', 'figure'), # 出力対象。ここではIDが 'mapPlot' のグラフに更新されたFigureを渡す
        [Input('city_selection', 'value'), Input('variable', 'value')] # 入力対象。'city_selection' と 'variable' の値を監視
    )
    def update_map(city, selected_var): # 選択したcityと変数selected_varに基づいて地図を更新する関数
        logging.debug(f"update_map callback triggered with city: {city}, selected_var: {selected_var}") # ログにcityとselected_varの値を記録
        print(f"update_map callback triggered with city: {city}, selected_var: {selected_var}") # コンソールにcityとselected_varの値を出力
        
        if not city or not selected_var: # ユーザーが市区町村（city）または変数（selected_var）を選択していない場合の処理
            logging.info("City or variable not selected. Returning empty figure.") # ログに「市区町村または変数が未選択」と記録
            print("City or variable not selected. Returning empty figure.") # コンソールにも同じメッセージを出力
            return go.Figure() # 空のFigureを返して終了

        try:
            # 東大阪市＆大東市
            if city == 'higashiosaka_daitou': # 東大阪市＆大東市を選択された場合
                data1 = load_municipality_data('higashiosaka')
                data2 = load_municipality_data('daitou')
                data = pd.concat([data1, data2], ignore_index=True) # 両市のデータを結合
            else:
                data = load_municipality_data(city) # 他の市の場合、その市のデータのみを読み込む

            display_label = [k for k, v in variable_options.items() if v == selected_var][0] # 選択された変数（selected_var）に対応するラベル（key）を取得

            if 'town_name' not in data.columns: # 'town_name' がデータに含まれていない場合空のFigure
                logging.error("Column 'town_name' not found in data.")
                print("Column 'town_name' not found in data.")
                return go.Figure()

            if data.geometry.isnull().all(): # 全て欠損値かどうかを確認。もしそうなら空のFigure
                logging.error("Geometry data is missing.")
                print("Geometry data is missing.")
                return go.Figure()

            if data.crs != "EPSG:4326": # データの座標参照系が EPSG:4326 でない場合変換
                data = data.to_crs(epsg=4326)
                logging.info("Coordinate reference system transformed to EPSG:4326.")
                print("Coordinate reference system transformed to EPSG:4326.")

            logging.debug(f"Generating map with selected_var: {selected_var}")
            print(f"Generating map with selected_var: {selected_var}")
            
            fig = px.choropleth_mapbox(
                data, # 入力データ
                geojson=data.__geo_interface__, # GeoJSON形式でのジオメトリ情報指定
                locations='town_name', # データフレームの列から地図の位置（町名）を指定
                color=selected_var, # 色付けに使う変数（ドロップダウンで選択された変数に基づく）
                featureidkey='properties.town_name', # GeoJSON内の町名プロパティとデータを対応付けるキー
                mapbox_style="open-street-map", # 地図のスタイル（オープンストリートマップ）
                center={"lat": data.geometry.centroid.y.mean(), "lon": data.geometry.centroid.x.mean()},# 地図の初期表示の中心座標を設定
                opacity=0.5, # 地図上の色付けの透明度を指定  
                labels={selected_var: display_label}
            )
            # 選んだ市の地図の表示の仕方
            if city == 'higashiosaka_daitou':
                fig.update_layout(
                    mapbox=dict(
                        zoom=11.9,
                        center={
                            "lat": data.geometry.centroid.y.mean() + 0.004,  # 地図縦軸調整
                            "lon": data.geometry.centroid.x.mean() + 0.006   # 地図横軸調整
                        }
                    )
                )
            if city == 'higashiosaka':
                fig.update_layout(
                    mapbox=dict(
                        zoom=12.4,
                        center={
                            "lat": data.geometry.centroid.y.mean() - 0.002,
                            "lon": data.geometry.centroid.x.mean() + 0.015
                        }
                    )
                )
            if city == 'daitou':
                fig.update_layout(
                    mapbox=dict(
                        zoom=13.1,
                        center={
                            "lat": data.geometry.centroid.y.mean() + 0.001,
                            "lon": data.geometry.centroid.x.mean() + 0.006
                        }
                    )
                )
            fig.update_traces(hovertemplate="<b>%{location}</b><br>" + display_label + ": %{z}<extra></extra>")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            logging.info("Map updated successfully.")
            print("Map updated successfully.")
            return fig
        except FileNotFoundError as e:
            logging.error(e)
            print(e)
            return go.Figure()
        except Exception as e:
            logging.exception("予期しないエラーが発生しました。")
            print("予期しないエラーが発生しました。")
            return go.Figure()

    @app.callback(
        Output('barPlot', 'figure'),
        [Input('mapPlot', 'clickData'), Input('city_selection', 'value')]
    )
    def update_bar(clickData, city):
        logging.debug("update_bar callback triggered.")
        print("update_bar callback triggered.")
        
        if not clickData or not city:
            logging.info("Insufficient data for bar plot. Returning empty figure.")
            print("Insufficient data for bar plot. Returning empty figure.")
            return go.Figure()

        try:
            town_name = clickData['points'][0]['location']
            logging.info(f"Clicked town: {town_name}")
            print(f"Clicked town: {town_name}")
            
            # 東大阪市＆大東市
            if city == 'higashiosaka_daitou':
                data1 = load_municipality_data('higashiosaka')
                data2 = load_municipality_data('daitou')
                data = pd.concat([data1, data2], ignore_index=True)
            else:
                data = load_municipality_data(city)

            selected_town_data = data[data['town_name'] == town_name]
            logging.info(f"Updating bar plot for town: {town_name}")
            print(f"Updating bar plot for town: {town_name}")

            if selected_town_data.empty:
                logging.warning(f"No data found for town: {town_name}")
                print(f"No data found for town: {town_name}")
                return go.Figure()

            # 年齢別変数のリスト
            age_groups = [
                'age_0_4', 'age_5_9', 'age_10_14', 'age_15_19',
                'age_20_24', 'age_25_29', 'age_30_34', 'age_35_39',
                'age_40_44', 'age_45_49', 'age_50_54', 'age_55_59',
                'age_60_64', 'age_65_69', 'age_70_74'#, 'age_over_75'
            ]
            age_labels = [
                '0-4', '5-9', '10-14', '15-19',
                '20-24', '25-29', '30-34', '35-39',
                '40-44', '45-49', '50-54', '55-59',
                '60-64', '65-69', '70-74'#, '75以上'
            ]

            # 年齢区分ごとの人口を取得
            population_values = []
            actual_age_labels = []
            for ag, label in zip(age_groups, age_labels):
                if ag in selected_town_data.columns:
                    population = selected_town_data[ag].iloc[0]
                    population_values.append(population if not pd.isnull(population) else 0)
                    actual_age_labels.append(label)
                else:
                    # 列が存在しない場合は0を設定
                    population_values.append(0)
                    actual_age_labels.append(label)

            df = pd.DataFrame({'AgeGroup': actual_age_labels, 'Population': population_values})
            fig = px.bar(df, x='AgeGroup', y='Population', title=f'{town_name}の年齢層別人口')

            fig.update_layout(
                title={
                    'text': f'{town_name}の年齢層別人口',  # タイトルテキスト
                    'x': 0.503,  # タイトルの水平位置を調整
                    'xanchor': 'center',  # 中央揃え
                    'font': {'size': 14}  # タイトルフォントサイズ
                },
                xaxis_title='', yaxis_title='', xaxis_tickangle=45)
            logging.info("Bar plot updated successfully.")
            print("Bar plot updated successfully.")
            return fig

        except Exception as e:
            logging.exception("バープロットの更新中にエラーが発生しました。")
            print("バープロットの更新中にエラーが発生しました。")
            return go.Figure()
