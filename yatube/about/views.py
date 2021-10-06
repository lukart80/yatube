from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):
    """View класс для отображения страницы об авторе."""
    template_name = 'author.html'


class AboutTechView(TemplateView):
    """View класс для отображения страницы о использованных технологиях."""
    template_name = 'tech.html'
