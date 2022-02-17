from pytest_django.asserts import assertContains

from apps.payments.services import create_payment
from apps.payments.views import payment_processing_view, payment_view, process_notification


def test_process_notification(rf, admin_user):
    payment = create_payment(
        amount="250.00",
        return_url="http://localhost",
        description="-",
        user=admin_user,
    )

    data = (
        """
{
  "type": "notification",
  "event": "payment.succeeded",
  "object": {
    "id": "%s",
    "status": "succeeded",
    "paid": true,
    "amount": {
      "value": "250.00",
      "currency": "RUB"
    },
    "authorization_details": {
      "rrn": "10000000000",
      "auth_code": "000000",
      "three_d_secure": {
        "applied": true
      }
    },
    "created_at": "2021-07-10T14:27:54.691Z",
    "description": "Заказ №72",
    "expires_at": "2021-07-17T14:28:32.484Z",
    "metadata": {},
    "payment_method": {
      "type": "bank_card",
      "id": "22d6d597-000f-5000-9000-145f6df21d6f",
      "saved": false,
      "card": {
        "first6": "555555",
        "last4": "4444",
        "expiry_month": "07",
        "expiry_year": "2021",
        "card_type": "MasterCard",
      "issuer_country": "RU",
      "issuer_name": "Sberbank"
      },
      "title": "Bank card *4444"
    },
    "refundable": false,
    "test": false
  }
}
"""
        % payment.id
    )
    request = rf.post("", data=data, content_type="application/json")
    response = process_notification(request)
    assert response.status_code == 200


def test_payment_view(rf, admin_user):
    request = rf.get("")
    request.user = admin_user
    response = payment_view(request)
    assert response.status_code == 302
    response = payment_view(request)
    assert response.url.endswith("redirect/") is True


def test_payment_processing_view(rf):
    request = rf.get("")
    response = payment_processing_view(request)
    assertContains(response, "обрабатывается")
