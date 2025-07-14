#Importing libraries
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import plotly.express as px
st.set_page_config(
    page_title="IMDb Data Visualizer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("<h1 style = 'text-align: center;'>🎬 IMDb Movie Dashboard</h>", unsafe_allow_html=True)
st.markdown("---", unsafe_allow_html=True)

#Uploading and Reading csv file
file = st.file_uploader("Select Files", type=['csv'])
if file:
    csv_path = os.path.join(os.path.dirname(__file__), 'IMDB_Movies_Data.csv')
    df = pd.read_csv(csv_path)

    #Data Visualization
    def visualizer():
        tab1, tab2 = st.tabs(["📋 Full Data", "📈 Visualizations"])

        #Combine all genres for Displaying the Data frame
        df_combined = df.groupby('Title').agg({
            'Genre': lambda x: ', '.join(sorted(set(x.str.split(',\s*').sum()))),  
            'Ratings': 'first',
            'Runtime': 'first',
            'Vote_Counts': 'first'
        }).reset_index()

        df_combined.index = range(1, len(df_combined) + 1)

        with tab1:
            st.subheader("📋 Full IMDb Movie Dataset")
            search_term = st.text_input("🔍 Search by Title")
            if search_term:
                df_combined = df_combined[df_combined['Title'].str.contains(search_term, case=False, na=False)]
            st.dataframe(df_combined[['Title', 'Genre', 'Ratings', 'Runtime', 'Vote_Counts']])

            def get_duration_category(rt):
                if rt < 120:
                    return "< 2hrs"
                elif 120 <= rt <= 180:
                    return "2-3hrs"
                else:
                    return "> 3hrs"
                
            df_combined['Duration (Hrs)'] = df_combined['Runtime'].apply(get_duration_category)
            
            #Explode genres for filtering
            df_exploded = df_combined.copy()
            df_exploded['Genre'] = df_exploded['Genre'].str.split(', ')
            df_exploded = df_exploded.explode('Genre')

            #Applying Filters
            st.sidebar.header("Apply Filters")
            filtered_df = df_exploded.copy()

            genre_options = sorted(df['Genre'].dropna().unique())
            genre_filter = st.sidebar.multiselect("Select Genres", options=genre_options, default=[])

            ratings_filter = st.sidebar.slider("Minimum IMDB Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.1)

            votings_filter = st.sidebar.number_input("Minimum Voting Counts", min_value=0, value=0, step=500)

            duration_filter = st.sidebar.multiselect("Select Duration Range", 
                                                    options=['< 2hrs', '2-3hrs', '> 3hrs'],
                                                    default=[]
                                                    )
            
            apply_filters = st.sidebar.button("Apply")
            
            if apply_filters:
                if genre_filter:
                    filtered_df = filtered_df[filtered_df['Genre'].isin(genre_filter)]

                if duration_filter:
                    filtered_df = filtered_df[filtered_df['Duration (Hrs)'].isin(duration_filter)]

                filtered_df = filtered_df[
                    (filtered_df['Ratings'] >= ratings_filter) &
                    (filtered_df['Vote_Counts'] >= votings_filter)  
                ]

                filtered_df = filtered_df.groupby('Title').agg({
                    'Genre': lambda x: ', '.join(sorted(set(x))),
                    'Ratings': 'first',
                    'Vote_Counts': 'first',
                    'Runtime': 'first',
                    'Duration (Hrs)': 'first'
                }).reset_index()

                st.subheader("Filtered Results")
                st.write(f"Showing {len(filtered_df)} result(s)")
                filtered_df.index = range(1, len(filtered_df) + 1)
                st.dataframe(filtered_df)
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Filtered Data", csv, "filtered_imdb.csv", "text/csv")
        
        #Data Visualization using various Charts
        with tab2:
            #Top 10 Movies
            st.subheader("🏆 Top 10 Movies")
            top_movies = df.sort_values(by=["Ratings", "Vote_Counts"], ascending=[False, False]).drop_duplicates(subset = "Title").head(10)
            cols = top_movies[["Title", "Ratings", "Vote_Counts"]]
            cols.index = range(1, len(cols) + 1)
            st.dataframe(cols)

            #Genre Distribution
            genre = df['Genre'].astype(str)
            genre_counts = genre.value_counts()
            genre_df = genre_counts.reset_index()
            genre_df.columns = ['Genre', 'Count']
            fig = px.bar(
                    genre_df,
                    x='Count',
                    y='Genre',
                    orientation='h',
                    color='Count',
                    color_continuous_scale='viridis',
                    hover_data={'Genre': True, 'Count': True},
                    title='📊 Genre Distribution'
                )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig)

            #Average Duration per Genre
            df['Runtime'] = df['Runtime'].astype(int)
            avg_duration = df.groupby(genre)['Runtime'].mean().sort_values(ascending=False)
            duration_df = avg_duration.reset_index()
            duration_df.columns = ['Genre', 'Average Duration']
            fig = px.bar(
                duration_df,
                x='Average Duration',
                y='Genre',
                orientation='h',
                color='Average Duration',
                color_continuous_scale='magma',
                hover_data={'Genre': True, 'Average Duration': ':.1f'},
                title='📊 Average Duration per Genre'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig)

            #Duration Extremes
            st.subheader("⏱️ Duration Extremes")
            shortest = df.loc[df['Runtime'].idxmin()]
            longest = df.loc[df['Runtime'].idxmax()]

            #Function for runtime Format
            def format_runtime(minutes):
                hrs = minutes // 60
                mins = minutes % 60
                return f"{int(minutes)} min ({int(hrs)}h {int(mins)}m)"
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🎬 Shortest Movie")
                st.metric(label = 'Title', value = shortest['Title'])
                st.metric(label = 'Duration', value = format_runtime(shortest['Runtime']))

            with col2:
                st.subheader("🎬 Longest Movie")
                st.metric(label = 'Title', value = longest['Title'])
                st.metric(label = 'Duration', value = format_runtime(longest['Runtime']))

            #Voting Trends by Genre
            df['Vote_Counts'] = df['Vote_Counts'].astype(float)
            average_votes = df.groupby('Genre', as_index=False)['Vote_Counts'].mean()
            average_votes = average_votes.sort_values(by = 'Vote_Counts', ascending=False)
            fig = px.treemap(
                average_votes,
                path=['Genre'],
                values='Vote_Counts',
                color='Vote_Counts',
                color_continuous_scale='YlGnBu',
                hover_data={'Vote_Counts': ':.0f'},
                title=("👍 Voting Trends by Genre")
            )
            st.plotly_chart(fig)

            #Distribution of Movie Ratings
            plot_type = st.selectbox("Select Plot type:", ["Histogram", "Boxplot"])
            if plot_type == "Histogram":
                fig = px.histogram(
                    df,
                    x='Ratings',
                    nbins=20,  # Adjust bin size as needed
                    color_discrete_sequence=['skyblue'],
                    hover_data=['Title', 'Genre', 'Vote_Counts'],
                    title="⭐ Distribution of Movie Ratings"
                )
                fig.update_layout(
                    xaxis_title="Ratings",
                    yaxis_title="Number of Movies",
                    bargap=0.1
                )
                st.plotly_chart(fig)

            elif plot_type == "Boxplot":
                fig = px.box(
                    df,
                    x='Ratings',
                    points="all",  # show all points
                    hover_data=['Title', 'Genre', 'Vote_Counts'],
                    title="⭐ Distribution of Movie Ratings"
                )
                st.plotly_chart(fig)

            #Most Popular Genres
            genre_votes = df.groupby('Genre')['Vote_Counts'].sum().reset_index()
            fig = px.pie(
                genre_votes,
                names='Genre',
                values='Vote_Counts',
                color_discrete_sequence=px.colors.sequential.RdBu,
                hover_data={'Vote_Counts': True},
                title=("🎭 Most Popular Genres")
            )
            fig.update_traces(textinfo='percent+label', hovertemplate='%{label}<br>Votes: %{value:,}')
            fig.update_layout(
                width=700,
                height=500,  
                margin=dict(t=20, b=20, l=20, r=50)
            )
            st.plotly_chart(fig)

            #Genre-Based Rating Leaders
            st.subheader("⭐ Genre-Based Rating Leaders")
            top_rated = df.sort_values(by = "Ratings", ascending=False).drop_duplicates('Genre')
            cols1 = top_rated[["Title", "Genre", "Ratings"]].sort_values(by = 'Genre')
            cols1["Ratings"] = cols1["Ratings"].map('{:.1f}'.format)
            cols1.index = range(1, len(cols1) + 1)
            st.dataframe(cols1)

            #Correlation Analysis
            st.subheader("📈 Correlation Analysis")
            fig = px.scatter(
                filtered_df,
                x='Ratings',
                y='Vote_Counts',
                hover_name='Title',
                hover_data={
                    'Genre': True,
                    'Runtime': True,
                    'Ratings': ':.1f',
                    'Vote_Counts': ':,'
                },
                color='Genre',
                size='Vote_Counts',
                title='Ratings vs Voting Counts'
            )
            fig.update_layout(legend_title="Genre")
            st.plotly_chart(fig)

            #Correlation Coefficient
            corr_values = df['Ratings'].corr(df['Vote_Counts'])
            st.write(f"📈 **Correlation Coefficient**: `{corr_values:.2f}`" )

            #Ratings by Genre
            st.subheader("🎭 Ratings by Genre")
            average_ratings = df.groupby('Genre')['Ratings'].mean().reset_index()
            heat_map = average_ratings.pivot_table(index = 'Genre', values = 'Ratings')
            fig, ax = plt.subplots(figsize=(8, len(heat_map) * 0.2))
            fig.patch.set_alpha(0.0)    
            ax.set_facecolor('none')
            sns.heatmap(
                heat_map,
                annot=True,
                cmap="coolwarm",
                fmt=".1f",
                cbar_kws={'label': 'Average Rating'},
                ax=ax
            )
            ax.tick_params(axis='both', labelsize=7)
            ax.set_ylabel("Genre", fontsize=7)
            ax.set_xlabel("")
            plt.xticks(rotation=0)
            plt.yticks(rotation=0)  
            ax.tick_params(colors='white')       
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            st.pyplot(fig)

    visualizer()

else:
    st.error("No csv file found!")








        

