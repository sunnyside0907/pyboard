import os
import math
import socket
from datetime import datetime
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlquote
from django.views.decorators.csrf import csrf_exempt
from board.models import Board, Comment, Video  # model.py에 있는 테이블 사용
from django.db.models import Q  # Q()| 사용
from django.core.paginator import *
from . import models
from django.views.generic import ListView
import requests, json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

UPLOAD_DIR = "/Users/chaehyejin/Documents/bubblegit/pyboard/pyboard/upload/"  # upload 폴더정보


# Create your views here.


# 글 읽기 페이지 작성
@csrf_exempt
def list(request):
    # 검색하기
    try:
        search_option = request.POST["search_option"]
    except:
        search_option = ""
    try:
        search = request.POST["search"]
    except:
        search = ""

    if search_option == "all":
        boardCount = Board.objects.filter(
            Q(writer__contains=search) | Q(title__contains=search) | Q(content__contains=search)
        ).count()
    elif search_option == "writer":
        boardCount = Board.objects.filter(writer__contains=search).count()
    elif search_option == "title":
        boardCount = Board.objects.filter(title__contains=search).count()
    elif search_option == "content":
        boardCount = Board.objects.filter(content__contains=search).count()
    else:
        boardCount = Board.objects.all().count()

    try:
        start = int(request.GET['start'])
    except:
        start = 0

    page_size = 1000
    end = start + page_size

    if search_option == "all":
        boardList = Board.objects.filter(
            Q(writer__contains=search) | Q(title__contains=search) | Q(content__contains=search)
        ).order_by('-idx')[start:end]
    elif search_option == "writer":
        boardList = Board.objects.filter(writer__contains=search).order_by('-idx')[start:end]
    elif search_option == "title":
        boardList = Board.objects.filter(title__contains=search).order_by('-idx')[start:end]
    elif search_option == "content":
        boardList = Board.objects.filter(content__contains=search).order_by('-idx')[start:end]
    else:
        boardList = Board.objects.all().order_by('-idx')[start:end]
    # 페이지 네이션
    paginator = Paginator(boardList, 10)
    try:
        page = request.GET.get('page')
    except:
        page = 1
    try:
        boardList = paginator.page(page)
    except PageNotAnInteger:
        boardList = paginator.page(1)
    except EmptyPage:
        boardList = paginator.page(paginator.num_pages)

    contacts = paginator.get_page(page)
    page_range = 5
    max_index = paginator.num_pages
    current_page = int(page) if page else 1
    start_index = int((current_page - 1) / page_range) * page_range
    end_index = start_index + page_range
    num = []
    for i in range(boardCount) :
        num.append(i)

    # print(current_page, start_index, end_index, max_index)
    if end_index >= max_index:
        end_index = max_index
    p_range = paginator.page_range[start_index:end_index]


    return render(request, "list.html",
                  {"boardList": boardList, "boardCount": boardCount, "search_option": search_option, "search": search,
                   'contacts': contacts, 'p_range': p_range, "num":num
                   }
                  )


# fileter  where Q() 는 %% like 검색


# 글쓰기 페이지 작성
def write(request):
    return render(request, "write.html")


# 글쓰기 저장
@csrf_exempt
def insert(request):
    fname = ""
    fsize = 0
    if "file" in request.FILES:
        file = request.FILES["file"]
        fname = file.name
        fsize = file.size
        fp = open("%s%s" % (UPLOAD_DIR, fname), "wb")
        for chunk in file.chunks():
            fp.write(chunk)
            fp.close()

    dto = Board(writer=request.POST["writer"], title=request.POST["title"],
                content=request.POST["content"], filename=fname, filesize=fsize,
                video_url=request.POST["video_url"],
                section_school=request.POST["section_school"],
                section_subject=request.POST["section_subject"],
                section_semester=request.POST["section_semester"],
                grade=request.POST["grade"],
                th_high=request.POST["th_high"],
                th_medium=request.POST["th_medium"],
                th_default=request.POST["th_default"]
                )
    dto.save()

    return redirect("/")


# 파일 다운로드
def download(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx=id)
    path = UPLOAD_DIR + dto.filename
    print("path:", path)
    filename = os.path.basename(path)
    filename = filename.encode("utf-8")
    filename = urlquote(filename)
    print("pfilename:", os.path.basename(path))
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type="application/octet-stream")
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{0}".format(filename)
        dto.down_up()
        dto.save()
        return response


# 상세보기 - 조회수 증가 처리
def detail(request):
    id = request.GET["idx"]
    dto = Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()

    if 'https://' in dto.video_url:
        video_key = dto.video_url.split('/')[3]

        commentList = Comment.objects.filter(board_idx=id).order_by("idx")

        # filesize = "%0.2f" % (dto.filesize / 1024)     1024로 나눠서 반올림한 값으로 표시해주기
        filesize = "%.2f" % (dto.filesize / 1024)
        return render(request, "detail.html",
                      {"dto": dto, "filesize": filesize, "commentList": commentList, "video_key": video_key})

    else:
        commentList = Comment.objects.filter(board_idx=id).order_by("idx")

        # filesize = "%0.2f" % (dto.filesize / 1024)     1024로 나눠서 반올림한 값으로 표시해주기
        filesize = "%.2f" % (dto.filesize / 1024)
        return render(request, "detail.html",
                      {"dto": dto, "filesize": filesize, "commentList": commentList})


