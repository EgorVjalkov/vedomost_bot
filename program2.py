import classes as cl
import pandas as pd
from testing import does_need_correction
from analytic_utilities import FrameForAnalyse
from BonusColumn import BonusColumn

recipients = ['Egr', 'Lera']
month = "oct23"

path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True


def main():
    if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

        md = cl.MonthData(path_to_file)
        md.load_and_prepare_vedomost()
        md.get_price_frame()
        md.limiting(limiting='for count')
        md.get_frames_for_working()
        md.fill_na()
        print(md.prices)

        for r_name in recipients:
            # рефакторнуть???
            rename_dict = {'COM': 'children', 'PLACE': 'place', 'DUTY': 'duty'}
            r = cl.Recipient(r_name, md.date)
            r.create_output_dir(f'output_files', month)
            r.get_mod_frame(md.accessory, md.categories, rename_dict)
            r.mod_data.to_excel(f'output_files/{month}/{r_name}/{r_name}_mods.xlsx')
            r.get_r_vedomost(['Egr', 'Lera'], md.categories)
            # fltr = FrameForAnalyse(df=r.cat_data)
            # cat_filter = ('positions', ['a', 'z', 'h'], 'pos')
            # fltr.filtration([cat_filter])
            # for column in fltr.items:
            for column in r.cat_data:
                cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices, r.r_name)
                print(cd.name)
                cd.add_price_column(show_calculation=show_calc)
                cd.add_mark_column(show_calculation=show_calc)
                cd.add_coef_and_result_column(show_calculation=show_calc)

                bc = BonusColumn(cd.cat_frame['mark'], cd.price_frame)
                if bc.bonus_logic and bc.enough_len:
                    bc.count_a_bonus()
                    cd.cat_frame[bc.name] = bc.get_bonus_ser_without_statistic()
                    bc_with_statistic = bc.get_bonus_ser_with_statistic()
                else:
                    bc_with_statistic = pd.Series()

                cd.get_ready_and_save_to_excel(md.date, f'output_files/{month}/{r_name}/{cd.name}.xlsx')
                r.collect_to_result_frame(cd.get_result_col_with_statistic(), bc_with_statistic)
            r.get_day_sum_if_sleep_in_time_and_save(f'output_files/{month}/{r_name}/{r_name}_total.xlsx')


if __name__ == '__main__':
    main()
