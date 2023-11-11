import pandas as pd
from statistics import mean


class FrameForAnalyse:
    def __init__(self, path='', df=pd.DataFrame()):
        if path:
            self.father_object = pd.read_excel(path).fillna('')
        else:
            self.father_object = df

        self.df = self.father_object.copy()
        # self.object['DATE'] = self.object['DATE'].convert_dtypes('str')
        # print(self.object['DATE'].dtypes)
        self.default_items = list(self.df.columns)
        self.axis = 1

        self.extracted = []

    @property
    def items(self):
        return self.default_items

    @items.setter
    def items(self, iter_object):
        self.default_items = iter_object

    @property
    def filters_dict(self):
        return {'<': lambda i, fltr: float(i) < fltr,
                '<=': lambda i, fltr: float(i) <= fltr,
                '>=': lambda i, fltr: float(i) >= fltr,
                '>': lambda i, fltr: float(i) > fltr,
                '=': lambda i, fltr: i == fltr,
                'part': lambda i, prt: prt in i,
                'columns': lambda i, clmns: i in clmns,
                'positions': lambda i, pos: i[0] in pos,
                'nan': lambda i, fltr: pd.isna(i)
                }

    def get_filter_func(self, _filter):
        return self.filters_dict[_filter]

    @property
    def praparation_dict(self):
        return {'columns': {'axis': 1, 'extr': ()},
                'index_values': {'axis': 0, 'extr': list(self.df.index[len(self.df)-2:])},
                'row_values': {'axis': 1, 'extr': ['DATE', 'DAY', 'day_sum', 'sleep_in_time', 'day_sum_in_time']}
                }

    def extract_statistic(self, instructions):
        self.items = {i: self.items[i] for i in self.items if i not in instructions}
        return self.items

    def change_axis_and_prepare_items(self, behavior, stat_extr):
        beh_from_dict = self.praparation_dict[behavior]
        self.axis = beh_from_dict['axis']
        if type(self.items) == list:
            self.items = pd.Series(self.items).to_dict()
        if stat_extr:
            self.extract_statistic(beh_from_dict['extr'])
        return self.axis, self.items

    def filtration(self, filters_list, behavior='columns', stat_extraction=False):
        self.change_axis_and_prepare_items(behavior, stat_extraction)

        for fltr in filters_list:
            dict_object = self.items
            fltr_type, value, filter_logic = fltr[0], fltr[1], fltr[2]
            filter_func = self.get_filter_func(fltr_type)
            if value == 'mean':
                value = self.above_zero_mean(dict_object)

            #key_value_changer = lambda k, v: k if behavior == 'columns' else v

            if filter_logic == 'pos':
                self.items = {i: dict_object[i] for i in dict_object if filter_func(dict_object[i], value)}
            elif filter_logic == 'neg':
                self.items = {i: dict_object[i] for i in dict_object if not filter_func(dict_object[i], value)}

        if behavior == 'columns':
            self.items = [dict_object[i] for i in self.items]

        return {'items': self.items, 'axis': self.axis}

    def remove_statistic(self, frame):
        if self.axis == 1:
            stat_frame = self.df[self.praparation_dict['date']]
            frame = pd.concat([stat_frame, frame], axis=1)
            stat_frame = self.df[self.praparation_dict['row']]
            frame = pd.concat([frame, stat_frame], axis=1)

        if self.axis == 0:
            stat_frame = self.df[self.praparation_dict['cat']:]
            stat_frame = stat_frame.filter(items=frame.columns, axis=1)
            frame = pd.concat([frame, stat_frame], axis=0)
        return frame

    def present_by_items(self, frame, by_previos_conditions=(), remove_stat=False, new_stat=False):
        if by_previos_conditions:
            frame = frame.filter(items=by_previos_conditions['items'], axis=by_previos_conditions['axis'])
        else:
            frame = frame.filter(items=self.items, axis=self.axis)
            # здесь надо бы доработать!!!
            if remove_stat:
                frame = self.remove_statistic(frame)
        return frame

    def above_zero_mean(self, prefilter_d):
        values_above_zero = list(filter(lambda i: i >= 0, prefilter_d.values()))
        return round(mean(values_above_zero), 2)
