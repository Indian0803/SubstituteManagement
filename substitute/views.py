from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
import datetime

from django.core.mail import send_mail


def loginPage(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                if user.is_admin:
                    return redirect('admin:index')
                else:
                    return redirect("teacher_home")
            else:
                messages.warning(request,
                                 "Your email address or password is incorrect")
    else:
        form = LoginForm()
    context = {"form": form}
    return render(request, "substitute/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def teacher_home(request):
    return render(request, "substitute/teacher_home.html")


def teacher_schedule(request):
    return render(request, "substitute/teacher_schedule.html")


def absence_report_day(request):
    yr = Lesson.objects.first().__getattribute__("year")
    yr = yr.split("-")
    year = []
    year.append(int(yr[0]))
    year.append(int(yr[1]))
    if request.method == "POST":
        form = AbsenceDayForm(year, request.POST)
        if form.is_valid():
            day = form.cleaned_data["day"]

            # Validation
            start = Holiday.objects.get(type="Calendar").start
            dt1 = day - start
            end = Holiday.objects.get(type="Calendar").end
            dt2 = day - end
            if (dt1.days < 0) or (dt2.days > 0):
                messages.warning(request,
                                 "The inputted day is not in this year's academic calendar")
                return HttpResponseRedirect(request.path_info)
            elif day.weekday() == 5 or day.weekday() == 6:
                messages.warning(request, "The inputted day is a holiday.")
                return HttpResponseRedirect(request.path_info)

            holidays = Holiday.objects.filter(type="Holiday")
            for holiday in holidays:
                if holiday.end == None:
                    if day == holiday.start:
                        messages.warning(request,
                                         "The inputted day is a holiday.")
                        return HttpResponseRedirect(request.path_info)
                elif holiday.start <= day <= holiday.end:
                    messages.warning(request,
                                     "The inputted day is a holiday.")
                    return HttpResponseRedirect(request.path_info)

            # Get schedule
            if dt1.days % 14 <= 6:
                week = "Week 1"
            else:
                week = "Week 2"

            for holiday in holidays:
                if holiday.end != None:
                    dt = holiday.end - holiday.start
                    if (dt.days + 1) >= 7 and holiday.start < day:
                        if 6 <= dt.days % 14 <= 8:
                            if week == "Week 1":
                                week = "Week 2"
                            else:
                                week = "Week 1"

            days = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']
            d = days[day.weekday()]

            lessons = tuple(Lesson.objects.filter(
                teacher=request.user, day=d+" ("+week+")").values_list('id', 'period').order_by('period'))
            request.session['lessons'] = lessons
            request.session['day'] = day.strftime("%#d %B, %Y")
            return redirect("absence_report_period")

        # user = User.objects.get(id=request.user.id)
        # lessons = []
        # monday1 = Lesson.objects.filter(teacher=user, day="Monday (Week 1)").order_by('period')
        # tuesday1 = Lesson.objects.filter(teacher=user, day="Tuesday (Week 1)").order_by('period')
        # wednesday1 = Lesson.objects.filter(teacher=user, day="Wednesday (Week 1)").order_by('period')
        # thursday1 = Lesson.objects.filter(teacher=user, day="Thursday (Week 1)").order_by('period')
        # friday1 = Lesson.objects.filter(teacher=user, day="Friday (Week 1)").order_by('period')
        # monday2 = Lesson.objects.filter(teacher=user, day="Monday (Week 2)").order_by('period')
        # tuesday2 = Lesson.objects.filter(teacher=user, day="Tuesday (Week 2)").order_by('period')
        # wednesday2 = Lesson.objects.filter(teacher=user, day="Wednesday (Week 2)").order_by('period')
        # thursday2 = Lesson.objects.filter(teacher=user, day="Thursday (Week 2)").order_by('period')
        # friday2 = Lesson.objects.filter(teacher=user, day="Friday (Week 2)").order_by('period')
    # When there are no classes

    form = AbsenceDayForm(year=year)

    context = {"form": form}
    return render(request, "substitute/absence_report_day.html", context)


def absence_report_period(request):
    # lesson_list = ["Period 1", "Period 2", "Period 3", "Period 4",
    #                "Period 5", "Period 6", "Recess", "Lunch 1", "Lunch 2", "Lunch 3"]
    lesson_list = ["", ]
    lessons = request.session.get("lessons")
    for lesson in lessons:
        lesson_list.append(lesson[1])
    day = request.session.get("day")
    if request.method == "POST":
        form = AbsenceForm(lessons, request.POST)
        formset = MessageFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            day = Lesson.objects.get(id=lessons[0][0]).day
            sub = SubstituteSchedule.objects.get(day=day)
            periods = form.cleaned_data["period"]
            messages = formset.cleaned_data

            for i in range(len(lessons)):
                try:
                    message = messages[i]['message']
                except KeyError:
                    continue
                lesson = lessons[i][1]
                if "Period 1" == lesson:
                    teachers = list(sub.period_one.all())
                elif "Period 2" == lesson:
                    teachers = list(sub.period_two.all())
                elif "Period 3" == lesson:
                    teachers = list(sub.period_three.all())
                elif "Period 4" == lesson:
                    teachers = list(sub.period_four.all())
                elif "Period 5" == lesson:
                    teachers = list(sub.period_five.all())
                elif "Period 6" == lesson:
                    teachers = list(sub.period_six.all())
                elif lesson == "Recess":
                    teachers = list(sub.morning_recess.all())
                elif lesson == "Lunch 1":
                    teachers = list(sub.lunch_one.all())
                elif lesson == "Lunch 2":
                    teachers = list(sub.lunch_two.all())
                elif lesson == "Lunch 3":
                    teachers = list(sub.lunch_three.all())

                if not len(teachers) == 1:
                    min_count = 99999
                    min = None
                    mins = []
                    for teacher in teachers:
                        if min_count > teacher.count:
                            min_count = teacher.count
                            min = teacher
                        elif min_count == teacher.count:
                            if not mins:
                                mins.append(min)
                            mins.append(teacher)
                else:
                    min = teachers[0]

                # fixxxxxxxxxxxxxxxxxx
                # finding teacher based on class/department and whether they're absent

                send_mail(
                    'Substitute Request',
                    'Teacher: ' + request.user.first_name + " " + request.user.last_name +
                    "\nDay: "+request.session.get("day")+"\nPeriod: "+lesson+"\nMessage: "+message+"\n\nIf you are available, please click this url to confirm." +
                    "saintmaur.pythonanywhere.com/confirm/"+str(request.user.id) +
                    "\nIf you are unavailable, please click this url.",
                    'rkawamura0483@gmail.com',
                    ['Indiankawamura@gmail.com'],
                    fail_silently=False,
                )
                sublesson = Lesson.objects.get(
                    teacher=request.user, day=day, period=lesson)
                days = request.session.get("day").split(" ")
                date = datetime.date(days[0], days[1][:-1], days[2])
                Substitute.objects.create(
                    lesson=sublesson, teacher=request.user, date=date, verified=False)
                return redirect("teacher_home")

    form = AbsenceForm(lessons)
    formset = MessageFormSet()
    context = {"form": form, 'formset': formset,
               'day': day, 'lesson_list': lesson_list}
    return render(request, "substitute/absence_report_period.html", context)


def confirm(request, pk):
    teacher = Teacher.objects.get(id=pk)
    subsitutes = Substitute.objects.filter(teacher=teacher)
    for sub in subtitutes:
        sub.verified = True
        sub.save()
    return render(request, confirm.html)


def deny(request, pk):

    return render(request, confirm.html)