# 수정하기
@csrf_exempt
def update(request):
    print("**")
    # 글번호
    # id = request.POST["idx"]               # 이건 에러뜨고 아래꺼는 ㄱㅊ...
    id = request.POST.get('idx', False)

    # select * from board_board where idx=id
    dto_src = Board.objects.get(idx=id)
    dto_src.save()

    # 수정시 조회수, 다운로드 수 날라가는거 방지 
    hitnum = dto_src.hit
    downnum = dto_src.down

    fname = dto_src.filename  # 기존 첨부파일 이름
    fsize = dto_src.filesize  # 기존 첨부파일 크기

    if "file" in request.FILES:  # 새로운 첨부파일이 있으면
        file = request.FILES["file"]
        fname = file.name  # 새로운 첨부파일 이름
        fsize = file.size
        fp = open("%s%s" % (UPLOAD_DIR, fname), "wb")
        for chunk in file.chunks():
            fp.write(chunk)  # 파일 저장
            fp.close()

            # 첨부파일 크기 ( 업로드 완료 후 계산
            fsize = os.path.getsize(UPLOAD_DIR + fname)

        # 수정 후 board의 내용
    dto_new = Board(idx=id, writer=request.POST["writer"], title=request.POST["title"],
                    content=request.POST["content"], filename=fname, filesize=fsize, hit=hitnum, down=downnum,
                    video_url=request.POST["video_url"],
                    section_school=request.POST["section_school"],
                    section_subject=request.POST["section_subject"],
                    section_semester=request.POST["section_semester"],
                    grade=request.POST["grade"],
                    th_high=request.POST["th_high"],
                    th_medium=request.POST["th_medium"],
                    th_default=request.POST["th_default"]
                    )
    dto_new.save()  # update query 호출

    return redirect("/")  # 시작페이지로 이ddong



# 삭제하기
@csrf_exempt
def delete(request):
    # 삭제할 게시글 번호
    id = request.POST["idx"]

    # 레코드 삭제
    Board.objects.get(idx=id).delete()

    return redirect("/")


# 댓글쓰기
@csrf_exempt
def reply_insert(request):
    id = request.POST['idx']

    # 댓글 객체 생성
    dto = Comment(board_idx=id, writer=request.POST["writer"], content=request.POST["content"])

    # insert query 실행
    dto.save()

    # detai?idx=글번호 페이지로 이동
    return HttpResponseRedirect("detail?idx=" + id)


# 검색하기
# api 1 : AIzaSyDASAZfOrimhTwQ1g5F-4XquL_9uVT0n9Q
# api 2 : AIzaSyCdFvZiU0BvUPE8sor8Os9ZdkiBA3DvhFY
# api 3 : AIzaSyDaxVz4EWlhHvJH1VaQIv0P85rpEXyYNSU
def search_youtube(request):
    API_KEY = "AIzaSyASxNB6hLN-lOnTfV-waBqtYd9u0Zo08T0"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    try:
        keyword = request.POST['keyword']
    except:
        keyword = ""

    if keyword:

        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'key': API_KEY,
            'part': 'snippet',
            'type': 'video',
            'maxResults': '3',
            'q': keyword,
        }
        response = requests.get(url, params)
        response_dict = response.json()

        Video.objects.all().delete()

        for items in response_dict['items']:
            # print(items)
            print("########")
            title = items['snippet']['title']
            print("title : "+title)
            video_id = items['id']['videoId']
            print("id : "+video_id)
            description = items['snippet']['description']
            print("desc : "+description)
            print("########")
            th_high = items['snippet']['thumbnails']['high']['url']
            th_default = items['snippet']['thumbnails']['default']['url']
            th_medium = items['snippet']['thumbnails']['default']['url']

            dto = Video(video_id=video_id, video_title=title, description=description, th_high=th_high, th_default=th_default, th_medium=th_medium)
            dto.save()

        videolist = Video.objects.all()


        context = {
            'youtube_items': response_dict['items'],
            'title':title,
            'video_id':video_id,
            'description':description,
            'keyword':keyword,
            'th_high':th_high,
            'vlist': videolist,
        }
    else:
        context = {
            'youtube_items': [], 'title': None, 'video_id': None, 'description': None, 'keyword': ""
        }

    return render(request, 'search.html', context)

def search_insert(request) :
    videolist = Video.objects.all()
    for row in videolist:
        vid = row.video_id
    print(vid)
    vlist = Video.objects.get(video_id=vid)
    fname = ""
    fsize = 0
    if "file" in request.FILES:
        file = request.FILES["file"]
        fname = file.name
        fsize = file.size
        fp = open("%s%s" % (UPLOAD_DIR, fname), "wb")
        for chunk in file.chunks():
            fp.write(chunk)
            fp.close()


    context = {
        'vlist': vlist
    }
    return render(request, 'search_write.html', context)
