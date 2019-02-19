import ipdb
import copy
import xml.etree.ElementTree as ET
from temp.const import *
from temp.exceptions import *


class AnswearParser:
    def __init__(self, path, file_name):
        self._tree = ET.parse(os.path.join(path + '/' + file_name))
        self._root = self._tree.getroot()

        self.partner_name = self._root[0][0].text.lower()

        if self.partner_name != PARTNERS[0]:
            raise HaveNoShuchPartner

        partner_categories = self._root[0][4].findall('category')
        partner_offers = self._root[0][5].findall('offer')

        self.male_categories = self.get_male_categories(partner_categories)
        self.categories = copy.deepcopy(NAMES)
        self.items = self.get_items(partner_offers)

    def get_male_categories(self, data):
        men = []
        women = []

        for category in data:
            if "ОН" in category.text:
                men.append(int(category.attrib['id']))
            elif "ОНА" in category.text:
                women.append(int(category.attrib['id']))

        categories = {"Мужской": men, "Женский": women}

        return categories

    def items_to_categories(self, items):
        counter = 0
        for name in self.categories.keys():
            for item in items:
                if name.lower() in item['name'].lower():
                    self.categories[name].append(item['id'])
                    counter += 1
        print(counter)

    def parse_description(self, strings):
        sep_string = strings.split('\n')[0].split('.')

        if sep_string[1]:
            description = '\n'.join([sep_string[0], sep_string[1]])
        else:
            description = sep_string[0]

        return description


    def get_items(self, data):
        result = []

        for offer in data:
            item = {}

            item['id'] = offer.attrib['id']

            if int(offer[1].text) in self.male_categories['Мужской']:
                item['male'] = True
            elif int(offer[1].text) in self.male_categories['Женский']:
                item['male'] = False
            else:
                continue

            for line in offer:
                if line.tag == 'description':
                    item[line.tag] = self.parse_description(line.text)
                    continue
                if line.tag == 'barcode':
                    continue
                item[line.tag] = line.text

            result.append(item)

        return result


if __name__ == "__main__":
    data = []
    for file_name in FIELLIST:
        answear_obj = AnswearParser(ABSPATH, file_name=file_name)
        answear_obj.items_to_categories(answear_obj.items)
        data.append(answear_obj)
    ipdb.set_trace()

# data: list with AnswearParser objects.
# to get items: obj = data[0] or obj = data[1]
# obj.items ===> {'id': 'SS17-LGM024-00X',
#                   'male': True,
#                   'category_id': '2734',
#                   'currencyId': 'UAH',
#                   'description': 'Короткие носки из коллекции adidas Originals\n
#                                   Модель выполнена из эластичного материала',
#                   'name': 'adidas Originals - Короткие носки',
#                   'oldprice': '329.00',
#                   'picture': 'https://img.ans-media.com/...66.jpg',
#                   'price': '149.00',
#                   'url': 'https://ad.admitad.com/g/h29o15jdr5B8'}