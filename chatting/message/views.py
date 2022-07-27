from django.shortcuts import render
import json
from django.conf import settings # gives access to the Stream API-key and secret values we declared
from django.views.decorators.csrf import csrf_exempt #allows access to the view using external RESTful services---HTTPS request sent from client and an HTTPS response from server.
from django.http import JsonResponse
from stream_chat import StreamChat

from .models import Member

# Create your views here.
@csrf_exempt
def init(request):
    if not request.body:
        return JsonResponse(status=200, data={'message':'No request body'})
    print(request.body)
    body = json.loads(bytes(request.body).decode('utf-8'))
    
    if 'username' not in body:
        return JsonResponse(status=400, data ={'message':'Username is required to join the channel'})
    
    username = body['username']
    # After passing the checks, we initialize the Stream client using the API_KEY and SECRET, 
    client = StreamChat(api_key=settings.STREAM_API_KEY,
                        api_secret=settings.STREAM_API_SECRET)
    # a messaging channel is created with a General identifier
    channel = client.channel('messaging', 'General')
#  if the user exists, a token is generated and decoded using the username as the identifier
    try:
        member = Member.objects.get(username=username)
        token = bytes(client.create_token(
            user_id=member.username),encoding='utf8').decode('utf-8')
        return JsonResponse(status=200, data={"username": member.username, "token": token, "apiKey": settings.STREAM_API_KEY})
# If the username doesn’t return an existing Member when queried, A token is then generated for the member, and the new user is added to the Stream record and the messaging channel.
    except Member.DoesNotExist:
        member = Member(username=username)
        member.save()
        token = bytes(client.create_token(
            user_id=username)).decode('utf-8')
        client.update_user({"id": username, "role": "admin"})
        channel.add_members([username])

        return JsonResponse(status=200, data={"username": member.username, "token": token, "apiKey": settings.STREAM_API_KEY})
