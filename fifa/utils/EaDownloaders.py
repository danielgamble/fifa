import requests
from django.utils.text import slugify

from fifa.apps.nations.models import Nation


class Downloader(object):
    def __init__(self):
        self.base_url = 'https://www.easports.com/uk/fifa/ultimate-team/api/fut/item'

    def get_total_pages(self):
        page = requests.get(self.base_url)

        if page.status_code == requests.codes.ok:
            try:
                page_json = page.json()
                return page_json['totalPages']
            except ValueError:
                print("Can't convert page to JSON")
        else:
            raise Exception("Couldn't get total page")

    def get_crawlable_urls(self):
        total_pages = self.get_total_pages()

        return [
            'https://www.easports.com/uk/fifa/ultimate-team/api/fut/item' \
            '?jsonParamObject=%7B%22page%22:{}%7D'.format(
                x
            ) for x in range(1, total_pages + 1)
        ]

    # def get_data(self, mapping, *args, **kwargs):
    #     urls = kwargs.get('failed', self.get_crawlable_urls())
    #     objects = kwargs.get('data', [])
    #     failed = []
    #
    #     for i, url in enumerate(urls):
    #         page = requests.get(url)
    #
    #         if page.status_code == requests.codes.ok:
    #             try:
    #                 print('Got page {}'.format(i))
    #
    #                 page_json = page.json()
    #                 items = page_json['items']
    #
    #                 for item in items:
    #                     ea_item = item[mapping['ea_item']]
    #                     data = {}
    #
    #                     for k, v in mapping['model_mapping'].items():
    #                         data[k] = ea_item[v]
    #
    #                     if mapping['model_images']:
    #                         for k, v in mapping['model_images'].items():
    #                             data[k] = ea_item['imageUrls' if mapping['ea_item'] != 'player' else 'headshot'][v]
    #
    #                     if data not in objects:
    #                         objects.append(data)
    #
    #             except ValueError:
    #                 failed.append(url)
    #
    #                 print("Can't convert page to JSON")
    #         else:
    #             failed.append(url)
    #
    #             print ("Can't convert page {} to JSON".format(i))
    #
    #     print(objects)
    #
    #     if failed:
    #         self.get_data(failed=failed, data=objects)


class NationDownloader(Downloader):
    def build_nation_data(self, *args, **kwargs):
        urls = kwargs.get('failed', self.get_crawlable_urls())
        nations = kwargs.get('data', [])
        failed_urls = []

        for i, url in enumerate(urls):
            page = requests.get(url)

            if page.status_code == requests.codes.ok:
                try:
                    print('Got page {}'.format(i))

                    page_json = page.json()
                    items = page_json['items']

                    for item in items:
                        nation = item['nation']

                        nation_data = {
                            'name': nation['name'],
                            'name_abbr': nation['abbrName'],
                            'ea_id': nation['id'],
                            'image_sm': nation['imageUrls']['small'],
                            'image_md': nation['imageUrls']['medium'],
                            'image_lg': nation['imageUrls']['large'],
                            'image': nation['imgUrl'],
                            'slug': slugify(nation['name'])
                        }

                        if nation_data not in nations:
                            nations.append(nation_data)

                except ValueError:
                    failed_urls.append(url)

                    print("Can't convert page to JSON")
            else:
                failed_urls.append(url)

                print('Url failed: {}'.format(url))

            print([n['name'] for n in nations])

        if failed_urls:
            self.build_nation_data(failed=failed_urls, data=nations)

        return nations

    def build_nations(self, *args, **kwargs):
        data = self.build_nation_data()
        created_nations = []

        for obj in data:
            nation, created = Nation.objects.get_or_create(**obj)

            if created:
                created_nations.append(created)

                print('Created Nation: {}'.format(nation))

        print(len(created_nations))

        return