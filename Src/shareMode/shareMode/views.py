from django.shortcuts import render
from django.views.generic.base import View
import os

class HomePage(View):
    def get(self, request):
        path = "/Users/Lavender/Desktop/15112F17_Term_Project_ColorfulNotes/Src/shareMode/static/gallery"
        images = os.listdir(path)
        print(images)
        return render(request, 'index.html', {'images': images})