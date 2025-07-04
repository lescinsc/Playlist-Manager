from flask import Flask, request, render_template
import artistmethods
import auth

app = Flask(__name__)

sp = auth.create_connection()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        artist = request.form['artist']
        tracks = artistmethods.get_random_tracks_from_artist(sp, artist, 5)
        html_tracks = '<ul>' + ''.join(f'<li>{track}</li>' for track in tracks) + '</ul>'
        return f'''
            <h1>Random Tracks for "{artist}"</h1>
            {html_tracks}
            <a href="/">Search again</a>
        '''
    return '''
        <form method="post">
            <input type="text" name="artist" placeholder="Enter an artist">
            <input type="submit">
            <input type="text" name="Number of songer" placeholder="Enternumber of songs"
            <input type="submit">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)