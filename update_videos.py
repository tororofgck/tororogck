import os,json,urllib.request,urllib.parse,re
key=os.environ['YOUTUBE_API_KEY']; base='https://www.googleapis.com/youtube/v3/'
def get(path,**kw):
 u=base+path+'?'+urllib.parse.urlencode(dict(kw,key=key))
 with urllib.request.urlopen(u,timeout=30) as r:return json.load(r)
channel=get('channels',part='contentDetails',id='UCsvwCi51I9pFl3fVf18pWEQ')
pid=channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
items=[];page=None
while len(items)<100:
 args=dict(part='snippet,contentDetails',playlistId=pid,maxResults=50)
 if page:args['pageToken']=page
 result=get('playlistItems',**args);items+=result.get('items',[]);page=result.get('nextPageToken')
 if not page:break
ids=[x['contentDetails']['videoId'] for x in items if x.get('contentDetails',{}).get('videoId')]
details={}
for i in range(0,len(ids),50):
 for v in get('videos',part='contentDetails,status',id=','.join(ids[i:i+50])).get('items',[]):details[v['id']]=v
normal=[];shorts=[]
for x in items:
 vid=x.get('contentDetails',{}).get('videoId');info=details.get(vid)
 if not info or info.get('status',{}).get('privacyStatus')!='public' or info.get('status',{}).get('embeddable') is False:continue
 iso=info['contentDetails'].get('duration','PT0S');parts=re.search(r'(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$',iso)
 h,m,s=[int(n or 0) for n in parts.groups()];seconds=h*3600+m*60+s
 # YouTube Data API does not provide a definitive Shorts flag.
 # <=180s is a heuristic and may classify some short horizontal videos as Shorts.
 entry={'videoId':vid,'title':x['snippet']['title'],'thumbnail':'https://i.ytimg.com/vi/'+vid+'/mqdefault.jpg','durationSeconds':seconds}
 (shorts if seconds<=180 else normal).append(entry)
with open('videos.json','w',encoding='utf-8') as f:json.dump({'normal':normal[:20],'shorts':shorts[:30]},f,ensure_ascii=False,indent=2)
print('Normal:',len(normal),'Shorts candidates:',len(shorts))
