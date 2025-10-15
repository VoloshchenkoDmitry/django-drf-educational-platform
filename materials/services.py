from django.conf import settings


# Временно закомментируем Stripe для миграций
# stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course):
    """
    Создание продукта в Stripe
    """

    # Временно возвращаем заглушку
    class MockProduct:
        def __init__(self):
            self.id = f"prod_mock_{course.id}"

    return MockProduct()

    # try:
    #     product = stripe.Product.create(
    #         name=course.title,
    #         description=course.description or "Курс обучения",
    #         metadata={
    #             'course_id': course.id,
    #             'type': 'educational_course'
    #         }
    #     )
    #     return product
    # except stripe.error.StripeError as e:
    #     raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(product_id: str, amount: int):
    """
    Создание цены в Stripe
    """

    # Временно возвращаем заглушку
    class MockPrice:
        def __init__(self, product_id):
            self.id = f"price_mock_{product_id}"

    return MockPrice(product_id)

    # try:
    #     price = stripe.Price.create(
    #         product=product_id,
    #         unit_amount=amount,
    #         currency='rub',
    #     )
    #     return price
    # except stripe.error.StripeError as e:
    #     raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str):
    """
    Создание сессии оплаты в Stripe
    """

    # Временно возвращаем заглушку
    class MockSession:
        def __init__(self, price_id):
            self.id = f"sess_mock_{price_id}"
            self.url = "https://example.com/mock-payment"
            self.payment_status = 'unpaid'

    return MockSession(price_id)

    # try:
    #     session = stripe.checkout.Session.create(
    #         payment_method_types=['card'],
    #         line_items=[{
    #             'price': price_id,
    #             'quantity': 1,
    #         }],
    #         mode='payment',
    #         success_url=success_url,
    #         cancel_url=cancel_url,
    #     )
    #     return session
    # except stripe.error.StripeError as e:
    #     raise Exception(f"Ошибка создания сессии оплаты в Stripe: {str(e)}")


def get_stripe_session_status(session_id: str):
    """
    Получение статуса сессии оплаты
    """

    # Временно возвращаем заглушку
    class MockSession:
        def __init__(self, session_id):
            self.id = session_id
            self.payment_status = 'unpaid'

    return MockSession(session_id)

    # try:
    #     session = stripe.checkout.Session.retrieve(session_id)
    #     return session
    # except stripe.error.StripeError as e:
    #     raise Exception(f"Ошибка получения статуса сессии: {str(e)}")


def create_payment_flow(course, user, base_url: str):
    """
    Полный процесс создания платежа
    """
    try:
        from payments.models import Payment

        # Создаем продукт в Stripe
        product = create_stripe_product(course)

        # Создаем цену в Stripe (сумма в копейках)
        amount_rub = int(course.price * 100) if course.price else 100000
        price = create_stripe_price(product.id, amount_rub)

        # Создаем сессию оплаты
        success_url = f"{base_url}/api/lessons/payments/success/"
        cancel_url = f"{base_url}/api/lessons/payments/cancel/"

        session = create_stripe_checkout_session(price.id, success_url, cancel_url)

        # Создаем запись о платеже в нашей системе
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount_rub / 100,
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            payment_url=session.url
        )

        return payment

    except Exception as e:
        raise Exception(f"Ошибка в процессе оплаты: {str(e)}")


def get_test_payment_info():
    """
    Возвращает информацию для тестирования платежей
    """
    test_cards = [
        {
            'number': '4242424242424242',
            'description': 'Успешная оплата'
        },
        {
            'number': '4000000000000002',
            'description': 'Отклоненная карта'
        },
    ]

    return {
        'test_cards': test_cards,
        'default_test_card': test_cards[0],
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_mock'),
        'environment': 'TEST MODE'
    }