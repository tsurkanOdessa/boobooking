from django.dispatch import Signal
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import logging

logger = logging.getLogger(__name__)

user_registered = Signal()

def handle_user_registered(sender, user, **kwargs):
    user.is_active = False
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://localhost:8000/api/user/activate/?uid={uid}&token={token}"

    logger.info(f"Ссылка активации для {user.email}: {activation_link}")
