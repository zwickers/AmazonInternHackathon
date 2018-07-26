def create_movie_list_attribute(movieList):
    return {'movieList': movieList, 'index': 0}


def next_movie_item(session):
    if 'index' in session.get('attributes', {}):
        index = session['attributes']['index']
        session['attributes']['index'] = index + 1
    return session['attributes']


def previous_movie_item(session):
    if 'index' in session.get('attributes', {}):
        index = session['attributes']['index']
        if index > 0:
            session['attributes']['index'] = index - 1
    return session['attributes']
