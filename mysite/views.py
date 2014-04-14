from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render

from contracts.models import Advertiser


__author__ = 'roger'


class AdvertiserForm(ModelForm):
    class Meta:
        model = Advertiser
        exclude = ['approved', 'email']

        help_texts = {
            'salesperson':
                '(optional) If you were contacted by someone at The Harvard Lampoon, you can select their name here.',
        }


@login_required
def register_advertiser(request):
    if request.method == 'POST':
        form = AdvertiserForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            advertiser = form.save(commit=False)
            if not advertiser.email:
                advertiser.email = request.user.email
            advertiser.save()
            form.save_m2m()
            profile = request.user.get_profile()
            profile.advertiser = advertiser
            profile.save()
            # if no user info, update it here
            if not request.user.first_name:
                if len(advertiser.contact.split()) == 2:
                    request.user.first_name = advertiser.contact.split()[0]
                    request.user.last_name = advertiser.contact.split()[1]
                else:
                    request.user.first_name = advertiser.contact
                request.user.save()

            messages.success(request, 'Advertiser profile updated.')
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            else:
                return HttpResponseRedirect('/')
    else:
        profile = request.user.get_profile()
        data = {}
        data['form'] = AdvertiserForm(instance=profile.advertiser, initial={'email': request.user.email})

        if profile.advertiser is None:
            messages.warning(request, 'Before ordering an ad contract, you must first fill in your contact profile.')
        else:
            data['approved'] = profile.advertiser.approved
        return render(request, 'advertiser/form.html', data)

