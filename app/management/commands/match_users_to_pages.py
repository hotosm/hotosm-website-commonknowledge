import time

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import PersonPage, User


class Command(BaseCommand):
    help = "Sync all CountryPage coordinates so that pages can be geo-tagged via related_countries."

    def handle(self, *args, **options):
        for user in User.objects.all():
            page, is_new = User.get_or_create_page()
