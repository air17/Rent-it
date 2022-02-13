from django.db import IntegrityError

from apps.accounts.models import User
from apps.rentitapp.forms import NewComment
from apps.rentitapp.models import Comment, Advertisement


def process_comment(form: NewComment, user: User, ad: Advertisement):
    """Creates and saves a new comment.

    Args:
        form: Comment creation form
        user: Comment author
        ad: commented advertisement

    Returns: True if comment created. False if comment from this author already
    exists or form is not valid.

    """
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
