from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                            publish__year=year, publish__month=month,
                            publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recomends you reading "{}"'\
                        .format(cleaned_data['name'], cleaned_data['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'\
                        .format(post.title, post_url, cleaned_data['name'], cleaned_data['comments'])
            send_mail(subject, message, 'test@test.com', [cleaned_data['to']])

            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                            status='published',
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            new_comment.save()

    else:
        comment_form = CommentForm()

    return render(request,
                    'blog/post/detail.html',
                    {'post': post,
                    'comments': comments,
                    'comment_form': comment_form})
