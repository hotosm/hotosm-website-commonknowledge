from typing import List, TypedDict

import json
import re
from datetime import date, datetime, time
from io import BytesIO
from multiprocessing.sharedctypes import Value
from pathlib import Path
from urllib.parse import urlparse

import marko
import PIL
import requests
import willow
import yaml
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.text import slugify
from marko import block, inline
from marko.html_renderer import HTMLRenderer
from PIL import Image as PImage
from wagtail.contrib.redirects.models import Redirect
from wagtail.core.rich_text import RichText
from wagtail.images.models import Image
from wagtail.models import Page, Site

from app.models.wagtail.cms import CMSImage
from app.models.wagtail.pages import (
    ActivationIndexPage,
    ActivationProjectPage,
    ArticlePage,
    CountryPage,
    DirectoryPage,
    HomePage,
    MagazineIndexPage,
    MagazineSection,
    OpportunityPage,
    OrganisationPage,
    PersonPage,
    ProjectPage,
    StaticPage,
)

# from wagtail.images.models import Image


class PageData(TypedDict):
    frontmatter: dict
    content: str
    page: Page
    old_path: Path


class RedirectData(TypedDict):
    old_path: str
    redirect_to: Page


class Command(BaseCommand):
    """
    main thing of interest is the WagtailHtmlRenderer class,
    which renders markdown as wagtail-friendly html using its custom notation for links.

    Other key thing is to create all the pages and images before setting their content
    so that the referenced pages all exist when the html gets rendered out
    """

    help = "Set up essential pages"

    def add_arguments(self, parser):
        parser.add_argument("--scratch", dest="scratch", type=bool, default=False)

        parser.add_argument("--limit", dest="limit", type=int, default=20)

        parser.add_argument("--start-after", dest="StartAfter", type=str, default=None)

    def handle(self, *args, **options):
        args = dict(Prefix="website/")
        if options.get("StartAfter", None) is not None:
            args["StartAfter"] = options["StartAfter"]
        items = get_images_from_s3(**args)[: options["limit"]]

        if options.get("scratch"):
            CMSImage.objects.all().delete()

        for item in items:
            file_name = item["Key"]
            if "." in file_name:
                image = save_s3_image_to_db(
                    url=f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}",
                    file_name=file_name,
                )


def save_s3_image_to_db(url, file_name=None):
    print("Syncing", url)
    title = Path(file_name).stem
    try:
        image = CMSImage.objects.get(title=url)
        print("----Found")
        return image
    except CMSImage.DoesNotExist:
        if default_storage.exists(file_name):
            try:
                s3_file = default_storage.open(file_name)
                image = CMSImage(title=url)
                image.file = s3_file
                image.file._committed = True
                image.save()
                print("----Saved")
            except IntegrityError:
                print("-- Not an image!")
        else:
            pass
        # pil_image = None
        # try:
        #     response = requests.get(url, stream=True)
        #     pil_image = PImage.open(response.raw)
        # except PIL.UnidentifiedImageError:
        #     pass
        # if pil_image is not None:
        #     print("pil_image", pil_image)
        #     image_file = ImageFile(BytesIO(response.content), name=file_name)
        #     setattr(image_file, "_dimensions_cache", [
        #             pil_image.width, pil_image.height])
        #     print("image_file", image_file)
        #     image = CMSImage(title=file_name, width=pil_image.width,
        #                      height=pil_image.height, file=image_file, alt_text="No alt text",)
        #     image.save()
        #     print("image", image)

        # response = requests.get(url, stream=True)
        # pil = None
        # try:
        #     # print(response.content)
        #     pil = PIL.Image.open(url)
        # except PIL.UnidentifiedImageError:
        #     pass
        # if pil == None:
        #     print("Image not recognised")
        #     return

        # print("Loading image", pil)
        # image_file = ImageFile(BytesIO(response.content), name=file_name)
        # image = CMSImage(title=file_name, width=pil.width,
        #                  height=pil.height, file=image_file)
        # image.save()

        # req = requests.get(url)
        # print("==== Creating image", file_name, url)
        # raw = requests.get(url, stream=True).raw
        # # image_file = ImageFile(raw, file_name)
        # # print("1. image_file", image_file)
        # pil = PIL.Image.open(raw)
        # # print("2. pil", pil)
        # image = CMSImage(title=file_name, width=pil.width,
        #                  height=pil.height)
        # print("3. image", image, image.width, image.height)
        # output = BytesIO()
        # pil.save(output, format=pil.format)
        # image.file = File(output)
        # image.save()
        # # print("4. image.file", image.file)
        # print("DONE", image)
        # return image
    # return image

    # result = request.urlretrieve(url)
    # if result:
    #     img_file = ImageFile(BytesIO(img_bytes), name=filename)
    #     im = willow.Image.open(path)
    #     width, height = im.get_size()

    #     img_obj = Image(title=filename, file=img_file, width=width, height=height)
    #     print(img_obj.file)
    #     img_obj.save()
    #     image_data = open(result[0], 'rb')
    #     image = CMSImage(
    #         title=filename,
    #         image=ImageFile(image_data, name=filename)
    #     )
    #     image.save()


def get_images_from_s3(**kwargs):
    import boto3

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
    )

    NextContinuationToken = None
    items = []

    while NextContinuationToken is not False:
        args = dict(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            **kwargs,
        )

        if NextContinuationToken:
            args.update(dict(ContinuationToken=NextContinuationToken))

        response = s3_client.list_objects_v2(**args)

        items += response["Contents"]

        # print(response)

        if "NextContinuationToken" in response:
            NextContinuationToken = response["NextContinuationToken"]
        else:
            NextContinuationToken = False

    return items
