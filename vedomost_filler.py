import pandas as pd
import numpy as np
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
from VedomostCell import VedomostCell
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок
# задроч с путем надо подумать как его слеоать!
# хрень с классом Сell


ff = FrameForAnalyse()


class VedomostFiller:
    def __init__(self, path='', recipient='', behavior=None):
        self.path_to_mother_frame = path
        self.md_instrument = cl.MonthData()

        # поле переменных для работы функций
        self.mother_frame = pd.DataFrame()
        self.prices = pd.DataFrame()
        self.r_vedomost = pd.DataFrame()

        self.day_row = pd.DataFrame()
        self.day_row_index = None
        self.recipient = recipient
        self.r_cats_ser_by_positions = pd.Series()
        self.cells_df = pd.DataFrame()
        self.behavior = behavior

        self.active_cell = None

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @ property
    def private_sleeptime_category(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @ property
    def private_siesta_category(self):
        return f'{self.recipient[0].lower()}:siesta'

    def get_mother_frame_and_prices(self, path_to_mother_frame=None):
        if path_to_mother_frame:
            self.path_to_mother_frame = path_to_mother_frame
        self.mother_frame = self.md_instrument.load_and_prepare_vedomost(self.path_to_mother_frame)
        self.prices = self.md_instrument.get_price_frame(self.path_to_mother_frame)

    def refresh_day_row(self):
        self.day_row = pd.DataFrame()
        self.day_row_index = None
        self.r_cats_ser_by_positions = pd.Series()
        self.cells_df = pd.DataFrame()
        self.active_cell = None

    def get_r_name_and_limiting(self, r_name: str, behavior: str):
        self.recipient = r_name
        self.md_instrument.vedomost = self.mother_frame
        self.behavior = behavior
        self.r_vedomost = self.md_instrument.limiting(behavior, self.recipient)

    @property
    def days(self):
        days = self.r_vedomost['DATE'].to_dict()
        if self.behavior:
            if self.behavior == 'for filling':
                days = {i: days[i] for i in days if days[i] <= datetime.date.today()}

            elif self.behavior == 'for correction':
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                categories_f = self.r_vedomost.get(
                    [cat for cat in self.r_vedomost if cat.islower()])

                days_index = [i for i in days if days[i] in [yesterday, today]] #находим индекс вчера и сегодня
                days_index = [i for i in days_index                         # проверяем по индексу
                              if not all(categories_f.loc[i].map(pd.isna))] # нужно ли что то корректированть

                days = {i: days[i] for i in days_index}

        days = {datetime.date.strftime(days[d], '%d.%m.%y'): d
                for d in days}
        return days

    @property
    def changed_date(self):
        date = self.day_row.date.at[self.day_row_index, 'DATE']
        date = datetime.date.strftime(date,  '%d.%m.%y')
        return date

    def change_the_day_row(self, date_form_tg):
        self.day_row_index = self.days[date_form_tg]
        self.md_instrument.vedomost = self.r_vedomost.loc[self.day_row_index:self.day_row_index]
        self.day_row = self.md_instrument
        self.day_row.get_frames_for_working()
        return self.day_row

    @property
    def r_positions(self):
        r = cl.Recipient(self.recipient, self.day_row.date)
        r.get_and_collect_r_name_col(self.day_row.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(self.day_row.accessory['PLACE'], 'place')
        r.get_and_collect_r_name_col(self.day_row.accessory['DUTY'], 'duty')
        r.get_with_children_col()
        r.get_r_positions_col()
        return r.mod_data.at[self.day_row_index, 'positions']

    def filtering_by_positions(self):
        if not self.day_row.vedomost.empty:
            filtered = [i for i in self.day_row.categories.columns
                        if i[0] in self.r_positions]
            self.r_cats_ser_by_positions = \
                self.day_row.categories.loc[self.day_row_index][filtered]
        return self.r_cats_ser_by_positions

    def get_cells_df(self, category_name=''):
        #self.r_cats_ser_by_positions = self.r_cats_ser_by_positions.replace('!', np.nan)
        #print(self.r_cats_ser_by_positions)
        if category_name:
            self.active_cell = category_name
            cell = VedomostCell(self.prices,
                                self.recipient,
                                name=category_name,
                                value=np.nan) # при выборе ячейки вручную, ее старое стирается
            self.cells_df[cell.cat_name] = cell.extract_cell_data()

        else:
            non_filled = self.r_cats_ser_by_positions.to_dict()
            for cat in non_filled:
                cell = VedomostCell(self.prices,
                                    self.recipient,
                                    name=cat,
                                    value=non_filled[cat])
                if self.behavior == 'for filling':
                    if cell.can_be_filled:
                        # print(cell.name, cell.old_value)
                        # print(cell.can_be_filled)
                        self.cells_df[cell.cat_name] = cell.extract_cell_data()

                else:
                    if cell.can_be_corrected:
                        self.cells_df[cell.cat_name] = cell.extract_cell_data()

        return self.cells_df

    @property
    def cell_names_list(self):
        non_filled_list = []
        if not self.cells_df.empty:
            if self.behavior == 'for filling':
                non_filled = self.cells_df.loc['new_value'].map(lambda v: v is None)
                non_filled_list = [i for i in non_filled.index if non_filled[i]]
            else:
                non_filled_list = list(self.cells_df.columns)
                # вот здесь коллизия: нужно решить как сделать: если я делаю мануальное, то у меня заполняется селл_намес
                # лист, а значит пробиается флаг на полное заполнение, ставится ложная метка! нужно фиксить
        return non_filled_list

    @property
    def already_filled_cell_names_dict(self):
        filled = []
        if not self.cells_df.empty:
            old = self.cells_df.loc['old_value'].to_dict()
            new = self.cells_df.loc['new_value'].to_dict()
            new = {i: new[i] for i in new if new[i]}
            filled = {i: new[i] for i in new if new[i] != old[i]}
        return filled

    @property
    def filled_cells_list_for_print(self):
        return [f'{i} - "{self.already_filled_cell_names_dict[i]}"'
                for i in self.already_filled_cell_names_dict]

    @property
    def recipient_all_filled_flag(self):
        if not self.cell_names_list:
            return True
        else:
            return False

    def change_a_cell(self, name_from_tg):
        self.active_cell = name_from_tg
        if self.behavior == 'for correction':
            old_value = self.cells_df.at['old_value', self.active_cell]
            print(old_value)
            cell_for_correction = VedomostCell(self.prices,
                                               self.recipient,
                                               name=self.active_cell,
                                               value=old_value)
            cell_for_correction.revert_value()
            self.cells_df[self.active_cell] = cell_for_correction.extract_cell_data()

        return self.active_cell

    def fill_the_cell(self, value_from_tg):
        if value_from_tg == 'не мог':
            value_from_tg = 'can`t'
        elif value_from_tg == 'забыл':
            value_from_tg = '!'
        cell_ser = self.cells_df[self.active_cell]

        if cell_ser['is_filled']:
            self.cells_df.at['new_value', self.active_cell] = \
                    f'{cell_ser["old_value"]},{self.recipient[0]}{value_from_tg}'

        else:
            if cell_ser['has_private_value']:
                self.cells_df.at['new_value', self.active_cell] = \
                    f'{self.recipient[0]}{value_from_tg}'
            else:
                self.cells_df.at['new_value', self.active_cell] = value_from_tg

    def change_done_mark(self):
        # print(self.mother_frame.loc[self.day_row_index]['DONE'])
        if self.recipient_all_filled_flag:
            if pd.notna(self.mother_frame.at[self.day_row_index, 'DONE']):
                self.mother_frame.at[self.day_row_index, 'DONE'] = 'Y'
            else:
                self.mother_frame.at[self.day_row_index, 'DONE'] = self.recipient[0]
        # print(self.mother_frame.loc[self.day_row_index]['DONE'])

    def write_day_data_to_mother_frame(self):
        for c in self.already_filled_cell_names_dict:
            self.day_row.vedomost.at[self.day_row_index, c]\
                = self.already_filled_cell_names_dict[c]

        self.mother_frame[self.day_row_index:self.day_row_index+1]\
            = self.day_row.vedomost

    def count_day_sum(self):
        pass

    def save_day_data(self):
        with pd.ExcelWriter(
                self.path_to_mother_frame,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='replace'
        ) as mf_writer:
            self.mother_frame.to_excel(mf_writer, sheet_name='vedomost', index=False)




if __name__ == '__main__':
    month = 'nov23'
    #pd.reset_option('display.max.columns')
    filler = VedomostFiller(path=f'months/{month}/{month}.xlsx')
    filler.get_mother_frame_and_prices()
    filler.get_r_name_and_limiting('Egr', 'for filling')
    #print(filler.r_vedomost)
    print(filler.days)

    filler.change_the_day_row('11.11.23')
    filler.filtering_by_positions()
    # print(filler.r_cats_ser_by_positions)

    filler.get_cells_df()
    cell = 'e:plan'
    print(filler.cells_df[cell])
    filler.change_a_cell(cell)
    filler.fill_the_cell('G')
    print(filler.cells_df[cell])
    print(filler.already_filled_cell_names_dict)
    print(filler.cell_names_list)
    print(filler.recipient_all_filled_flag)
    #filler.write_day_data_to_mother_frame()
    # filler.change_done_mark()
    # filler.save_day_data()
#    print(filler.day_row.vedomost)
#    print(filler.mother_frame.loc[14:15])
#