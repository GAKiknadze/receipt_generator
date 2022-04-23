from django.shortcuts import render
from django.http import FileResponse, HttpResponse
import os
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes


from .business_logic import *
from receipt_generator.settings import MEDIA_PATH


@api_view(['POST'])
@authentication_classes([])
def cash_machine(request):
    items_ids = request.data.get('items')
    if not items_ids:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    valid_items = validate_items(items_ids)
    if not valid_items:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    file_name = render_to_pdf(*valid_items)
    
    pdf_file_url = request.build_absolute_uri('media/') + file_name
    
    image = generate_qr_code(pdf_file_url)
    
    response = HttpResponse(content_type='image/jpg')
    
    image.save(response, "JPEG")
    
    return response


@api_view(['GET'])
def get_media(request, file_name: str):
    print(file_name)
    if not check_uuid4(file_name.replace('.pdf', '')) or \
        not os.path.exists(f'{MEDIA_PATH}{file_name}'):
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    f =  open(f'{MEDIA_PATH}{file_name}', 'rb')
    return FileResponse(f, filename=file_name)
