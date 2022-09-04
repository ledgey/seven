
from django.shortcuts import render
from django.views import View

import random


csselement = """.cont .drip:nth-child(%d){
  border-color:black;
  height:%s%%;
  width:%s%%;
  animation-delay: -%ss;
  background:#4E2A2A;

  margin-top: 20px;
  left:%s%%;
  margin-left:60px;
}

"""

css = []



for i in range(1, 101):
    (hw, d, l) = (random.uniform(0, 1), random.uniform(0, 20), random.uniform(2,10))
    css.append(csselement % (i, hw, hw, d, l))




class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='index.html')

class Coming(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='coming.html')


class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html', {'css_string_list': css})

