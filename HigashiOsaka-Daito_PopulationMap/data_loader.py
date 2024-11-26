# data_loader.py

import os
import pandas as pd
import geopandas as gpd
import logging

def load_municipality_data(municipality_name):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, "data", municipality_name)
    
    logging.debug(f"Loading data for municipality: {municipality_name}")
    print(f"Loading data for municipality: {municipality_name}")
    
    # CSVファイルを指定
    pop_file = os.path.join(data_dir, f"{municipality_name}_population.csv")
    try:
        # CSVファイルを読み込む（エンコーディングは必要に応じて変更）
        population_data = pd.read_csv(pop_file, encoding='utf-8')
        logging.debug(f"Population data columns before processing: {population_data.columns.tolist()}")
        print(f"Population data columns before processing: {population_data.columns.tolist()}")
        
        # 列名を加工して整える
        population_data.rename(columns={'NAME': 'town_name'}, inplace=True)
        population_data.columns = population_data.columns.str.replace(r'[\n\r\s　]+', '', regex=True).str.lower()
        population_data.columns = population_data.columns.str.replace('歳', '', regex=False)
        
        if 'town_name' not in population_data.columns:
            logging.error("'town_name' 列が population_data に存在しません。")
            print("'town_name' 列が population_data に存在しません。")
            raise KeyError("'town_name' 列が population_data に存在しません。")
        
        # 年齢別変数の生成
        population_data = population_data.assign( # 年齢区分や性別ごとの集計値を新たな列として追加
            age_0_4=population_data['０～４'],
            age_5_9=population_data['５～９'],
            age_10_14=population_data['１０～１４'],
            age_15_19=population_data['１５～１９'],
            age_20_24=population_data['２０～２４'],
            age_25_29=population_data['２５～２９'],
            age_30_34=population_data['３０～３４'],
            age_35_39=population_data['３５～３９'],
            age_40_44=population_data['４０～４４'],
            age_45_49=population_data['４５～４９'],
            age_50_54=population_data['５０～５４'],
            age_55_59=population_data['５５～５９'],
            age_60_64=population_data['６０～６４'],
            age_65_69=population_data['６５～６９'],
            age_70_74=population_data['７０～７４'],
            age_over_75=population_data['７５以上'],
            
            male_age_under_10=population_data['男０～４'] + population_data['男５～９'],
            male_age_10_14=population_data['男１０～１４'],
            male_age_10_19=population_data['男１０～１４'] + population_data['男１５～１９'],
            male_age_20_29=population_data['男２０～２４'] + population_data['男２５～２９'],
            male_age_20_39=population_data['男２０～２４'] + population_data['男２５～２９'] + population_data['男３０～３４'] + population_data['男３５～３９'],
            male_age_30_39=population_data['男３０～３４'] + population_data['男３５～３９'],
            male_age_40_49=population_data['男４０～４４'] + population_data['男４５～４９'],
            male_age_50_59=population_data['男５０～５４'] + population_data['男５５～５９'],
            male_age_60_69=population_data['男６０～６４'] + population_data['男６５～６９'],
            male_age_70_74=population_data['男７０～７４'],
            male_age_over_75=population_data['男７５以上'],

            female_age_under_10=population_data['女０～４'] + population_data['女５～９'],
            female_age_10_14=population_data['女１０～１４'],
            female_age_10_19=population_data['女１０～１４'] + population_data['女１５～１９'],
            female_age_20_29=population_data['女２０～２４'] + population_data['女２５～２９'],
            female_age_20_39=population_data['女２０～２４'] + population_data['女２５～２９'] + population_data['女３０～３４'] + population_data['女３５～３９'],
            female_age_30_39=population_data['女３０～３４'] + population_data['女３５～３９'],
            female_age_40_49=population_data['女４０～４４'] + population_data['女４５～４９'],
            female_age_50_59=population_data['女５０～５４'] + population_data['女５５～５９'],
            female_age_60_69=population_data['女６０～６４'] + population_data['女６５～６９'],
            female_age_70_74=population_data['女７０～７４'],
            female_age_over_75=population_data['女７５以上'],
            
            #特殊
            age_under_10=population_data['０～４'] + population_data['５～９'],
            age_10_19=population_data['１０～１４'] + population_data['１５～１９'],
            age_20_29=population_data['２０～２４'] + population_data['２５～２９'],
            age_20_39=population_data['２０～２４'] + population_data['２５～２９'] + population_data['３０～３４'] + population_data['３５～３９'],
            age_30_39=population_data['３０～３４'] + population_data['３５～３９'],
            age_40_49=population_data['４０～４４'] + population_data['４５～４９'],
            age_50_59=population_data['５０～５４'] + population_data['５５～５９'],
            age_60_69=population_data['６０～６４'] + population_data['６５～６９'],
        )
        
        # 列名を簡潔に変更
        population_data.rename(columns={
            '人口総数': 'population_total',
            '男性総数': 'male_total',
            '女性総数': 'female_total'
        }, inplace=True)
        
        logging.debug(f"Final population_data columns: {population_data.columns.tolist()}")
        print(f"Final population_data columns: {population_data.columns.tolist()}")
    except FileNotFoundError:
        logging.error(f"Population data file not found for {municipality_name}")
        print(f"Population data file not found for {municipality_name}")
        raise FileNotFoundError(f"Population data file not found for {municipality_name}")
    except KeyError as e:
        logging.error(f"人口データの読み込み中にエラーが発生しました: {e}")
        print(f"人口データの読み込み中にエラーが発生しました: {e}")
        raise e
    except Exception as e:
        logging.error(f"人口データの読み込み中にエラーが発生しました: {e}")
        print(f"人口データの読み込み中にエラーが発生しました: {e}")
        raise e

    # シェイプファイルの読み込み
    try:
        shape_file = None
        expected_shape_filename = f"{municipality_name}.shp".lower()
        for file in os.listdir(data_dir):
            if file.endswith('.shp') and not file.startswith('~$') and file.lower() == expected_shape_filename:
                shape_file = os.path.join(data_dir, file)
                break
        
        if not shape_file:
            logging.error(f"No shapefile found for {municipality_name}")
            print(f"No shapefile found for {municipality_name}")
            raise FileNotFoundError(f"No shapefile found for {municipality_name}")

        try:
            map_data_town = gpd.read_file(shape_file, encoding='utf-8')
        except UnicodeDecodeError:
            map_data_town = gpd.read_file(shape_file, encoding='shift_jis')

        logging.debug(f"Shapefile data columns: {map_data_town.columns.tolist()}")
        print(f"Shapefile data columns: {map_data_town.columns.tolist()}")
    except Exception as e:
        logging.error(f"シェイプファイルの読み込み中にエラーが発生しました: {e}")
        print(f"シェイプファイルの読み込み中にエラーが発生しました: {e}")
        raise e

    # マージ用の列を探す
    possible_merge_columns = ['s_name', 'moji', 'name', '町名', 'town_name']
    map_data_town.columns = map_data_town.columns.str.lower()
    merge_left_on = next((col for col in possible_merge_columns if col in map_data_town.columns), None)

    if not merge_left_on:
        logging.error(f"シェイプファイル内にマージ用の列が見つかりませんでした ({municipality_name})")
        print(f"シェイプファイル内にマージ用の列が見つかりませんでした ({municipality_name})")
        print(f"利用可能な列名: {map_data_town.columns.tolist()}")
        raise KeyError("マージ用の列がシェイプファイルに存在しません。")

    try:
        population_data['town_name'] = population_data['town_name'].str.strip().str.lower()
        map_data_town[merge_left_on] = map_data_town[merge_left_on].astype(str).str.strip().str.lower()
        map_data_town = map_data_town.merge(population_data, left_on=merge_left_on, right_on='town_name', how='left')
        logging.debug(f"After merge, map_data_town columns: {map_data_town.columns.tolist()}")
        print(f"After merge, map_data_town columns: {map_data_town.columns.tolist()}")
    except Exception as e:
        logging.error(f"データのマージ中にエラーが発生しました: {e}")
        print(f"データのマージ中にエラーが発生しました: {e}")
        raise e

    logging.info("データのマージが完了しました。")
    print("データのマージが完了しました。")

    logging.debug(f"Final map_data_town columns: {map_data_town.columns.tolist()}")
    print(f"Final map_data_town columns: {map_data_town.columns.tolist()}")

    return map_data_town
