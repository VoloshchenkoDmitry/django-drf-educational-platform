import stripe
from django.conf import settings
from materials.models import Course

# Настройка Stripe
stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course: Course):
    """
    Создание продукта в Stripe
    """
    try:
        product = stripe.Product.create(
            name=course.title,
            description=course.description or "Курс обучения",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(product_id: str, amount: int):
    """
    Создание цены в Stripe
    """
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount,  # Сумма в копейках
            currency='rub',
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str):
    """
    Создание сессии оплаты в Stripe
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии оплаты в Stripe: {str(e)}")


def get_stripe_session_status(session_id: str):
    """
    Получение статуса сессии оплаты
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка получения статуса сессии: {str(e)}")


def create_payment_flow(course: Course, user, base_url: str):
    """
    Полный процесс создания платежа
    """
    try:
        # Создаем продукт в Stripe
        product = create_stripe_product(course)

        # Создаем цену в Stripe (сумма в копейках)
        amount_rub = int(course.price * 100) if hasattr(course, 'price') else 100000  # 1000 руб по умолчанию
        price = create_stripe_price(product.id, amount_rub)

        # Создаем сессию оплаты
        success_url = f"{base_url}/api/payments/success/"
        cancel_url = f"{base_url}/api/payments/cancel/"

        session = create_stripe_checkout_session(
            price.id,
            success_url,
            cancel_url
        )

        # Создаем запись о платеже в нашей системе
        from .models import Payment
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount_rub / 100,  # Конвертируем обратно в рубли
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            payment_url=session.url
        )

        return payment

    except Exception as e:
        raise Exception(f"Ошибка в процессе оплаты: {str(e)}")