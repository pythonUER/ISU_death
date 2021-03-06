# Предобработка исходных данных, получаемых от МедСофт
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pandas as pd

from connect_PostGres import cnx
from ISU_death_functions import make_day_week_month_year_death, calculate_death_age
from ISU_death_functions import calculate_age_group, calculate_employee_group, make_mkb, make_address
from ISU_death_functions import find_original_reason_mkb_group_name
from ISU_death_lists_dict import results_files_path, results_files_suff, column_name_type_death_finished

monthdelta = -3


def calc_last_date(monthdelta):
    return date(date.today().year, date.today().month, 1) + relativedelta(months=monthdelta)


def delete_record(monthdelta):
    with cnx.connect() as connection:
        connection.execute(f"DELETE from death_finished WHERE date_death >= '{calc_last_date(monthdelta)}'")


def death_preprocessing_three_month(save_to_sql=True, save_to_excel=False):
    start_time = datetime.now()
    program = 'death_preprocessing'
    logging.info(f'{program} started')
    print(f'{program} started')

    query = f"SELECT sex, birth, death, address_full, at_death,  reason_a, \
                          original_reasons_a, reason_b, original_reasons_b, reason_c, original_reasons_c, reason_d, \
                          original_reasons_d, reason_2d FROM death WHERE death >= '{calc_last_date(monthdelta)}'"
    df_death = pd.read_sql_query(query, cnx)
    df_death.columns = ['Пол', 'Дата рождения', 'Дата смерти', 'Место жительства', 'Место смерти',
                        'Причина а) КОД МКБ', 'Является первоначальной а)', 'Причина б)', 'Является первоначальной б)',
                        'Причина в)', 'Является первоначальной в)', 'Причина г)', 'Является первоначальной г)',
                        'Причина II (д)']
    print('Обрабатываем даты рождения и смерти...')
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
    df_death = df_death.drop(columns=['Место жительства', 'Место смерти'])
    df_death.columns = ['gender', 'date_born', 'date_death',
                        'reason_a', 'original_reason_a', 'reason_b', 'original_reason_b', 'reason_v',
                        'original_reason_v', 'reason_g', 'original_reason_g', 'reason_d',
                        'day_death', 'week_death', 'month_death', 'year_death',
                        'age_death', 'age_group_death', 'employable_group',
                        'mkb_name_a', 'mkb_group_name_a', 'mkb_name_b', 'mkb_group_name_b', 'mkb_name_v',
                        'mkb_group_name_v', 'mkb_name_g', 'mkb_group_name_g', 'mkb_name_d', 'mkb_group_name_d',
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
        df_death.loc[i, 'date_period'] = date(year, month, 1)
########################################################################################################################
    # Корректируем даты, чтобы сохранить только полностью завершенный месяц
    dates_ = sorted(df_death['date_period'].unique())[:-1]
    df_death = df_death[(df_death.date_period.isin(dates_)) & (df_death.year_death >= 2017)]
    df_death.index = [x for x in range(1, len(df_death)+1)]
########################################################################################################################
    if save_to_sql:
        print('Сохраняем данные в базу данных')
        delete_record(monthdelta)
        df_death.to_sql('death_finished', cnx, if_exists='append', index=False,
                        # dtype=column_name_type_death_finished
                        )
    if save_to_excel:
        print('Сохраняем данные в файл')
        with pd.ExcelWriter(f'{results_files_path}death_finished_{results_files_suff}.xlsx', engine='openpyxl') as writer:
            df_death.to_excel(writer, sheet_name=f'death_{results_files_suff}', header=True, index=False,
                              encoding='1251')
########################################################################################################################
    print(f'{program} done. elapsed time {datetime.now() - start_time}')
    logging.info('{} done. elapsed time {}'.format(program, (datetime.now() - start_time)))
    return df_death
########################################################################################################################


if __name__ == '__main__':
    logging.basicConfig(filename='logfile.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    df = death_preprocessing_three_month(save_to_sql=True, save_to_excel=True)

