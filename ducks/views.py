from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views import generic
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from .models import Duck, DuckFact
from .forms import DuckForm, DuckFactForm


class IndexView(FormMixin, ListView):
    model = Duck
    template_name = "ducks/index.html"
    context_object_name = "duck_list"
    form_class = DuckForm
    success_url = reverse_lazy("ducks:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Duck added successfully!")
            return redirect(self.get_success_url())
        else:
            # Form is invalid, render with errors
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class DetailView(generic.DetailView):
    model = Duck
    template_name = "ducks/duck_detail.html"


def duck_by_name(request, name):
    duck = Duck.objects.filter(name=name).first()
    if duck is None:
        raise Http404("Duck not found")
    return render(request, "ducks/duck_detail.html", {"duck": duck})


def rate(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)
    try:
        fact_id = request.POST["fact_id"]
        direction = request.POST["direction"]
        selected_fact = duck.duckfact_set.get(pk=fact_id)
    except (KeyError, DuckFact.DoesNotExist):
        messages.error(request, "Unable to process your vote.")
        return render(
            request,
            "ducks/duck_detail.html",
            {
                "duck": duck,
            },
        )

    if direction == "up":
        messages.success(request, "Thanks for upvoting!")
        selected_fact.rating += 1
    elif direction == "down":
        messages.error(request, "Thanks for downvoting!")
        selected_fact.rating -= 1

    selected_fact.save()

    return HttpResponseRedirect(reverse("ducks:duck_by_id", args=(duck.id,)))


def index(request):
    duck_list = Duck.objects.all()
    form = DuckForm()

    if request.method == "POST":
        form = DuckForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Duck added successfully!")
            return redirect("ducks:index")

    return render(request, "ducks/index.html", {"duck_list": duck_list, "form": form})


def add_fact(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)

    if request.method == "POST":
        form = DuckFactForm(request.POST)
        if form.is_valid():
            new_fact = form.save(commit=False)
            new_fact.duck = duck
            new_fact.rating = 0
            new_fact.save()
            messages.success(request, "Fact added successfully!")
            return redirect("ducks:duck_by_id", pk=duck.id)
    else:
        form = DuckFactForm()

    return render(request, "ducks/add_fact.html", {"form": form, "duck": duck})


def delete_fact_by_id(request, fact_id):
    fact = get_object_or_404(DuckFact, id=fact_id)
    if request.method == "POST":
        fact.delete()
        messages.success(request, "Fact deleted successfully")
    else:
        messages.error(request, "Invalid Request")
    return HttpResponseRedirect(reverse("ducks:duck_by_id", args=(fact.duck_id,)))


def delete_duck_by_id(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)
    if request.method == "POST":
        duck.delete()
        messages.success(request, f"Duck - `{duck.name}' - deleted successfully!")
        return redirect("ducks:index")

    messages.error(request, "Invalid Request")
    return redirect("ducks:index")
