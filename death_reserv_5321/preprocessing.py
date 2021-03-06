# Предобработка исходных данных, получаемых от МедСофт
from datetime import date, datetime
import logging
import pandas as pd

from connect_PostGres import cnx
from ISU_death_functions import make_date, make_date_born_death, make_day_week_month_year_death, calculate_death_age
from ISU_death_functions import calculate_age_group, calculate_employee_group, make_mkb, make_address
from ISU_death_functions import find_original_reason_mkb_group_name
from ISU_death_lists_dict import results_files_path, results_files_suff


def death_preprocessing(save_to_sql=True, save_to_excel=False):
    start_time = datetime.now()
    program = 'death_preprocessing'
    logging.info(f'{program} started')
    print(f'{program} started')

    df_death = pd.read_sql_query('''SELECT * FROM death''', cnx)

    df_death = df_death.drop(columns=['id', 'locality', 'place_death', 'family', 'education', 'occupation', 'locality2',
                                      'date_issue_certificate', 'reason_death', 'reason_established',
                                      'period_reason_a', 'period_reason_b', 'period_reason_c', 'period_reason_d',
                                      'period_reason_2d', 'road_accident'])
    df_death.columns = ['Пол', 'Дата рождения', 'Дата смерти', 'Место жительства', 'Место смерти',
                        'Причина а) КОД МКБ', 'Является первоначальной а)', 'Причина б)', 'Является первоначальной б)',
                        'Причина в)', 'Является первоначальной в)', 'Причина г)', 'Является первоначальной г)',
                        'Причина II (д)']
    print('Обрабатываем даты рождения и смерти...')
    date_col = ['Дата рождения', 'Дата смерти']
    df_death = make_date(df_death, date_col)
    df_death = make_date_born_death(df_death, date_col)
    df_death = make_date(df_death, ['ДАТА_РОЖДЕНИЯ', 'ДАТА_СМЕРТИ'])
    df_death = make_day_week_month_year_death(df_death)

    print('Обрабатываем возраст умершего...')
    df_death = calculate_death_age(df_death)
    df_death = calculate_age_group(df_death)
    df_death = calculate_employee_group(df_death)

    print('Обрабатываем диагнозы...')
    df_death = make_mkb(df_death, 'Причина а) КОД МКБ', 'а) MKB_NAME', 'а) MKB_GROUP_NAME')
    df_death = make_mkb(df_death, 'Причина б)', 'б) MKB_NAME', 'б) MKB_GROUP_NAME')
    df_death = make_mkb(df_death, 'Причина в)', 'в) MKB_NAME', 'в) MKB_GROUP_NAME')
    df_death = make_mkb(df_death, 'Причина г)',  'г) MKB_NAME', 'г) MKB_GROUP_NAME')
    df_death = make_mkb(df_death, 'Причина II (д)', 'д) MKB_NAME', 'д) MKB_GROUP_NAME')

    print('Обрабатываем адреса...')
    df_death = make_address(df_death, 'Место жительства', 'Место смерти')

    df_death = df_death.drop(columns=['Дата рождения', 'Дата смерти', 'Место жительства', 'Место смерти'])
    df_death.columns = ['gender', 'reason_a', 'original_reason_a', 'reason_b', 'original_reason_b', 'reason_v',
                        'original_reason_v', 'reason_g', 'original_reason_g', 'reason_d',
                        'date_born', 'date_death', 'day_death', 'week_death', 'month_death', 'year_death',
                        'age_death', 'age_group_death', 'employable_group',
                        'MKB_NAME_a', 'MKB_GROUP_NAME_a', 'MKB_NAME_b', 'MKB_GROUP_NAME_b', 'MKB_NAME_v',
                        'MKB_GROUP_NAME_v', 'MKB_NAME_g', 'MKB_GROUP_NAME_g', 'MKB_NAME_d', 'MKB_GROUP_NAME_d',
                        'region_location', 'district_location', 'locality_location', 'street_location',
                        'locality_death', 'street_death'
                        ]
    df_death = df_death[df_death['region_location'].isin(['Липецкая'])]
    df_death.index = range(df_death.shape[0])
    index_lipetsk = df_death[df_death['locality_location'] == 'Липецк'].index
    index_elec = df_death[df_death['locality_location'] == 'Елец'].index
    df_death.loc[index_lipetsk, 'district_location'] = 'Липецк'
    df_death.loc[index_elec, 'district_location'] = 'Елец'
    print('Определяем первоначальную причину смерти...')
    for col in ['original_reason_a', 'original_reason_b', 'original_reason_v', 'original_reason_g']:
        df_death.loc[df_death[col] == 'True', col] = '1'
        df_death.loc[df_death[col] == 'False', col] = '0'
    df_death = find_original_reason_mkb_group_name(df_death)
    print('Добавляем столбец с ДАТОЙ в формате ГОД-МЕСЯЦ-1число для построения графиков')
    for i in df_death.index:
        year = df_death.loc[i, 'year_death']
        month = df_death.loc[i, 'month_death']
        df_death.loc[i, 'DATE'] = date(year, month, 1)
########################################################################################################################
    # Корректируем даты, чтобы сохранить только полностью завершенный месяц
    dates_ = sorted(df_death['DATE'].unique())[:-1]
    df_death = df_death[df_death.DATE.isin(dates_)]
########################################################################################################################
    if save_to_sql:
        # Сохраняем предобработанные данные в БД
        print('Сохраняем данные в базу данных')
        df_death.to_sql('death_finished', cnx, if_exists='replace', index_label='id')
    if save_to_excel:
        print('Сохраняем данные в файл')
        with pd.ExcelWriter(f'{results_files_path}death_finished_{results_files_suff}.xlsx', engine='openpyxl') as writer:
            df_death.to_excel(writer, sheet_name=f'death_{results_files_suff}', header=True, index=False,
                              encoding='1251')
########################################################################################################################
    print(f'{program} done. elapsed time {datetime.now() - start_time}')
    logging.info('{} done. elapsed time {}'.format(program, (datetime.now() - start_time)))
    return df_death


if __name__ == '__main__':
    logging.basicConfig(filename='logfile.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    df = death_preprocessing(save_to_sql=False, save_to_excel=True)
