
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
    (hw, d, l) = (random.uniform(0, 2), random.uniform(0, 20), random.uniform(0,10))
    css.append(csselement % (i, hw, hw, d, l))

# with open('/Users/craigledgerwood/Documents/seven/sevencoffee/shop/static/shop/dripstyle.css', 'a+') as f:
#     f.write(css)
#     f.close()

# print(f.filename)


class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='index.html')

class Coming(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='coming.html')


class Home(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'test.html', {'css_string_list': css})

class HomeTest(View):
    def get(self, request, *args, **kwargs):
        return render(request,template_name='home4.html')