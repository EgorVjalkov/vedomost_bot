import pandas as pd
import analytic_utilities as au


ff = au.FrameForAnalyse()


class BonusColumn:
    def __init__(self, mark_column, cat_price_column):
        self.name = f'{cat_price_column.name}'
        self.mark_ser = pd.Series(mark_column)

        self.logic = cat_price_column.loc['logic']
        self.interval = int(cat_price_column.loc['N'])
        self.cond = cat_price_column.loc['condition']
        self.pay = float(cat_price_column.loc['bonus'])

        self.mark_bonus_frame = None
        self.output_bonus_ser = self.mark_ser.copy()

    @property
    def tools(self):
        return {'every N': self.every_n_give_a_bonus}

    @property
    def bonus_logic(self):
        flag = True if self.logic else False
        return flag

    @property
    def enough_len(self):
        flag = True if len(self.mark_ser) >= self.interval else False
        return flag

    @property
    def max_bonus_ser(self):
        max_bonus_ser = self.mark_ser.map(lambda i: self.cond)
        max_bonus_ser.name = 'max_mark'
        return max_bonus_ser

    @property
    def not_cant_index(self):
        ff.items = self.mark_ser.to_dict()
        ff.filtration([('=', 'can`t', 'neg')], behavior='index_values')
        return ff.items

    def get_full_name(self):
        if self.cond == 'T':
            self.name += '_bonus'
        else:
            self.name += '_fire'
        return self.name

    def count_a_bonus(self):
        self.get_full_name()
        self.mark_bonus_frame = pd.concat(
            [self.mark_ser,
             self.max_bonus_ser,
             pd.Series(index=self.mark_ser.index, name=self.name)],
            axis=1)
        self.mark_bonus_frame = self.mark_bonus_frame.filter(items=self.not_cant_index, axis=0)

        self.tools[self.logic]('mark', self.name)
        self.tools[self.logic]('max_mark', 'max_bonus')

    def get_remains_list(self, mark_col):
        remains_index_list = []
        if self.cond == 'T':
            remains_dict = self.mark_bonus_frame[mark_col].to_dict()
            last_non_cond = {i: remains_dict[i] for i in remains_dict if remains_dict[i] != self.cond}
            if last_non_cond: # проверка на некондицию
                last_non_cond = max(last_non_cond) # последная некондиция, от нее и будет происходить дробление
                remains_dict = {i: remains_dict[i] for i in remains_dict if i > last_non_cond}

            if remains_dict:
                remains = len(remains_dict) % self.interval
                #print(remains)
                if remains:
                    remains_index_list = list(remains_dict.keys())[-remains:]
        return remains_index_list

    def every_n_give_a_bonus(self, mark_col, bonus_col):
        if bonus_col not in self.mark_bonus_frame.columns:
            self.mark_bonus_frame[bonus_col] = pd.Series()

        remains_list = self.get_remains_list(mark_col)

        counter = 1
        for i in self.mark_bonus_frame.index:
            if self.mark_bonus_frame.at[i, mark_col] == self.cond:
                if counter < self.interval:
                    if i in remains_list and i == remains_list[-1]:
                        #print(f'{remains_list}, {self.pay}/{self.interval}*{len(remains_list)}')
                        # TRUE, но длины не хватит для результата, дробление суммы. ОПЦИЯ бонусов
                        self.mark_bonus_frame.at[i, bonus_col] = round(self.pay / self.interval * len(remains_list), 1)

                    else: # TRUE, резуотат не достигнут, прибавка счетчика
                        self.mark_bonus_frame.at[i, bonus_col] = self.mark_bonus_frame.at[i, mark_col]
                        counter += 1

                else: # TRUE, достгнут результат, начисление бонуса
                    self.mark_bonus_frame.at[i, bonus_col] = self.pay
                    counter = 1

            else: # FALSE, сброс счетчика
                self.mark_bonus_frame.at[i, bonus_col] = self.mark_bonus_frame.at[i, mark_col]
                counter = 1

    def get_bonus_ser_without_statistic(self):
        frame = pd.concat([self.output_bonus_ser, self.mark_bonus_frame[self.name]], axis=1)
        self.output_bonus_ser = frame[self.name].fillna('can`t')
        return self.output_bonus_ser

    def get_bonus_ser_with_statistic(self):
        get_0_if_str = lambda i: 0 if type(i) == str else i
        sum_of_bonus = self.mark_bonus_frame[self.name].map(get_0_if_str).sum()
        sum_of_max = self.mark_bonus_frame['max_bonus'].map(get_0_if_str).sum()
        true_count = round(sum_of_bonus/sum_of_max, 2)
        if sum_of_max < 0:
            true_count = 1.00 - true_count
        stat_ser = pd.Series([true_count, sum_of_bonus])

        self.output_bonus_ser = pd.concat([self.output_bonus_ser, stat_ser], axis=0, ignore_index=True)
        self.output_bonus_ser.name = self.name
        return self.output_bonus_ser


if __name__ == '__main__':
    month = 'oct23'
    cat_name = 'z:teeth'
    mark_column = pd.read_excel(f'output_files/{month}/Lera/{cat_name}.xlsx')['mark']
    cat_price_column = pd.read_excel(f'months/{month}/{month}.xlsx', sheet_name='price', index_col=0).fillna(0)
    cat_price_column = pd.Series(cat_price_column[cat_name])
    bc = BonusColumn(mark_column, cat_price_column)
    if bc.bonus_logic and bc.enough_len:
        bc.count_a_bonus()
        print(bc.mark_bonus_frame)
