
from django.shortcuts import render
from django.views import View


class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='menu.html')

class Coming(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='coming.html')
