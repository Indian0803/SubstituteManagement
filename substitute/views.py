from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
import datetime
from datetime import date, timedelta
from .decorators import unauthenticated_user

from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

# Restricting authenticated users to access the page


@unauthenticated_user
# Renders login page
def loginPage(request):
    # Receiving input from the user
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # authentication
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

# Logging out user


def logoutUser(request):
    logout(request)
    return redirect("login")

# Restricting unauthenticated users from accessing the page


@login_required(login_url="login")
# Renders home page for teachers
def teacher_home(request):
    # Passing lesson information
    lessons = tuple(Lesson.objects.filter(
        teacher=request.user, day="Wednesday (Week 2)").order_by('period'))
    context = {'lessons': lessons}
    return render(request, "substitute/teacher_home.html", context)
    day = datetime.date.today()
    start = Holiday.objects.get(type="Calendar").start
    dt1 = day - start
    end = Holiday.objects.get(type="Calendar").end
    dt2 = day - end

    # Checking if the given day is before/past the academic calendar
    if (dt1.days < 0) or (dt2.days > 0):
        lessons = None
        context = {'lessons': lessons}
        return render(request, "substitute/teacher_home.html", context)

    # Checking if the day is not a weekend
    if day.weekday() == 5 or day.weekday() == 6:
        lessons = None
        context = {'lessons': lessons}
        return render(request, "substitute/teacher_home.html", context)

    # Obtaining holidays recorded in the DB and checking against the range
    holidays = Holiday.objects.filter(type="Holiday")
    for holiday in holidays:
        # If the holiday is a single day
        if holiday.end == None:
            if day == holiday.start:
                lessons = None
                context = {'lessons': lessons}
                return render(request, "substitute/teacher_home.html", context)
        # If the holiday spans over a few days
        elif holiday.start <= day <= holiday.end:
            lessons = None
            context = {'lessons': lessons}
            return render(request, "substitute/teacher_home.html", context)

    # Check week 1 or 2 according to the academic calendar without considering holidays
    if dt1.days % 14 <= 6:
        week = "Week 1"
    else:
        week = "Week 2"

    # Alternate weeks according to holidays
    for holiday in holidays:
        # Ignore if the holiday is a single day
        if holiday.end != None:
            # Check how long the holiday is
            dt = holiday.end - holiday.start
            # If the holiday is longer than a week and the given day is after the holiday, the week switches
            if (dt.days + 1) >= 7 and holiday.start < day:
                # Checking if the holiday length is an odd number, meaning that the weeks switch
                if 6 <= dt.days % 14 <= 8:
                    # Switching week 1/2
                    if week == "Week 1":
                        week = "Week 2"
                    else:
                        week = "Week 1"

    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    d = days[day.weekday()]
    lessons = tuple(Lesson.objects.filter(
        teacher=request.user, day=d+" ("+week+")").values_list('id', 'period').order_by('period'))
    context = {'lessons': lessons}
    return render(request, "substitute/teacher_home.html", context)

# Webpage for reporting absence and choosing the day


@login_required(login_url="login")
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

            start = Holiday.objects.get(type="Calendar").start
            dt1 = day - start
            end = Holiday.objects.get(type="Calendar").end
            dt2 = day - end

            # Checking if the given day is before/past the academic calendar
            if (dt1.days < 0) or (dt2.days > 0):
                messages.warning(request,
                                 "The inputted day is not in this year's academic calendar")
                return HttpResponseRedirect(request.path_info)

            # Checking if the day is not a weekend
            if day.weekday() == 5 or day.weekday() == 6:
                messages.warning(request, "The inputted day is a holiday.")
                return HttpResponseRedirect(request.path_info)

            # Obtaining holidays recorded in the DB and checking against the range
            holidays = Holiday.objects.filter(type="Holiday")
            for holiday in holidays:
                # If the holiday is a single day
                if holiday.end == None:
                    if day == holiday.start:
                        messages.warning(request,
                                         "The inputted day is a holiday.")
                        return HttpResponseRedirect(request.path_info)
                # If the holiday spans over a few days
                elif holiday.start <= day <= holiday.end:
                    messages.warning(request,
                                     "The inputted day is a holiday.")
                    return HttpResponseRedirect(request.path_info)

            # Check week 1 or 2 according to the academic calendar without considering holidays
            if dt1.days % 14 <= 6:
                week = "Week 1"
            else:
                week = "Week 2"

             # Alternate weeks according to holidays
            for holiday in holidays:
                # Ignore if the holiday is a single day
                if holiday.end != None:
                    # Check how long the holiday is
                    dt = holiday.end - holiday.start
                    # If the holiday is longer than a week and the given day is after the holiday, the week switches
                    if (dt.days) >= 6 and holiday.start < day:
                        # Checking if the holiday length is an odd number, meaning that the weeks switch
                        print(dt.days)
                        if 6 <= dt.days % 14 <= 8:
                            # Switching week 1/2
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

    # When there are no classes

    form = AbsenceDayForm(year=year)

    context = {"form": form}
    return render(request, "substitute/absence_report_day.html", context)

