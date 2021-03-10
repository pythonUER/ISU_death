# Основные списки
import pandas as pd
import numpy as np
from connect_PostGres import cnx
from functools import partial
from operator import is_not
from datetime import date
from sqlalchemy import types


def not_nan_filter(df, col):
    unique_list = list(filter(partial(is_not, np.nan), df[col].unique()))
    return unique_list


########################################################################################################################
REGION = ['Воловский', 'Грязинский', 'Данковский', 'Добринский', 'Добровский', 'Долгоруковский', 'Елецкий',
          'Задонский', 'Измалковский', 'Краснинский', 'Лебедянский', 'Лев-Толстовский', 'Липецкий', 'Становлянский',
          'Тербунский',  'Усманский', 'Хлевенский', 'Чаплыгинский', 'Елец', 'Липецк']

AgeGroupList = {0: '0-4', 1: '0-4', 2: '0-4', 3: '0-4', 4: '0-4',
                5: '5-9', 6: '5-9', 7: '5-9', 8: '5-9', 9: '5-9',
                10: '10-14', 11: '10-14', 12: '10-14', 13: '10-14', 14: '10-14',
                15: '15-19', 16: '15-19', 17: '15-19', 18: '15-19', 19: '15-19',
                20: '20-24', 21: '20-24', 22: '20-24', 23: '20-24', 24: '20-24',
                25: '25-29', 26: '25-29', 27: '25-29', 28: '25-29', 29: '25-29',
                30: '30-34', 31: '30-34', 32: '30-34', 33: '30-34', 34: '30-34',
                35: '35-39', 36: '35-39', 37: '35-39', 38: '35-39', 39: '35-39',
                40: '40-44', 41: '40-44', 42: '40-44', 43: '40-44', 44: '40-44',
                45: '45-49', 46: '45-49', 47: '45-49', 48: '45-49', 49: '45-49',
                50: '50-54', 51: '50-54', 52: '50-54', 53: '50-54', 54: '50-54',
                55: '55-59', 56: '55-59', 57: '55-59', 58: '55-59', 59: '55-59',
                60: '60-64', 61: '60-64', 62: '60-64', 63: '60-64', 64: '60-64',
                65: '65-69', 66: '65-69', 67: '65-69', 68: '65-69', 69: '65-69',
                70: '70-74', 71: '70-74', 72: '70-74', 73: '70-74', 74: '70-74',
                75: '75-79', 76: '75-79', 77: '75-79', 78: '75-79', 79: '75-79',
                80: '80-84', 81: '80-84', 82: '80-84', 83: '80-84', 84: '80-84',
                85: '85-89', 86: '85-89', 87: '85-89', 88: '85-89', 89: '85-89',
                90: '90-94', 91: '90-94', 92: '90-94', 93: '90-94', 94: '90-94',
                95: '95-99', 96: '95-99', 97: '95-99', 98: '95-99', 99: '95-99',
                '': ''}

EmployeeAgeList = {'100 и более': 'Старше трудоспособного возраста', '95-99': 'Старше трудоспособного возраста',
                   '90-94': 'Старше трудоспособного возраста', '85-89': 'Старше трудоспособного возраста',
                   '80-84': 'Старше трудоспособного возраста', '75-79': 'Старше трудоспособного возраста',
                   '70-74': 'Старше трудоспособного возраста', '65-69': 'Старше трудоспособного возраста',
                   '60-64': 'Трудоспособного возраста', '55-59': 'Трудоспособного возраста',
                   '50-54': 'Трудоспособного возраста', '45-49': 'Трудоспособного возраста',
                   '40-44': 'Трудоспособного возраста', '35-39': 'Трудоспособного возраста',
                   '30-34': 'Трудоспособного возраста', '25-29': 'Трудоспособного возраста',
                   '20-24': 'Трудоспособного возраста', '15-19': 'Трудоспособного возраста',
                   '10-14': 'Младше трудоспособного возраста', '5-9': 'Младше трудоспособного возраста',
                   '0-4': 'Младше трудоспособного возраста'}
########################################################################################################################
Main_MKB_dict = {0: 'MKB_GROUP_NAME_a',
                 1: 'MKB_GROUP_NAME_b',
                 2: 'MKB_GROUP_NAME_v',
                 3: 'MKB_GROUP_NAME_g'}

df_MKB = pd.read_sql_query('''SELECT * FROM public."MKB"''', cnx)
df_MKB = df_MKB.drop(columns=['id'])

