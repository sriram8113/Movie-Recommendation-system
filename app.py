import streamlit as st
import pickle 
import pandas as pd
import requests

st. set_page_config(layout="wide")

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://media3.giphy.com/media/wQOWdWdmwYnVS/giphy.gif?cid=ecf05e47rc58dgagnymqr98lmpik7369ld05sfmwae2fkdss&rid=giphy.gif&ct=g");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=68cdc6760f9f7a64ecad63c76a73c9ad&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']



cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
sig = pickle.load(open('sig.pkl', 'rb'))
movies_list = pickle.load(open('movie_dict.pkl', 'rb'))
movies_list = pd.DataFrame(movies_list)
st.title('Movie Recommendation System')


indices = pd.Series(movies_list.index, index=movies_list['original_title'])

def get_recommendations(title):


    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    titles = movies_list['original_title']
    posters= []
    recommended_movies = []
    for i in movie_indices:
        posters.append(fetch_poster(movies_list['id'][i]))

    return titles.iloc[movie_indices].head(10), posters






st.header('Content based Recommendation')
selected_movie_name = st.selectbox('Select a movie', movies_list['original_title'])

if st.button('Recommend'):
    recommendations, posters = get_recommendations(selected_movie_name)
    col1, col2, col3, col4, col5, col6= st.columns(6)
    with col1:
        st.text(recommendations.iloc[0])
        st.image(posters[0])
    with col2:
        st.text(recommendations.iloc[1])
        st.image(posters[1])
    with col3:
        st.text(recommendations.iloc[2])
        st.image(posters[2])
    with col4:
        st.text(recommendations.iloc[3])
        st.image(posters[3])
    with col5:
        st.text(recommendations.iloc[4])
        st.image(posters[4])
    with col6:
        st.text(recommendations.iloc[5])
        st.image(posters[5])




gen_md = pickle.load(open('genre1.to_dict.pkl', 'rb'))
gen_md = pd.DataFrame(gen_md)


st.header('Recommendation based on Genre')
selected_genre = st.selectbox('Select a genre', gen_md['genre'])

def build_chart(genre, percentile=0.85):
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)
    
    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][['original_title', 'release_date', 'vote_count', 'vote_average', 'popularity']]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    
    qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(250)

    posters1= []
    for i in qualified.index.values.tolist():
        posters1.append(fetch_poster(gen_md['id'][i]))
    
    return qualified['original_title'].head(10), posters1

if st.button('Recommendation'):
    recommendations1, posters1 = build_chart(selected_genre)
    col1, col2, col3, col4, col5, col6= st.columns(6)
    with col1:
        st.text(recommendations1.iloc[0])
        st.image(posters1[0])
    with col2:
        st.text(recommendations1.iloc[1])
        st.image(posters1[1])
    with col3:
        st.text(recommendations1.iloc[2])
        st.image(posters1[2])
    with col4:
        st.text(recommendations1.iloc[3])
        st.image(posters1[3])
    with col5:
        st.text(recommendations1.iloc[4])
        st.image(posters1[4])
    with col6:
        st.text(recommendations1.iloc[5])
        st.image(posters1[5])




movies_df = pickle.load(open('metadata.to_dict.pkl', 'rb'))
movies_df = pd.DataFrame(movies_df)

st.header('Recommendation based on Cast and Crew')
selected_movie_name1 = st.selectbox('Select a movie name', movies_df['original_title'])

cosine_sim2 = pickle.load(open('similarity1.pkl', 'rb'))

vote_counts = movies_df[movies_df['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = movies_df[movies_df['vote_average'].notnull()]['vote_average'].astype('int')
C = vote_averages.mean()
m = vote_counts.quantile(0.95)

def weighted_rating(x):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

def improved_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim2[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]
    
    movies = movies_df.iloc[movie_indices][['original_title', 'vote_count', 'vote_average', 'release_date']]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.60)
    qualified = movies[(movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    qualified['wr'] = qualified.apply(weighted_rating, axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(10)

    posters2= []
    for i in qualified.index.values.tolist():
        posters2.append(fetch_poster(movies_df['id'][i]))

    return qualified['original_title'], posters2

if st.button('Recommendation on cast& crew'):
    recommendations2, posters2 = improved_recommendations(selected_movie_name1)
    col1, col2, col3, col4, col5, col6= st.columns(6)
    with col1:
        st.text(recommendations2.iloc[0])
        st.image(posters2[0])
    with col2:
        st.text(recommendations2.iloc[1])
        st.image(posters2[1])
    with col3:
        st.text(recommendations2.iloc[2])
        st.image(posters2[2])
    with col4:
        st.text(recommendations2.iloc[3])
        st.image(posters2[3])
    with col5:
        st.text(recommendations2.iloc[4])
        st.image(posters2[4])
    with col6:
        st.text(recommendations2.iloc[5])
        st.image(posters2[5])