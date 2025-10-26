import pickle
import streamlit as st
import requests
import time

#  TMDB v4 Bearer Token
TMDB_V4_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2YWEyNmRhZjFkZDRjMTNmZmI0ZTM5NzliYzJmZWI4YiIsIm5iZiI6MTc2MTQ1NTM1Ni4yMzEsInN1YiI6IjY4ZmRhY2ZjN2FiZGQ2NDRmZmVhYWQ1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.zQk1DqKpCs77e6tqqKmcjyYs7E5qyzBkL9EyJV7e468"

#  Function to fetch poster safely

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_V4_TOKEN}"
    }

    for attempt in range(3):  # retry up to 3 times
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(2)  # wait before retry

    return "https://via.placeholder.com/500x750?text=Error+Loading"


#  Function to get movie recommendations

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        time.sleep(0.3)  # short delay to avoid hitting TMDB rate limits

    return recommended_movie_names, recommended_movie_posters


st.header("🎥 Movie Recommender System")

# Load preprocessed movie data and similarity matrix
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button("Show Recommendation"):
    with st.spinner("Fetching recommendations..."):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # Display movies in rows of 5
    for row_start in range(0, len(recommended_movie_names), 5):
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            movie_idx = row_start + idx
            if movie_idx < len(recommended_movie_names):
                with col:
                    st.text(recommended_movie_names[movie_idx])
                    st.image(recommended_movie_posters[movie_idx])

