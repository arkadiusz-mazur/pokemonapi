from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from typing import Iterable, List
import requests, json, os, time
import glob

def index(request):
    context = {'files': Show().files(), 'file_path': settings.CSV_DIR}
    return render(request, 'show/index.html', context)

class Show():

    def files(self) -> List:
        file_path = settings.CSV_DIR
        return os.listdir(file_path)
