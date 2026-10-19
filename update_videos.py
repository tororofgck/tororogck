import json, os, urllib.parse, urllib.request
from pathlib import Path

KEY = os.environ['YOUTUBE_API_KEY']
CHANNEL = 'UCsvwCi51I9pFl3fVf18pWEQ'

def request(endpoint, **params):
    params['key'] = KEY
    url = 'https://www.googleapis.com/youtube/v3/' + endpoint + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'tororogck-video-updater'}), timeout=30) as response:
        return json.load(response)

channels = request('channels', part='contentDetails', id=CHANNEL)
if not channels.get('items'):
    raise RuntimeError('YouTube channel not found')
playlist = channels['items'][0]['contentDetails']['relatedPlaylists']['uploads']
items = request('playlistItems', part='snippet', playlistId=playlist, maxResults=30).get('items', [])
videos = []
for item in items:
    sn = item.get('snippet', {})
    vid = sn.get('resourceId', {}).get('videoId')
    if vid and sn.get('title') not in ('Private video', 'Deleted video'):
        videos.append({'id':vid,'title':sn.get('title','動画')})
    if len(videos) >= 10:
        break
if not videos:
    raise RuntimeError('No public videos found; preserving existing videos.json')
Path('videos.json').write_text(json.dumps(videos, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Updated videos.json:',len(videos),'videos')
