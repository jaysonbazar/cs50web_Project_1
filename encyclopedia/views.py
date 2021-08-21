from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util

import markdown
import random



class SearchForm(forms.Form):
    search = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Search Encyclopedia"}))

class NewTitleForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "form-control col-md-8 col-lg-8",
        "placeholder": "Title"}))

class NewEntryForm(forms.Form):
    entry = forms.CharField(label='', widget=forms.Textarea(attrs={
        "class": "form-control col-md-8 col-lg-8",
        'rows': 20,
        "placeholder": "Insert Text"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def title(request, title):
    md = markdown.Markdown()
    entry = util.get_entry(title)
    if entry is None:
        empty = ["Page not found"]
        return render(request, "encyclopedia/error.html", {
            "empty":empty,
            "form": SearchForm()
        })
    else:
        return render(request, "encyclopedia/title.html", {
            "entries": md.convert(entry),
            "form": SearchForm(),
            "title": title
        })

def search(request):
    similar = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            for entry in util.list_entries():
                
                if search.lower() == entry.lower():
                    return HttpResponseRedirect(f'/wiki/{search}')
                    
                elif search.lower() in entry.lower():
                    similar.append(entry)

            if not similar:
                empty = ["No similar result/s found"]
                return render(request, "encyclopedia/error.html", {
                    "empty":empty,
                    "form": SearchForm()
                })

            return render(request, "encyclopedia/search.html", {
                "entries": similar,
                "form": SearchForm()
            })
        
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "form": form
        })

    return HttpResponseRedirect(reverse("index"))


def create(request):

    if request.method == "POST":
        form_title = NewTitleForm(request.POST)
        form_entry = NewEntryForm(request.POST)

        if form_title.is_valid() and form_entry.is_valid():
            title = form_title.cleaned_data["title"]
            entry = form_entry.cleaned_data["entry"]

            for list in util.list_entries():
                if title.lower() == list.lower():
                    empty = ["Page already exists"]
                    return render(request, "encyclopedia/error.html", {
                        "empty":empty,
                        "form": SearchForm()
                    })

            util.save_entry(title, entry)
            return HttpResponseRedirect(f'wiki/{title}')
        
        return render(request, "encyclopedia/create.html", {
            "title": form_title,
            "entry": form_entry,
            "form": SearchForm()
        })

    return render(request, "encyclopedia/create.html", {
        "title": NewTitleForm(),
        "entry": NewEntryForm(),
        "form": SearchForm()
    })


def edit(request, title):
    entry = util.get_entry(title)  
    if request.method == "GET":

        return render(request, "encyclopedia/edit.html", {
            "title": NewTitleForm(initial={'title':title}),
            "entry": NewEntryForm(initial={'entry': entry}),
            "form": SearchForm()
        })

    elif request.method == "POST":
        
        form_title = NewTitleForm(request.POST)
        form_entry = NewEntryForm(request.POST)

        if form_title.is_valid() and form_entry.is_valid():
            title = form_title.cleaned_data["title"]
            entry = form_entry.cleaned_data["entry"]

            util.save_entry(title, entry)
            return HttpResponseRedirect(f'/wiki/{title}')

        return render(request, "encyclopedia/edit.html", {
            "title": form_title,
            "entry": form_entry,
            "form": SearchForm()
        })


def randoms(request):
    title = util.list_entries()
    random_title = random.choice(title)
    return HttpResponseRedirect(f'wiki/{random_title}')