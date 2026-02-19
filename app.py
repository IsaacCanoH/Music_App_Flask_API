from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote

app = Flask(__name__)
session = requests.Session()


def get_itunes_top(limit=12, country="us"):
    url = f"https://rss.applemarketingtools.com/api/v2/{country}/music/most-played/{limit}/songs.json"

    try:
        r = session.get(url, timeout=(3, 10))
        r.raise_for_status()
        data = r.json()

        songs = []
        for item in data.get("feed", {}).get("results", []):
            cover = item.get("artworkUrl100")

            songs.append({
                "title": item.get("name"),
                "preview": None,  
                "artist_name": item.get("artistName"),
                "artist_image": cover, 
                "album_title": item.get("collectionName"), 
                "album_cover": cover,
                "itunes_url": item.get("url"), 
            })
        return songs
    except Exception:
        return []



@app.route('/', methods=['GET', 'POST'])
def search():
    songs = []
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            url = f"https://api.deezer.com/search?q={quote(query)}&limit=12"
            r = session.get(url, timeout=(3, 10))
            data = r.json()

            for track in data.get('data', []):
                title = track.get('title')
                artist_name = track.get('artist', {}).get('name')

                artist_image = track.get('artist', {}).get('picture_medium')
                album_cover = track.get('album', {}).get('cover_medium')
                image = artist_image or album_cover

                songs.append({
                    'title': title,
                    'preview': track.get('preview'),
                    'artist_name': artist_name,
                    'artist_image': image,
                    'album_title': track.get('album', {}).get('title'),
                    'album_cover': album_cover,
                })

    if not songs:
        songs = get_itunes_top(limit=12, country="mx")  

    return render_template('index.html', songs=songs)


@app.route('/lyrics')
def lyrics():
    artist = request.args.get('artist', '').strip()
    title = request.args.get('title', '').strip()
    if not artist or not title:
        return jsonify({"lyrics": "Letra no disponible"}), 400

    try:
        lyr_url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
        r = session.get(lyr_url, timeout=(3, 8))
        if r.status_code == 200:
            return jsonify({"lyrics": (r.json().get("lyrics") or "Letra no disponible")})
    except Exception:
        pass

    return jsonify({"lyrics": "Letra no disponible"})


if __name__ == '__main__':
    app.run(debug=True)
