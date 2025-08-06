from django.db import models

class Users(models.Model):
    id_user = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, default="Nam")
    dob = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=50, default="Vietnamese")

    class Meta:
        db_table = '[dbo].[Users]'   # Bắt buộc đúng tên bảng & schema
        managed = False             # Không cho Django tự tạo bảng
