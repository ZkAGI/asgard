from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView

from core.utils import StandardResponse
from listner.models import TGVerifiedUsers


class VerifyTelegram(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        userid = data.get("userid")
        otp = data.get("otp")
        try:
            tguser = TGVerifiedUsers.objects.get(userid=userid)
        except:
            return StandardResponse(
                data=None,
                errors={"data": "No such user found"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not otp == tguser.otp:
            return StandardResponse(
                data=None,
                errors={"data": "Invalid OTP"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return StandardResponse(
            data={"data": "User verified"},
            errors=None,
            status_code=status.HTTP_200_OK,
        )
