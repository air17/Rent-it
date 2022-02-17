from apps.subscriptions.models import PremiumSubscription
from apps.subscriptions.views import premium_view


def test_subscriptions_model(db):
    subscription = PremiumSubscription.objects.first()
    str(subscription).startswith("Subscription")


def test_premium_view(rf, admin_user):
    request = rf.get("")
    request.user = admin_user
    assert premium_view(request).status_code == 200
