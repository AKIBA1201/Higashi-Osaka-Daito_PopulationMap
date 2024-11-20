# callbacks.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from layout import variable_options
from data_loader import load_municipality_data
import logging

def register_callbacks(app):
    @app.callback(
        Output('mapPlot', 'figure'),
        [Input('city_selection', 'value'), Input('variable', 'value')]
    )
    def update_map(city, selected_var):
        logging.debug(f"update_map callback triggered with city: {city}, selected_var: {selected_var}")
        print(f"update_map callback triggered with city: {city}, selected_var: {selected_var}")
        
        if not city or not selected_var:
            logging.info("City or variable not selected. Returning empty figure.")
            print("City or variable not selected. Returning empty figure.")
            return go.Figure()

        try:
            # 東大阪市＆大東市
            if city == 'higashiosaka_daitou':
                data1 = load_municipality_data('higashiosaka')
                data2 = load_municipality_data('daitou')
                data = pd.concat([data1, data2], ignore_index=True)
            else:
                data = load_municipality_data(city)

            display_label = [k for k, v in variable_options.items() if v == selected_var][0]

            if 'town_name' not in data.columns:
                logging.error("Column 'town_name' not found in data.")
                print("Column 'town_name' not found in data.")
                return go.Figure()

            if data.geometry.isnull().all():
                logging.error("Geometry data is missing.")
                print("Geometry data is missing.")
                return go.Figure()

            if data.crs != "EPSG:4326":
                data = data.to_crs(epsg=4326)
                logging.info("Coordinate reference system transformed to EPSG:4326.")
                print("Coordinate reference system transformed to EPSG:4326.")

            logging.debug(f"Generating map with selected_var: {selected_var}")
            print(f"Generating map with selected_var: {selected_var}")
            
            fig = px.choropleth_mapbox(
                data,
                geojson=data.__geo_interface__,
                locations='town_name',
                color=selected_var,
                featureidkey='properties.town_name',
                mapbox_style="open-street-map",
                zoom=12.2,
                center={"lat": data.geometry.centroid.y.mean(), "lon": data.geometry.centroid.x.mean()},
                opacity=0.5,
                labels={selected_var: display_label}
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

            fig.update_layout(xaxis_title='', yaxis_title='', xaxis_tickangle=45)
            logging.info("Bar plot updated successfully.")
            print("Bar plot updated successfully.")
            return fig

        except Exception as e:
            logging.exception("バープロットの更新中にエラーが発生しました。")
            print("バープロットの更新中にエラーが発生しました。")
            return go.Figure()