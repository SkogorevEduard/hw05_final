from django.core.paginator import Paginator

COUNT: int = 10


def paginate(request, data_list):
    '''Пагинатор постов.'''
    paginator = Paginator(data_list, COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
