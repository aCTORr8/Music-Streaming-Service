from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup as bs
import re

def top_artists():
  url = "https://spotify-scraper.p.rapidapi.com/v1/artist/related"
  querystring = {"artistId": "2uFUBdaVGtyMqckSeCl0Qj"}
  headers = {
    "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
    "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
  }
  try:
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    response_data = response.json()

    related_artists_info = []

    if 'items' in response_data.get('relatedArtists', {}):
      for item in response_data['relatedArtists']['items']:
        name = item.get('name', 'No Name')
        avatar_url = item.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No URL')
        item_id = item.get('id', 'No ID')
        related_artists_info.append((name, avatar_url, item_id))

    return related_artists_info

  except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    return []
  
def top_tracks():
    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/related"
    querystring = {"artistId": "2uFUBdaVGtyMqckSeCl0Qj"}
    headers = {
      "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
      "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    } 

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        response_data = response.json()

        artists_related_info = []

        if 'items' in response_data.get('relatedArtists', {}):
            last_18_items = response_data['relatedArtists']['items'][-18:]

            for i, item in enumerate(last_18_items):
                name = item.get('name', 'No Name')
                avatar_url = item.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No URL')
                item_id = item.get('id', 'No ID')
                artists_related_info.append((name, avatar_url, item_id))    

        return artists_related_info

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    
def get_audio_details(query):

  url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"
  querystring = {"track":"Lego House Ed Sheeran"}
  headers = {
    "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
    "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
  }

  response = requests.get(url, headers=headers, params=querystring)

  audio_details = []

  if response.status_code == 200:
      response_data = response.json()
      
      if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
        audio_list = response_data['youtubeVideo']['audio']
        if audio_list:
          first_audio_url = audio_list[0]['url']
          duration_text = audio_list[0]['durationText']

          audio_details.append(first_audio_url)
          audio_details.append(duration_text)
        else:
          print("No audio data availble")
      else:
        print("No 'youtubeVideo' or 'audio' key found")
  else:
    print("Failed to fetch data")
  
  return audio_details

def get_track_image(track_id, track_name):
    url = 'https://open.spotify.com/track/'+track_id
    r = requests.get(url)
    soup = bs(r.content)
    image_links_html = soup.find('img', {'alt': track_name})
    if image_links_html:
        image_links = image_links_html['srcset']
    else:
        image_links = ''

    match = re.search(r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w', image_links)

    if match:
        url_640w = match.group().rstrip(' 640w')
    else:
        url_640w = ''

    return url_640w

def music(request, pk):
    track_id = pk

    url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"
    querystring = {"trackId":"5ubHAQtKuFfiG4FXfLP804"}
    headers = {
      "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
      "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        track_name = data.get("name", "Unknown Track")
        artists_list = data.get("artists", [])
        first_artist_name = "No artist found"
        if artists_list:
          first_artist_name = artists_list[0].get("name", "No artist found")
        
        audio_details_query = track_name + first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]
        
        track_image = get_track_image(track_id, track_name)


        context = {
          'track_name': track_name,
          'artist_name': first_artist_name,
          'audio_url': audio_url,
          'duration_text': duration_text,
          'track_image': track_image,
        }
    else:
        context = {
            'track_name': "Track not found",
            'artist_name': "Artist not found"
        }

    return render(request, 'music.html', context)
   
def search(request):
  if request.method == 'POST':
    search_query = request.POST['search_query']

    url = "https://spotify-scraper.p.rapidapi.com/v1/search"

    querystring = {"term":search_query,"type":"track"}

    headers = {
      "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
      "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    track_list = []
    
    if response.status_code == 200:
      data = response.json()

      search_results_count = data["tracks"]["totalCount"]
      tracks = data["tracks"]["items"]

      for track in tracks:
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        duration = track["durationText"]
        trackid = track["id"]

        if get_track_image(trackid, track_name):
          track_image = get_track_image(trackid, track_name)
        else:
          track_image = "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"
  
          track_list.append({
            'track_name': track_name,
            'artist_name': artist_name,
            'duration': duration,
            'trackid': trackid,
            'track_image': track_image,
        })
        context = {
          'search_results_count': search_results_count,
          'track_list': track_list,
       }
    return render(request, 'search.html', context)
  else:
    return render(request, 'search.html')

def profile(request, pk):
    artist_id = pk

    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"

    querystring = {"artistId": artist_id}

    headers = {
      "x-rapidapi-key": "fdf56cae71msh179b0a3a57315a6p106eaejsnf2eacb23db6f",
      "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()

        name = data["name"]
        monthly_listeners = data["stats"]["monthlyListeners"]
        header_url = data["visuals"]["header"][0]["url"]

        top_tracks = []

        for track in data["discography"]["topTracks"]:
          trackid = str(track["id"])
          trackname = str(track["name"])
          if get_track_image(trackid, trackname):
              trackimage = get_track_image(trackid, trackname)
          else:
              trackimage = "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"

          track_info = {
              "id": track["id"],
              "name": track["name"],
              "durationText": track["durationText"],
              "playCount": track["playCount"],
              "track_image": trackimage
          }

          top_tracks.append(track_info)

        artist_data = {
            "name": name,
            "monthlyListeners": monthly_listeners,
            "headerUrl": header_url,
            "topTracks": top_tracks,
        }

    return render(request, 'profile.html', artist_data)


@login_required(login_url='login')
def index(request):
    related_artists_info = top_artists()
    top_track_list = top_tracks()

    print(top_artists)

    first_six_tracks = top_track_list[:6]
    second_six_tracks = top_track_list[6:12]
    third_six_tracks = top_track_list[12:18]

    context = {
        'related_artists_info': related_artists_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }

    return render(request, 'index.html', context)
 
def login(request):
  if request.method == "POST":
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username,password=password)

    if user is not None:

      auth.login(request, user)
      return redirect('/')
    else:
      messages.info(request, 'Credentials Invalid')
      return redirect('login')

  return render(request, 'login.html')
 
def signup(request):
  if request.method == "POST":
    email = request.POST['email']
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password2']
    
    if password == password2:
      if User.objects.filter(email=email).exists():
        messages.info(request, 'Email Taken')
        return redirect('signup')
      elif User.objects.filter(username=username).exists():
        messages.info(request, 'Username Taken')
        return redirect('signup')
      else:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user_login = auth.authenticate(username=username, email=email, password=password)
        auth.login(request, user_login)
        return redirect('/')
    else:
      messages.info(request, 'Password Not Matching')
      return redirect('signup')
  else:
    return render(request, 'signup.html')
  
@login_required(login_url='login')
def logout(request):
  auth.logout(request)
  return redirect('login')
 

