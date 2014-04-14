from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.forms import ModelForm

from contracts.models import Advert


class AdvertForm(ModelForm):
    class Meta:
        model = Advert
        fields = ['size', 'description', 'imageFile', 'issues']
        exclude = ['notes']


def has_profile(u):
    try:
        profile = u.get_profile()
    except:
        return False
    finally:
        return profile.advertiser is not None


def is_approved(u):
    profile = u.get_profile()
    return profile.advertiser.approved


@login_required
@user_passes_test(has_profile, login_url='/register')
@user_passes_test(is_approved, login_url='/pending')
def index(request):
    adverts = Advert.objects.filter(advertiser=request.user.get_profile().advertiser)
    context = {'adverts': adverts}
    return render(request, 'contracts/list.html', context)


@login_required
@user_passes_test(has_profile, login_url='/register')
@user_passes_test(is_approved, login_url='/pending')
def create(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = AdvertForm(request.POST, request.FILES)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            new_contract = form.save(commit=False)
            new_contract.advertiser = request.user.get_profile().advertiser
            new_contract.save()
            form.save_m2m()
            messages.success(request, 'Advert created.')
            return HttpResponseRedirect('/contracts/')  # Redirect after POST
    else:
        form = AdvertForm(initial={'advertiser': request.user.get_profile().advertiser})

    return render(request, 'contracts/form.html', {'form': form})


@login_required
@user_passes_test(has_profile, login_url='/register')
@user_passes_test(is_approved, login_url='/pending')
def detail(request, contract_id):
    contract = get_object_or_404(Advert, pk=contract_id)
    return render(request, 'contracts/detail.html', {'ad': contract})


@login_required
@user_passes_test(is_approved, login_url='/pending')
def update(request, contract_id):
    if request.method == 'POST':  # If the form has been submitted...
        form = AdvertForm(request.POST, request.FILES,
                          instance=Advert.objects.get(id=contract_id))  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            ad = form.save()
            messages.success(request, 'Advert updated.')
            return HttpResponseRedirect(ad.get_absolute_url())  # Redirect after POST
    else:
        form = AdvertForm(instance=Advert.objects.get(id=contract_id))  # An unbound form

    return render(request, 'contracts/form.html', {'form': form, 'contract_id': contract_id})
