from dataclasses import dataclass
from typing import List

import pytest

from test_data.common.base import AllureCase, TestCaseData
from test_data.common.enums import AllureSeverity, PytestMark
from test_data.common.helpers import create_param_from_case
from utils.config_loader import get_config


@dataclass
class UIPurchaseRequest:
    """購買流程 UI 的請求資料 (即表單填寫的內容和商品名稱)"""

    username: str
    password: str
    first_name: str
    last_name: str
    postal_code: str
    product_name: str


@dataclass
class UIPurchaseCase(AllureCase, TestCaseData[UIPurchaseRequest]):
    """購買流程 UI 的測試案例"""

    parent_suite: str = 'UI 情境測試'
    suite: str = '購買成功流程'
    epic: str = 'UI 購買成功流程'
    feature: str = '商品購買'


def generate_ui_purchase_cases() -> List[pytest.param]:
    """
    產生購買流程 UI 的測試情境。
    """
    secrets = get_config()
    default_user = secrets['users']['ui_default_user']
    cases = [
        create_param_from_case(
            UIPurchaseCase(
                severity=AllureSeverity.CRITICAL,
                story='成功購買一件商品',
                sub_suite='購買 - 成功',
                title='UI 成功購買商品',
                description='模擬使用者從登入、瀏覽、加入購物車到完成結帳的完整流程。',
                request=UIPurchaseRequest(
                    username=default_user['account'],
                    password=default_user['password'],
                    first_name='Test',
                    last_name='User',
                    postal_code='12345',
                    product_name='Sauce Labs Bike Light',
                ),
                expected={
                    'success': True,
                    'details': {
                        'product_name': 'Sauce Labs Bike Light',
                        'payment_info': 'SauceCard #31337',
                        'shipping_info': 'Free Pony Express Delivery!',
                        'item_total': '9.99',
                        'tax': '0.80',
                        'final_total': '10.79',
                        'complete_header': 'Thank you for your order!',
                        'complete_text': (
                            'Your order has been dispatched, and will arrive just as fast as the pony can get there!'
                        ),
                    },
                },
                marks=[PytestMark.POSITIVE, PytestMark.UI_SCENARIO],
            ),
            id='ui_purchase_success',
        ),
    ]

    return cases
