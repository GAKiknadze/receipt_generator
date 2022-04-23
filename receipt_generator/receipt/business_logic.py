from datetime import datetime
from django.template import Context
from django.template.loader import get_template, render_to_string
import os
import pdfkit
from typing import List, Dict, Any, Tuple
import uuid
import qrcode


from .models import Item
from receipt_generator.settings import WKHTMLTOPDF_PATH, MEDIA_PATH


def validate_items(items_ids: List[int]) -> Tuple[Dict[Any, int], int]:
    try:
        valid_ids = list(filter(lambda x: isinstance(x, int), items_ids))
        if len(valid_ids) != len(items_ids) \
            or len(items_ids) == 0:
            raise ValueError

        valid_ids = set(valid_ids)
        
        items = Item.objects.filter(pk__in=valid_ids)
        
        items_counts = {}
        total_price = 0
        
        for item in items:
            item_count = items_ids.count(item.pk)
            item_total = item.price * item_count
            setattr(item, 'total', item_total)
            item.title = item.title.upper()
            items_counts.update({item: item_count})
            total_price += item_total

        return items_counts, total_price
    except ValueError:
        return None


def render_to_pdf(items: Dict[Any, int], total: int):
    ts = datetime.now()
    file_name = f'{uuid.uuid4()}.pdf'
    
    html = render_to_string('receipt.html',
        {
            'date': ts.date().strftime('%d.%m.%Y'),
            'time': ts.time().strftime('%H:%M'),
            'items': items,
            'total_price': total
        }
    )
    
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(html, MEDIA_PATH + file_name, configuration=config)

    return file_name


def generate_qr_code(url: str):
    return qrcode.make(url)


def check_uuid4(test_uuid, version=4):
    try:
        return uuid.UUID(test_uuid).version == version
    except ValueError:
        return False

