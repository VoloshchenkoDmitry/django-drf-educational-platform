from rest_framework.pagination import PageNumberPagination


class LessonPaginator(PageNumberPagination):
    page_size = 10  # Количество уроков на странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 50  # Максимальное количество уроков на странице


class CoursePaginator(PageNumberPagination):
    page_size = 5  # Количество курсов на странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 20  # Максимальное количество курсов на странице