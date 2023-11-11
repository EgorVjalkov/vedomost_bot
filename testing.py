import pandas as pd
from colorama import Fore


def does_need_correction(price_frame):
    need_correction = False
    turn_out_dict = lambda i: type(i) == str and '{' in i
    for cat in price_frame:
        if cat != 'category':
            cat_dict = pd.DataFrame(price_frame[cat].to_list(), index=price_frame['category'], columns=[cat])
            cat_dict = cat_dict.to_dict('index')
            wrong_dict = {}
            for index in cat_dict:
                value = cat_dict[index][cat]
                if turn_out_dict(value):
                    try:
                        check = eval(value)
                    except SyntaxError:
                        need_correction = True
                        wrong_dict.update({index: value})
            if wrong_dict:
                wrong_dict = {print(Fore.RED + f'{cat}, {k}, {wrong_dict[k]}' + Fore.RESET) for k in wrong_dict}
            else:
                print(f'{cat} is correct')
    return need_correction


# recipients = ['Egr', 'Lera']
# month = "m23"
# path_to_file = f'months/{month}/{month}.xlsx'
# show_calc = True
#
# prices = pd.read_excel(path_to_file, sheet_name='price')
# check_dicts_in_price_frame(prices)
