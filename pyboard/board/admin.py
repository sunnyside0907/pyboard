from django.contrib import admin
from board.models import Board

# Register your models here.

# Admin 페이지에 테이블 반영 (admin.py)

class BoardAdmin(admin.ModelAdmin):
    list_display = ("writer","title","content")

admin.site.register(Board, BoardAdmin)
