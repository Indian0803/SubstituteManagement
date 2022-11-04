from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path

from .forms import *
from .models import *

import datetime
import unidecode


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(label="Submit a csv file")


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'middle_name',
                    'last_name', 'role', 'subject', 'count', 'is_admin')
    list_filter = ('is_admin', 'count')

    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name',
         'middle_name', 'last_name', 'role', 'subject', 'count')}),
        ('Permissions', {'fields': ('is_admin',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'middle_name', 'last_name', 'role', 'subject', 'is_admin')}
         ),
    )

    search_fields = ('email', 'first_name', 'middle_name',
                     'last_name', 'role', 'subject', 'count')
    ordering = ('email', 'first_name', 'middle_name',
                'last_name', 'role', 'subject', 'count')
    filter_horizontal = ()

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('teacher_upload/', self.teacher_upload)]
        return new_urls + urls

    def teacher_upload(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_upload"]
                if not csv_file.name.endswith('.csv'):
                    messages.warning(
                        request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                file_data = csv_file.read().decode(("utf-8"))
                csv_data = file_data.split("\n")
                csv_data.pop(0)
                csv_data.pop(-1)
                for r in csv_data:
                    fields = r.split(',')
                    if fields[4] != "Teaching Staff":
                        continue
                    first = fields[2][1:-1]
                    names = fields[1].split(' ')
                    last = names[0][1:]
                    if len(names) == 1:
                        middle = None
                    else:
                        middle = names[1]

                    email = fields[3]
                    if middle == None:
                        teacher = User.objects.create_user(
                            email=email,
                            first_name=unidecode.unidecode(first),
                            middle_name="",
                            last_name=unidecode.unidecode(last),
                            role="",
                            subject="",
                            password="test"
                        )
                    else:
                        teacher = User.objects.create_user(
                            email=email,
                            first_name=unidecode.unidecode(first),
                            middle_name=unidecode.unidecode(middle),
                            last_name=unidecode.unidecode(last),
                            role="",
                            subject="",
                            password="test"
                        )
                messages.add_message(
                    request, messages.INFO, 'File has been uploaded')
                url = reverse('admin:index')
                return HttpResponseRedirect(url)

        else:
            form = CsvImportForm()
        context = {'form': form}
        return render(request, 'admin/csv_upload.html', context)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'name', 'room', 'day', 'period')
    ordering = ('teacher', 'name', 'room', 'day', 'period')
    list_filter = ('teacher', 'count', 'day')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('csv_upload/', self.csv_upload), ]
        return new_urls + urls

    def csv_upload(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_upload"]
                if not csv_file.name.endswith('.csv'):
                    messages.warning(
                        request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                file_data = csv_file.read().decode(("utf-8"))
                csv_data = file_data.split("\n")
                csv_data.pop(0)
                substituteschedules = SubstituteSchedule.objects.all()
                for schedule in substituteschedules:
                    schedule.morning_recess.clear()
                    schedule.lunch_one.clear()
                    schedule.lunch_two.clear()
                    schedule.lunch_three.clear()
                for r in csv_data:
                    if r == "":
                        continue
                    fields = r.split(",")
                    if "Homeroom" in fields[8]:
                        continue
                    elif "Lesson Substitute" in fields[8]:
                        continue

                    if len(fields) == 13:
                        fields[8] = fields[8] + "," + fields[9]
                        fields.pop(9)
                    if fields[9] == "None":
                        continue

                    pop = 0
                    for i in range(len(fields)):
                        if fields[i].count('"') == 1 and fields[i][0] == '"':
                            fields[i] = fields[i][1:] + "," + fields[i+1][:-1]
                            pop = i+1
                    fields.pop(pop)

                    name = fields[9].split(", ")
                    if " " in name[0]:
                        names = name[0].split(" ")
                        last = names[0]
                    else:
                        last = name[0]
                    try:
                        teacher = User.objects.get(
                            first_name=name[1], last_name=last)
                    except User.DoesNotExist:
                        print(name[1])
                        print(name[0])
                    except IndexError:
                        print(fields)
                        print(name)
                    grade = fields[8][:2]
                    if grade[0] == "0":
                        if grade == "06" or grade == "07" or grade == "08":
                            if "Middle" not in teacher.role:
                                teacher.role.append("Middle")
                        elif grade == "09" and "High" not in teacher.role:
                            teacher.role.append("High")
                        else:
                            if "Elementary" not in teacher.role:
                                teacher.role.append("Elementary")
                    else:
                        if grade == "10" or grade == "11" or grade == "12":
                            if "High" not in teacher.role:
                                teacher.role.append("High")

                    if "Science" in fields[8] and "Computer Science" not in fields[8] and "Science" not in teacher.subject:
                        teacher.subject.append("Science")
                    elif "Computer Science" in fields[8] and "Computer Science" not in teacher.subject:
                        teacher.subject.append("Computer Science")
                    elif "Chemistry" in fields[8] or "Biology" in fields[8] or "Physics" in fields[8] and "Science" not in teacher.subject:
                        teacher.subject.append("Science")
                    elif "English" in fields[8] and "English" not in teacher.subject:
                        teacher.subject.append("English")
                    elif "Math" in fields[8] and "Math" not in teacher.subject:
                        teacher.subject.append("Math")
                    elif "Japanese" in fields[8] and "Japanese" not in teacher.subject:
                        teacher.subject.append("Japanese")
                    elif "Spanish" in fields[8] and "Spanish" not in teacher.subject:
                        teacher.subject.append("Spanish")
                    elif "French" in fields[8] and "French" not in teacher.subject:
                        teacher.subject.append("French")

                    if "Duty Substitute" in fields[8]:
                        schedule = SubstituteSchedule.objects.get(
                            day=fields[1])
                        if fields[3] == "Recess":
                            schedule.morning_recess.add(teacher)
                        elif fields[3] == "Lunch 1":
                            schedule.lunch_one.add(teacher)
                        elif fields[3] == "Lunch 2":
                            schedule.lunch_two.add(teacher)
                        elif fields[3] == "Lunch 3":
                            schedule.lunch_three.add(teacher)

                    if Lesson.objects.filter(teacher=teacher, day=fields[1], period=fields[3], year=fields[10]).exists():
                        continue

                    lesson = Lesson.objects.update_or_create(
                        teacher=teacher,
                        day=fields[1],
                        room=fields[2],
                        period=fields[3],
                        start=fields[4],
                        end=fields[5],
                        name=fields[8],
                        year=fields[10]
                    )
                sub = SubstituteSchedule.objects.get(day="Monday (Week 1)")

                messages.add_message(
                    request, messages.INFO, 'File has been uploaded')
                url = reverse('admin:index')
                return HttpResponseRedirect(url)

        else:
            form = CsvImportForm()
        context = {'form': form}
        return render(request, 'admin/csv_upload.html', context)


class SubstituteAdmin(admin.ModelAdmin):
    list_display = ('day',)
    ordering = ('day',)

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('substitute_upload/', self.substitute_upload)]
        return new_urls + urls

    def substitute_upload(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_upload"]
                if not csv_file.name.endswith('.csv'):
                    messages.warning(
                        request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                file_data = csv_file.read().decode(("utf-8"))
                csv_data = file_data.split("\n")
                csv_data.pop(0)

                substituteschedules = SubstituteSchedule.objects.all()
                for schedule in substituteschedules:
                    schedule.period_one.clear()
                    schedule.period_two.clear()
                    schedule.period_three.clear()
                    schedule.period_four.clear()
                    schedule.period_five.clear()
                    schedule.period_six.clear()
                days = {
                    'M1': "Monday (Week 1)", "M2": "Monday (Week 2)", "T1": "Tuesday (Week 1)", "T2": "Tuesday (Week 2)", 'W1': "Wednesday (Week 1)", "W2": "Wednesday (Week 2)", 'Th1': "Thursday (Week 1)", "Th2": "Thursday (Week 2)", 'F1': "Friday (Week 1)", "F2": "Friday (Week 2)", }

                for r in csv_data:
                    if r == "":
                        continue
                    fields = r.split(",")
                    if "Lesson Substitute" not in fields[1]:
                        continue
                    else:
                        f = fields[1].split(" ")
                        try:
                            if len(f[2]) == 4:
                                schedule = SubstituteSchedule.objects.get(
                                    day=days[f[2][:2]])

                            else:
                                schedule = SubstituteSchedule.objects.get(
                                    day=days[f[2][:3]])
                        except SubstituteSchedule.DoesNotExist:
                            print("Error")
                        period = f[2][-2:]
                        names = fields[3][1:].split(" ")
                        last = names[0]
                        first = fields[4][1:-1]
                        try:
                            teacher = User.objects.get(
                                first_name=first, last_name=last)
                            if "P1" == period:
                                schedule.period_one.add(teacher)
                            elif "P2" == period:
                                schedule.period_two.add(teacher)
                            elif "P3" == period:
                                schedule.period_three.add(teacher)
                            elif "P4" == period:
                                schedule.period_four.add(teacher)
                            elif "P5" == period:
                                schedule.period_five.add(teacher)
                            elif "P6" == period:
                                schedule.period_six.add(teacher)

                            # FIX TIME
                            # #########################################
                            #####################################################
                            #################################

                            lesson = Lesson.objects.update_or_create(
                                teacher=teacher,
                                day=fields[1],
                                room="",
                                period=fields[3],
                                start="",
                                end="",
                                name=fields[1],
                                year=fields[2]
                            )

                            ##################################
                            ###################################
                        except User.DoesNotExist:
                            print("Teacher not found")
                messages.add_message(
                    request, messages.INFO, 'File has been uploaded')
                url = reverse('admin:index')
                return HttpResponseRedirect(url)

        else:
            form = CsvImportForm()
        context = {'form': form}
        return render(request, 'admin/csv_upload.html', context)


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'type')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('csv_upload/', self.csv_upload), ]
        return new_urls + urls

    def csv_upload(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_upload"]
                if not csv_file.name.endswith('.csv'):
                    messages.warning(
                        request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                file_data = csv_file.read().decode(("utf-8"))
                csv_data = file_data.split("\n")
                csv_data.pop(0)
                csv_data.pop(-1)

                for r in csv_data:
                    fields = r.split(',')
                    type = fields[1]
                    start = datetime.datetime.strptime(fields[2], '%Y/%m/%d')
                    if fields[3] == '""':
                        end = None
                    else:
                        end = datetime.datetime.strptime(fields[3], '%Y/%m/%d')
                    Holiday.objects.update_or_create(
                        start=start, end=end, type=type)
                messages.add_message(
                    request, messages.INFO, 'File has been uploaded')
                url = reverse('admin:index')
                return HttpResponseRedirect(url)

        else:
            form = CsvImportForm()
        context = {'form': form}
        return render(request, 'admin/csv_upload.html', context)


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(SubstituteSchedule, SubstituteAdmin)
admin.site.register(Holiday, HolidayAdmin)
