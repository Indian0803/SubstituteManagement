from django.core.mail import send_mail
Substitute.objects.get()
send_mail(
    'Substitute Request',
    'Teacher: ' + request.user.first_name + " " + request.user.last_name +
    "\nDay: "+day+"\nPeriod: "+lesson+"\nMessage: "+message,
    'rkawamura0483@gmail.com',
    ['Indiankawamura@gmail.com'],
    fail_silently=False,
)
