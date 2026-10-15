from typing import TypedDict


class SupportState(TypedDict, total=False):
    message: str
    intent: str
    order_result: str
    policy_result: str
    answer: str