MKB_CODE_LIST = not_nan_filter(df_MKB, 'MKB_CODE')
MKB_GROUP_LIST = not_nan_filter(df_MKB, 'MKB_GROUP_NAME')
MKB_GROUP_LIST_MAIN = ['НОВООБРАЗОВАНИЯ (C00-D48)', 'ПСИХИЧЕСКИЕ РАССТРОЙСТВА И РАССТРОЙСТВА ПОВЕДЕНИЯ (F00-F99)',
                       'БОЛЕЗНИ ЭНДОКРИННОЙ СИСТЕМЫ, РАССТРОЙСТВА ПИТАНИЯ И НАРУШЕНИЯ ОБМЕНА ВЕЩЕСТВ (E00-E90)',
                       'БОЛЕЗНИ НЕРВНОЙ СИСТЕМЫ (G00-G99)', 'БОЛЕЗНИ СИСТЕМЫ КРОВООБРАЩЕНИЯ (I00-I99)',
                       'БОЛЕЗНИ ОРГАНОВ ДЫХАНИЯ (J00-J99)', 'БОЛЕЗНИ ОРГАНОВ ПИЩЕВАРЕНИЯ (K00-K93)',
                       'СИМПТОМЫ, ПРИЗНАКИ И ОТКЛОНЕНИЯ ОТ НОРМЫ, ВЫЯВЛЕННЫЕ ПРИ КЛИНИЧЕСКИХ И ЛАБОРАТОРНЫХ ИССЛЕДОВАНИЯХ, НЕ КЛАССИФИЦИРОВАННЫЕ В ДРУГИХ РУБРИКАХ (R00-R99)',
                       'ТРАВМЫ, ОТРАВЛЕНИЯ И НЕКОТОРЫЕ ДРУГИЕ ПОСЛЕДСТВИЯ ВОЗДЕЙСТВИЯ ВНЕШНИХ ПРИЧИН (S00-T98)']
########################################################################################################################
MONTH_number = list(range(1, 13))
MONTH_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
              'Октябрь', 'Ноябрь', 'Декабрь']
MONTHS_dict = dict(zip(MONTH_number, MONTH_name))
########################################################################################################################
df_FIO = pd.read_sql_query('''SELECT * FROM public."fio_recipient"''', cnx)
FIO_dict = dict(zip(df_FIO.position, df_FIO.fio))

escalation_recipient_list = {1: 'Начальник Управления здравоохранения',
                             2: 'Заместитель главы администрации (вопросы здравоохранения, соц.защиты, труда и занятости населения, демографической политики)',
                             3: 'Глава администрации'}

escalation_recipient_text = {1: 'Разобраться.',
                             2: 'Принять меры.',
                             3: 'Заслушать доклад.'}
########################################################################################################################
df_Population = pd.read_sql_query('''SELECT * FROM public."population_view"''', cnx)
df_Population = df_Population[(df_Population['Region'].isin(REGION)) &
                              (df_Population['Territory'].isin(['Все население'])) &
                              (df_Population['Gender'].isin(['Оба пола']))]
df_Population.index = range(df_Population.shape[0])
df_Population.columns = ['id', 'Feature', 'Region', 'Territory', 'GENDER', 'AGE_GROUP', 'Year', 'Population']
########################################################################################################################
results_files_path = r'../attached_file/'
results_files_suff = f'1-{date.today().month}-{date.today().year}'
########################################################################################################################
column_name_type_death_finished = {'gender': types.VARCHAR,
                                   'reason_a': types.VARCHAR, 'original_reason_a': types.INTEGER,
                                   'reason_b': types.VARCHAR, 'original_reason_b': types.INTEGER,
                                   'reason_v': types.VARCHAR, 'original_reason_v': types.INTEGER,
                                   'reason_g': types.VARCHAR, 'original_reason_g': types.INTEGER,
                                   'reason_d': types.VARCHAR,
                                   'date_born': types.TIMESTAMP,
                                   'date_death': types.TIMESTAMP,
                                   'day_death': types.INTEGER, 'week_death': types.INTEGER,
                                   'month_death': types.INTEGER, 'year_death': types.INTEGER,
                                   'age_death': types.INTEGER,
                                   'age_group_death': types.VARCHAR, 'employable_group': types.VARCHAR,
                                   'MKB_NAME_a': types.Text, 'MKB_GROUP_NAME_a': types.Text,
                                   'MKB_NAME_b': types.Text, 'MKB_GROUP_NAME_b': types.Text,
                                   'MKB_NAME_v': types.Text, 'MKB_GROUP_NAME_v': types.Text,
                                   'MKB_NAME_g': types.Text, 'MKB_GROUP_NAME_g': types.Text,
                                   'MKB_NAME_d': types.Text, 'MKB_GROUP_NAME_d': types.Text,
                                   'region_location': types.VARCHAR, 'district_location': types.VARCHAR,
                                   'locality_location': types.VARCHAR, 'street_location': types.VARCHAR,
                                   'locality_death': types.VARCHAR, 'street_death': types.VARCHAR,
                                   'MKB_GROUP_NAME_original_reason': types.Text, 'DATE': types.Date}
########################################################################################################################


if __name__ == '__main__':
    print(df_Population.loc[len(df_Population) - 1])
    print(MKB_GROUP_LIST[-1])
    print(REGION)
    print(df_Population[:10])
