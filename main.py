import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


DATE_RANGE = pd.date_range(start='2022-01-01', end='2024-12-31').tolist()


class KVPair:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'[key: {self.key}, val: {self.value}]'


class DayByDayData(list):
    def __init__(self, source_file, source_dir='data', threshold=0):
        super().__init__()
        with open(f'{source_dir}/{source_file}', 'r') as sf:
            json_data = json.load(sf)
        for key in json_data:
            if json_data[key] > threshold:
                self.append(KVPair(key, json_data[key]))

        self.sort(reverse=True, key=lambda x: x.value)

    def __getitem__(self, key):
        if isinstance(key, str):
            # need better way:
            try:
                return {str(_key.key): _key.value for _key in self}[key]
            except KeyError:
                return 0
        else:
            return super().__getitem__(key)


class DatasetHandler(list):
    def __init__(self, source='data', threshold=0, print_init=False):
        self.card_definitions = CardDefinitions()
        files = os.listdir(source)
        if print_init:
            super().__init__()
            length = len(files)
            for index, file in enumerate(files):
                self.append(DayByDayData(file, threshold=threshold))
                print(f'{index + 1} / {length}')

        else:
            obj_list = [DayByDayData(file, threshold=threshold) for file in files]
            super().__init__(obj_list)

    def get_nth_card(self, n, columns=None, to_df=True):
        if columns is None:
            columns = [n]
        if to_df:
            return pd.DataFrame([record[n].value for record in self], index=DATE_RANGE, columns=columns)
        else:
            return [record[n].value for record in self]

    def get_card_by_id(self, card_id, columns=None, to_df=True):
        if columns is None:
            columns = [card_id]

        if to_df:
            return pd.DataFrame([record[card_id] for record in self], index=DATE_RANGE, columns=columns)
        else:
            return [record[card_id] for record in self]

    def save(self, output_file, dump_dict=None):
        if dump_dict is None:
            dump_dict = {'main': [[y.value for y in x] for x in self]}

        with open(output_file, 'w') as of:
            json.dump(dump_dict, of)


class CardDefinitions(dict):
    def __init__(self, source='card-definitions.txt'):
        with open(source, 'r') as sf:
            json_data = json.load(sf)
        super().__init__(**json_data)

    def get_ids(self, card_name):
        return [key for key in self if self[key]['name'].lower() == card_name.lower()]


def main():
    dh = DatasetHandler(threshold=10, print_init=True)
    df_prices = dh.get_nth_card(50)

    classic_cards = ['wasteland', 'force of will', 'mox diamond', 'sheoldred, the apocalypse']
    for card in classic_cards:
        try:
            card_id = dh.card_definitions.get_ids(card)[-1]
            appendix = dh.get_card_by_id(card_id, columns=[card], to_df=False)

            df_prices.insert(1, card, appendix)

        except IndexError:
            pass

    df_prices.insert(0, 20, dh.get_nth_card(10, to_df=False))
    sns.lineplot(df_prices)

    plt.gcf().autofmt_xdate()
    plt.show()


if __name__ == '__main__':
    main()
