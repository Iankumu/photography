from functools import wraps

from flask import redirect, flash
from flask_login import current_user


def photographer_required(func):
    """
    if used to make sure the the current user is sa photographer
    :param func:
    :return:
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.photographer is None:
            flash("You are not yet registered as a photographer")
            return redirect('photographer_register')
        return func(*args, **kwargs)

    return decorated_view
