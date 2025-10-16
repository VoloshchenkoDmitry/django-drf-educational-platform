import stripe
from django.conf import settings
from materials.models import Course
from .models import Payment

# Импортируем конфигурацию Stripe
from config.stripe_config import STRIPE_API_KEY

# Настройка Stripe
stripe.api_key = STRIPE_API_KEY


def create_stripe_product(course: Course):
    """
    Создание продукта в Stripe
    """
    try:
        product = stripe.Product.create(
            name=course.title,
            description=course.description or "Курс обучения",
            metadata={
                'course_id': course.id,
                'course_title': course.title
            }
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


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str, user_email: str):
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
            customer_email=user_email,
            metadata={
                'user_email': user_email
            }
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
        # Проверяем доступность Stripe API
        if not stripe.api_key or stripe.api_key.startswith('sk_test_default'):
            raise Exception("Stripe API ключ не настроен. Пожалуйста, настройте STRIPE_API_KEY в переменных окружения.")

        # Создаем продукт в Stripe
        product = create_stripe_product(course)

        # Создаем цену в Stripe (сумма в копейках)
        amount_rub = int(course.price * 100) if course.price else 100000  # 1000 руб по умолчанию
        price = create_stripe_price(product.id, amount_rub)

        # Создаем сессию оплаты
        success_url = f"{base_url}/api/payments/success/"
        cancel_url = f"{base_url}/api/payments/cancel/"

        session = create_stripe_checkout_session(
            price.id,
            success_url,
            cancel_url,
            user.email
        )

        # Создаем запись о платеже в нашей системе
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=amount_rub / 100,  # Конвертируем обратно в рубли
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            payment_url=session.url,
            status='pending'
        )

        return payment

    except Exception as e:
        raise Exception(f"Ошибка в процессе оплаты: {str(e)}")


def update_payment_status(session_id: str):
    """
    Обновление статуса платежа на основе данных из Stripe
    """
    try:
        session = get_stripe_session_status(session_id)
        payment = Payment.objects.get(stripe_session_id=session_id)

        if session.payment_status == 'paid':
            payment.status = 'paid'
            payment.stripe_payment_intent_id = session.payment_intent
        elif session.payment_status == 'unpaid':
            payment.status = 'failed'
        else:
            payment.status = 'pending'

        payment.save()
        return payment

    except Payment.DoesNotExist:
        raise Exception("Платеж не найден")
    except Exception as e:
        raise Exception(f"Ошибка обновления статуса платежа: {str(e)}")