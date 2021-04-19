from rest_framework.pagination import PageNumberPagination

# 分页代码
class StandardPagination(PageNumberPagination):
    # 每页显示个数
    page_size = 1
    # url中默认修改每页个数的参数名
    # 比如http://127.0.0.1:8000/api/snippets/?page=1&page_size=4
    # 就是显示第一页并且显示个数是4个
    # page_size的变量名称默认如下
    page_size_query_param = 'page_size'
    # url中默认是参数名是page下面还是改成page哈
    page_query_param = "page"
    # 每页最大个数不超过100
    max_page_size = 100

    # 自定义数据,
    msg = None

    def paginate_queryset(self, queryset, request, view=None):
        """
        获取分页内容
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        # 重定义错误，默认如果页数page超过分页大小会报错，这里改成超过的话页数变成第一页
        # page_number是传递进来要展示第几页的页数
        try:
            self.page = paginator.page(page_number)
        except Exception as e:
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)