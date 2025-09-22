import allure
import functools
import inspect


def allure_from_case(func):
    """
    一個自訂裝飾器，從測試函式的 'case' 參數中
    讀取資料並動態設定 Allure 報告。
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
