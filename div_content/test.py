from django.core.mail import send_mail

send_mail(
    'Testovací email',
    'Toto je testovací zpráva.',
    'heslo@div.cz',
    ['váš@email.cz'],
    fail_silently=False,
)
