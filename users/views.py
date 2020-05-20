from django.views.generic import CreateView
from django.urls import reverse_lazy

#  импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # где login — это параметр "name" в path()
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
