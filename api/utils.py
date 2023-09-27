from datetime import datetime
from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import random


class Utils:
    def convertFromBase64ToFile(image, name):
        format, imgstr = image.split(';base64,')  # type: ignore
        if format != None:
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=name + '.' + ext)
            return data

    # ESTA FECHA TIENE QUE VENIR CONVERTIDA EN UN FORMATO ESPECIFICO. EN ANGULAR SE TIENE QUE SETTIAR LA FECHA A toLocaleString()
    def convertDateToSave(self, date):
        if date != None:
            # type: ignore
            return datetime.strptime(date, "%d/%m/%Y, %H:%M:%S")
        else:
            return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get(
            'HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def generar_codigo(self):
        codigo = ""
        for i in range(4):
            codigo += str(random.randint(0, 9))
        return codigo

    def calculate_remaining_time_in_seconds(self, start_date, end_date):
        remaining_time = end_date - start_date
        return int(remaining_time.total_seconds())


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if self.context.get('request', None):
            fields = self.context['request'].query_params.get('fields', None)
            if fields:
                fields = fields.replace(" ", "").split(',')
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)