# Webpage for selecting specific periods teachers will miss for the selected day


@login_required(login_url="login")
def absence_report_period(request):
    # Retrieving the day that the teacher selected and the lessons they have on that day
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

            # Iterating through the lessons reported to retrieve teachers available at that time
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

                # Finding optimum substitute teacher
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

                sublesson = Lesson.objects.get(
                    teacher=request.user, day=day, period=lesson)

                subteacher = User.objects.get(email="rkawamura0483@gmail.com")
                send_mail(
                    # Title
                    'Substitute Request',

                    # Body
                    'Teacher: ' + request.user.first_name + " " + request.user.last_name
                    + "\nDay: " +
                    request.session.get("day")+"\nPeriod: "+lesson+"\nRoom: "
                    + sublesson.room + "\nMessage: " + message +
                    "\n\nIf you are available, please click this url to confirm. "
                    + "saintmaur.pythonanywhere.com/confirm/" +
                    str(subteacher.id)
                    + "\nIf you are unavailable, please click this url. " +
                    "saintmaur.pythonanywhere.com/deny/" + str(subteacher.id),

                    # Sender
                    'rkawamura0483@gmail.com',

                    # Recipient
                    ["rkawamura0483@gmail.com"],
                    fail_silently=False,
                )

                sublesson = Lesson.objects.get(
                    teacher=request.user, day=day, period=lesson)
                days = request.session.get("day").split(" ")
                months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
                date = datetime.date(
                    int(days[2]), months[days[1][:-1]], int(days[0]))
                Substitute.objects.create(
                    lesson=sublesson, teacher=min, date=date, verified=False)
                return redirect("teacher_home")

    form = AbsenceForm(lessons)
    formset = MessageFormSet()
    context = {"form": form, 'formset': formset,
               'day': day, 'lesson_list': lesson_list}
    return render(request, "substitute/absence_report_period.html", context)


def confirm(request, pk):
    # Finding the matching teacher with the pk
    subteacher = User.objects.get(id=pk)
    # Finding the lesson that the teacher is substituting for
    substitutes = Substitute.objects.filter(teacher=subteacher, verified=False)
    for sub in substitutes:
        # Changing the status of the lesson to confirmed
        sub.verified = True
        sub.save()
        # Incrementing the teacher's subcount
        subteacher.count += 1
        subteacher.save()
    return render(request, "substitute/confirm.html")


def deny(request, pk):
    send_mail(
        # Title
        'Substitute Request',

        # Body
        'Teacher: ' + 'Sandra' + ' ' + 'Aguilera'
        + '\nDay: ' +
        '06 March 2023'+'\nPeriod: '+'Period 2'+'\nRoom: '
        + 'HS-1' + '\nMessage: ' + 'Please review' +
        '\n\nIf you are available, please click this url to confirm. '
        + 'saintmaur.pythonanywhere.com/confirm/' +
        '754'
        + '\nIf you are unavailable, please click this url. ' +
        'saintmaur.pythonanywhere.com/deny/' + '754',

        # Sender
        'rkawamura0483@gmail.com',

        # Recipient
        ['rtest0483@gmail.com'],
        fail_silently=False,
    )
    return render(request, "substitute/confirm.html")
    # Finding the matching teacher with the pk
    subteacher = User.objects.get(id=pk)
    # Finding the lesson that the teacher is substituting for
    substitutes = Substitute.objects.filter(teacher=subteacher, verified=False)
    for sub in substitutes:
        # Iterating through the lessons reported to retrieve teachers available at that time
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

            # Finding optimum substitute teacher
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

            sublesson = Lesson.objects.get(
                teacher=request.user, day=day, period=lesson)
            subteacher = User.objects.get(email="rtest0483@gmail.com")

            send_mail(
                # Title
                'Substitute Request',

                # Body
                'Teacher: ' + request.user.first_name + " " + request.user.last_name
                + "\nDay: " +
                request.session.get("day")+"\nPeriod: "+lesson+"\nRoom: "
                + sublesson.room + "\nMessage: " + message +
                "\n\nIf you are available, please click this url to confirm. "
                + "saintmaur.pythonanywhere.com/confirm/" +
                str(subteacher.id)
                + "\nIf you are unavailable, please click this url. " +
                "saintmaur.pythonanywhere.com/deny/" + str(subteacher.id),

                # Sender
                'rkawamura0483@gmail.com',

                # Recipient
                ["rtest0483@gmail.com"],
                fail_silently=False,
            )

            sublesson = Lesson.objects.get(
                teacher=request.user, day=day, period=lesson)
            days = request.session.get("day").split(" ")
            months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                      "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            date = datetime.date(
                int(days[2]), months[days[1][:-1]], int(days[0]))
            Substitute.objects.create(
                lesson=sublesson, teacher=min, date=date, verified=False)
    return render(request, "substitute/confirm.html")
