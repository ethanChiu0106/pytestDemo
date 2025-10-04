"""提供與 Allure 報告相關的工具函式。"""
import allure
import functools
import inspect


def allure_from_case(func):
    """一個裝飾器，用於從測試案例的 `case` 物件動態設定 Allure 報告

    此裝飾器會檢查被裝飾的測試函式，並從其 `kwargs` 中尋找名為 `case` 的參數
    如果 `case` 物件存在，裝飾器會讀取其 `title` 和 `description` 屬性，
    並用它們來動態設定 Allure 報告的標題和描述。

    使用範例:
        @allure_from_case
        @pytest.mark.parametrize('case', [some_case_object])
        def test_something(case):
            ...

    Args:
        func: 被裝飾的測試函式

    Returns:
        經過包裝、具備動態設定 Allure 功能的函式
    """
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            case = kwargs.get('case')
            if case:
                if hasattr(case, 'title'):
                    allure.dynamic.title(case.title)
                if hasattr(case, 'description'):
                    allure.dynamic.description(case.description)
            return await func(*args, **kwargs)
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            case = kwargs.get('case')
            if case:
                if hasattr(case, 'title'):
                    allure.dynamic.title(case.title)
                if hasattr(case, 'description'):
                    allure.dynamic.description(case.description)
            return func(*args, **kwargs)

    return wrapper
