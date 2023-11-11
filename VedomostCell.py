import numpy as np
import pandas as pd


class VedomostCell:
    def __init__(self, price_frame, recipient, name='', value=''):
        self.prices = price_frame
        self.r_litera = recipient[0]

        self.name = name
        self.old_value = value
        self.new_value = np.nan

    @property
    def cat_name(self):
        return self.name

    @cat_name.setter
    def cat_name(self, category_name):
        self.name = category_name

    @property
    def old_cat_value(self):
        return self.old_value

    @old_cat_value.setter
    def old_cat_value(self, value):
        self.old_value = value

    @property
    def category_data(self):
        cat_data = self.prices[self.cat_name]
        return cat_data

    @property
    def type(self):
        return self.category_data.loc['type']

    @property
    def description(self):
        descr_list = self.category_data.get(['description', 'hint']).to_list()
        descr_list = [e for e in descr_list if pd.notna(e)]
        return descr_list

    @property
    def keys(self):
        if 'range' in self.type:
            keys = list(eval(self.type))
        elif self.type == 'dict':
            keys = list(eval(self.category_data['PRICE']).keys())
        else:
            keys = ['передать вручную']
        if pd.notna(self.category_data['add_keys']):
            keys.append(self.category_data['add_keys'])
        return keys

    @property
    def is_filled(self):
        return pd.notna(self.old_value)

    @property
    def has_private_value(self):
        return pd.notna(self.category_data['private_value'])

    @property
    def can_append_data(self):
        flag = False
        if self.is_filled and self.r_litera not in self.old_value:
            flag = True
        return flag

    @property
    def can_be_filled(self) -> bool:
        flag = False
        if self.is_filled:  # прoверка на заполненность
            if self.has_private_value: # проверка на возможность иметь несколько значение
                if self.can_append_data:  # проверка на возможность дописывания в яйчейку
                    flag = True
        else:
            flag = True
        return flag

    @property
    def can_be_corrected(self) -> bool:
        return not self.can_be_filled

    def revert_value(self):
        revert_old_value = np.nan  # очистка ячейки в дефолте
        if self.is_filled and self.r_litera in self.old_value:  # очистка записи при наличии записи в ней
            revert_old_value = [i for i in self.old_value.split(',')
                                if self.r_litera not in i]
            revert_old_value = ''.join(revert_old_value)
        self.old_value = revert_old_value

    def extract_cell_data(self):
        cell_data = {
            'keys': self.keys,
            'description': self.description,
            'old_value': self.old_value,
            'is_filled': self.is_filled,
            'has_private_value': self.has_private_value,
            'can_append_data': self.can_append_data,
            'new_value': None
        }
        return pd.Series(cell_data)


#a = np.nan
#print(pd.isna(a))