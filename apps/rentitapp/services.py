from django.db import IntegrityError

from apps.rentitapp.models import Comment


def process_comment(form, user, ad):
    if not form.is_valid():
        return False
    try:
        Comment.objects.create(
            author=user,
            profile=ad.author,
            advertisement=ad,
            text=form.cleaned_data["comment"],
        )
        return True
    except IntegrityError:
        return False
