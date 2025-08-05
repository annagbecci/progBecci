from django.shortcuts import render


def home(request):
    ctx = {
        "title": "HomeDiAnnaBB"
    }
    return render(request, template_name="baseext.html", context=ctx)


def pagewstat(request):
    return render(request,
                  template_name="pstatic.html",
                  context={"title": "PageWstat"})
