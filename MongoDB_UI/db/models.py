from django.db import models

# Create your models here.

# class User(models.Model):
#     gender = (
#         ('male', '男'),
#         ('female', '女'),
#     )
#     usrAccount = models.StringField(max_length=20, unique=True)
#     usrPassword = models.StringField(max_length=20)
#     usrSex = models.StringField(max_length=32, choices=gender, default='男')
#     usrAge = models.IntField()
#     usrAbility = models.StringField(max_length=32)
#     usrWork_time = models.ListField()
#     usrSalary = models.IntField()
#
#     def __str__(self):
#         return self.usrAccount