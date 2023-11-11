import datetime


class PriceMarkCalc:
    def __init__(self, result='', condition='', date=''):
        self.comparison_dict = {'<': lambda r, y: r < y,
                                '<=': lambda r, y: r <= y,
                                '>=': lambda r, y: r >= y,
                                '>': lambda r, y: r > y,
                                '!=': lambda r, y: r != y,
                                '=': lambda r, y: r == y}

        if '{' in condition:
            for operator in self.comparison_dict:
                if operator in condition:
                    self.comparison_flag = True
                    break
                else:
                    self.comparison_flag = False
            condition = eval(condition)

        self.result = result
        self.condition = condition

        self.price = 0.0

        self.date = datetime.date.today() if date == 'DATE' or not date else date

        #print(self.result, type(result), self.condition)

    def prepare_result(self):
        if ':' in self.result:
            time = [int(i) for i in self.result.split(':')]
            time = datetime.time(*time)
            self.result = datetime.datetime.combine(self.date, time)
            if self.result.hour < 8:
                self.result += datetime.timedelta(days=1)

        else:
            if self.result not in self.condition:
                try:
                    self.result = float(self.result)
                except ValueError:
                    return self.result

        return self.result

    def get_price_if_datetime(self):
        for k in self.condition:
            if '.' in k:
                inner_condition = k.split('.')
                if inner_condition[0] in self.comparison_dict:
                    comparison_operator = inner_condition[0]
                    comparison_value = datetime.time(int(inner_condition[1]))
                    comparison_value = datetime.datetime.combine(self.date, comparison_value)
                    if comparison_value.hour < 8:
                        comparison_value += datetime.timedelta(days=1)
                    #print(self.result, comparison_value)

                    inner_condition = self.comparison_dict[comparison_operator](self.result, comparison_value)
                    delta = 0

                    if inner_condition:
                        price_modifier = self.condition[k]
                        #print(comparison_operator, comparison_value, price_modifier)
                        if type(price_modifier) == int:
                            self.price += price_modifier
                            per_minute_cond = '0*'
                        elif '+' in price_modifier:
                            price_modifier = price_modifier.split('+')
                            self.price += float(price_modifier[0])
                            per_minute_cond = price_modifier[1]
                        else:
                            per_minute_cond = price_modifier

                        if not delta:
                            if comparison_value > self.result:
                                delta = (comparison_value - self.result).seconds / 60
                            else:
                                delta = (self.result - comparison_value).seconds / 60
                        else:
                            delta = 60

                        multiplic = float(per_minute_cond.replace('*', ''))
                        self.price += delta * multiplic
                        #print(k, self.condition[k], inner_condition, self.price, '\n')
    # limiting
                    self.price = 200 if self.price > 200 else self.price
        return self.price

    def get_price_if_comparison_logic(self):
        for i in self.condition:
            if '.' in i:
                operator, value = tuple(i.split('.'))
                if self.comparison_dict[operator](float(self.result), int(value)):
                    self.price = self.condition[i]
                    break
        return self.price

    def get_price_if_multiply(self, condition):
        multiplicator = float(condition.replace('*', ''))
        return float(self.result) * multiplicator

    def get_price_if_complex_result(self):
        key, value = self.result[0], self.result[1:]
        result_d_by_key = self.condition[key]
        #print(result_d_by_key)
        for i in result_d_by_key:
            if value in i:
                self.price = float(result_d_by_key[i])
        return self.price

    def get_price(self):
        self.prepare_result()
        #print(self.result, self.condition)

        if self.result in self.condition:
            self.price = self.condition[self.result]# done

        else:
            if self.comparison_flag:
                if type(self.result) == datetime.datetime:
                    self.get_price_if_datetime() # done
                else:
                    self.get_price_if_comparison_logic()# done

            else:
                self.get_price_if_complex_result()# done

        if '*' in str(self.price):
            self.price = self.get_price_if_multiply(self.price)# done

        return self.price

    def prepare_named_result(self, recipient): # результат по литере
        r_litera = recipient[0]
        #print(self.result)
        if isinstance(self.result, str):
            comp_result_dict = {i[0]: i[1:] for i in self.result.split(',')}
            numeric_values = [int(comp_result_dict[i]) for i in comp_result_dict if comp_result_dict[i].isnumeric()]
            #print(numeric_values)
            if r_litera not in comp_result_dict:
                if sum(numeric_values) > 0:
                    self.result = 'wishn`t'
            else:
                if comp_result_dict[r_litera] == '0' and sum(numeric_values) > 0:
                    self.result = 'wishn`t'
                else:
                    self.result = comp_result_dict[r_litera]

        return self.result


#results = ['L1', 'E1', 'L22:00,Ecan`t', 'EF,LF', 'E1,L0']
#
#for i in results:
#   cc = PriceMarkCalc(result=i)
#   cc.prepare_named_result('Lera')
#   print(cc.result)
#   print()

# cc = PriceMarkCalc('+F', '{"+": {"CDIF": 50, "P": 0}, "-": {"CDIF": 0, "P": -50}}')
#cc = PriceMarkCalc('21:50', '{"<.22": "20+1*", "<.23": 0, ">=.23": "-2*"}')
#cc = PriceMarkCalc('22:40', '{"<.22": "20+1*", ">=.22": "-0.5*", ">.23": "-2*"}')
# cc = PriceMarkCalc(4.0, '10*')
# cc = PriceMarkCalc('23:00', '{"<.22": "3*", "<.23": "2*", ">.23": 0}')
# cc = PriceMarkCalc('4', '10*')
# cc = PriceMarkCalc('1', '{1: 50, 0: 0}')
# cc = PriceMarkCalc(result=True)
# cc = PriceMarkCalc(4.0, '{">=.4": 50, "<.4": 0}')
#print(cc.get_price())


