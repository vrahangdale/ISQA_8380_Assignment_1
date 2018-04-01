from django.shortcuts import render
from .models import Post
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator




# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='5168eb4e-c906-4474-a8aa-45a56b18bdb0',
        password='epXU1ehuSvaI',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='1d3cfa1b-ed7b-4abd-95b2-0ea5ab3b0f37',
        password='OmBRt2ADGa3W')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj = json.dumps(tone_analyzer.tone(tone_input=posting,
                                                content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        obj = json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        post.translations = post.obj2['translations']
        post.translations_text = post.translations[0]['translation']
        post.word_count = post.obj2['word_count']
        post.character_count = post.obj2['character_count']

    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

