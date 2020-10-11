from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from typing import Iterable, List
import requests, json, os, time
from .models import Files

def index(request):
    # return HttpResponse("Hello World! Hello Django :D 23.08.2020nd")
    saved = ApiResources().save_resources()
    saved_info = "There was a problem processing the data!"
    if saved:
        saved_info = "The data has been processed and saved correctly."
    context = {'info': saved_info}
    return render(request, 'load/index.html', context)

class ApiResources():
    api_url = settings.POKE_API
    delimiter = ';'

    def _all_urls(self) -> List[str]:
        url = self.api_url
        urls: list = []
        next = True
        while next:
            response: requests.models.Response = requests.get(url)
            json_data: dict = json.loads(response.content)
            for resource in json_data['results']:
                if json_data['next']:
                    if not json_data['next'] in urls:
                        urls.append(json_data['next'])
                    url = json_data['next']
                else:
                    next = False
        return urls

    def _receive_last_page(self, pages: Iterable[str]) -> str:
        return pages[-1]

    def _receive_last_id(self, last_page_url: str) -> int:
        response: requests.models.Response = requests.get(last_page_url)
        json_data: dict = json.loads(response.content)
        results = json_data['results']
        last_ulr = results[-1]['url']
        splitted_ulr = last_ulr.split('/')
        if not last_ulr[-1] == '/':
            last_id = splitted_ulr[-1]
        else:
            last_id = splitted_ulr[-2]
        return int(last_id)

    def _define_urls_scope(self, last_page_url: str, last_id: int) -> int:
        '''
        last_id = 10157 - this is amount of units in API.
        Because last_id is rather a huge number, let`s assume we want to save time
        and will consider only 10 units
        '''
        # return last_id
        last_id = 10
        scope = range(1, last_id+1)
        units_ulrs = []
        for i in scope:
            units_ulrs.append(settings.POKE_API+str(i))
        return units_ulrs

    def _get_resources(self, last_page_url: str, last_id: int) -> List:
        urls_scope = self._define_urls_scope(last_page_url, last_id)
        units = []
        for url in urls_scope:
            response: requests.models.Response = requests.get(url)
            json_data: dict = json.loads(response.content)
            unit = {}
            for s in json_data['forms']:
                unit['name'] = s['name']

            unit['abilities'] = []
            for s in json_data['abilities']:
                unit['abilities'].append(s['ability']['name'])

            unit['moves'] = []
            for s in json_data['moves']:
                unit['moves'].append(s['move']['name'])

            units.append(unit)
        return units

    def save_resources(self) -> bool:
        last_page_url = self._receive_last_page(self._all_urls())
        last_id: int = self._receive_last_id(last_page_url)
        resources = self._get_resources(last_page_url, last_id)
        csv_file_name = time.strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
        header = ['name', 'abilities', 'moves']
        file_path = settings.CSV_DIR + os.sep + csv_file_name
        list_comma = ','
        with open(file_path, 'w+') as f:
            f.write(self.delimiter.join(header) + '\n')
            for resource in resources:
                row = ''
                print(resource)
                row += resource['name'] + self.delimiter

                row_ability = ''
                for ability in resource['abilities']:
                    row_ability += ability + list_comma
                row += row_ability[:-1] + self.delimiter

                row_moves = ''
                for move in resource['moves']:
                    row_moves += move + list_comma
                row += row_moves[:-1] + self.delimiter

                f.write(row + '\n')
        if os.path.isfile(file_path):
            model_file = Files()
            model_file.name = file_path
            model_file.save()
            return True
        return False
