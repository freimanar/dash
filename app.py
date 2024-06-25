import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask_caching import Cache

# Создание приложения Dash
own_css = "/home/grootwood/mysite/assets/style.css"
app = dash.Dash(__name__,external_stylesheets=[own_css])
server = app.server
app.config.suppress_callback_exceptions = True
# Конфигурация кэша
cache = Cache(app.server, config={'CACHE_TYPE': 'SimpleCache'})
TIMEOUT = 60

# Загрузка данных из CSV файла
data = pd.read_csv('/home/grootwood/mysite/movies_metadata.csv', usecols=['budget', 'revenue', 'runtime', 'popularity', 'vote_average', 'original_title', 'release_date', 'overview', 'original_language'])
data['budget'] = pd.to_numeric(data['budget'], errors='coerce')
# Функции для создания графиков
@cache.memoize(timeout=TIMEOUT)
def create_language_pie_chart():
    language_counts = data['original_language'].value_counts().reset_index()
    language_counts.columns = ['original_language', 'count']
    top_languages = language_counts.head(10)  # Выбор только топ-10 языков

    fig = go.Figure(data=[go.Pie(labels=top_languages['original_language'],
                                 values=top_languages['count'],
                                 hole=0.5,
                                 marker=dict(colors=px.colors.qualitative.Pastel1,
                                             line=dict(color='#000000', width=2)),
                                 hoverinfo='label+percent',
                                 textinfo='value',
                                 pull=[0.1] * len(top_languages),  # Радиус выдвижения сегментов
                                 title='Доля фильмов по языкам')])

    fig.update_layout(
        title_x=0.5,  # Позиция заголовка по горизонтали
        title_y=0.95,  # Позиция заголовка по вертикали
        title_font_size=20,  # Размер шрифта заголовка
        title_font_color='navy',  # Цвет заголовка
        margin=dict(t=50, b=50, r=50, l=50),
        width=800,
        height=600,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return fig

@cache.memoize(timeout=TIMEOUT)
def create_revenue_line_plot():
    top_revenue_movies = data.nlargest(50, 'revenue')[['original_title', 'revenue']].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=top_revenue_movies['original_title'],
        y=top_revenue_movies['revenue'],
        mode='lines+markers',
        marker=dict(size=10, color='blue', symbol='circle'),
        line=dict(color='blue', width=2)
    ))
    fig.update_layout(
        title='Топ 50 фильмов по доходам',
        xaxis_title='Название фильма',
        yaxis_title='Доход',
        xaxis=dict(tickangle=45),
        margin=dict(t=50, b=150, r=50, l=50),
        width=1200,
        height=600,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return fig

@cache.memoize(timeout=TIMEOUT)
# Функция для создания графика топ 50 фильмов по бюджету
def create_budget_top_chart():
    top_budget_movies = data.nlargest(50, 'budget')
    fig = go.Figure(go.Bar(
        x=top_budget_movies['original_title'],
        y=top_budget_movies['budget'],
        marker_color='blue'
    ))
    fig.update_layout(
        title='Топ 50 фильмов по бюджету',
        xaxis_title='Название фильма',
        yaxis_title='Бюджет',
        xaxis=dict(tickangle=45),
        margin=dict(t=50, b=150, r=50, l=50),
        width=1200,
        height=600,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return fig

@cache.memoize(timeout=TIMEOUT)
def create_popularity_line_plot():
    # Подготовка данных
    year_counts = data['release_date'].str[:4].value_counts().reset_index()
    year_counts.columns = ['release_year', 'count']
    year_counts = year_counts.sort_values(by='release_year')

    # Построение графика
    fig = px.scatter(year_counts, x='release_year', y='count', title="Количество фильмов по годам",
                     labels={'release_year': 'Год', 'count': 'Количество фильмов'},
                     color='count', color_continuous_scale='Cividis')

    fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=0.5, color='White')))

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )

    return fig

@cache.memoize(timeout=TIMEOUT)
def create_vote_average_histogram():
    # Исключаем строки с оценкой 0
    data_filtered = data[data['vote_average'] != 0]

    # Группировка данных по средней оценке и подсчет количества фильмов для каждой оценки
    vote_counts = data_filtered['vote_average'].value_counts().reset_index()
    vote_counts.columns = ['vote_average', 'count']

    fig = go.Figure(go.Bar(
        x=vote_counts['vote_average'],
        y=vote_counts['count'],
        marker_color='orange'  # Устанавливаем цвет на тускло-оранжевый
    ))
    fig.update_layout(
        title='Распределение средних оценок фильмов',
        xaxis_title='Средняя оценка',
        yaxis_title='Количество фильмов',
        margin=dict(t=50, b=150, r=50, l=50),
        width=1200,
        height=600,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return fig

# Определение бокового меню
sidebar = html.Div(
    [
        html.H2("Меню", className="sidebar-title"),
        html.Hr(),
        dcc.Link(html.Button('Распределение фильмов по языкам', className="sidebar-button"), href="/page-1"),
        dcc.Link(html.Button('Топ 50 фильмов по доходам', className="sidebar-button"), href="/page-2"),
        dcc.Link(html.Button('Топ 50 фильмов по бюджету', className="sidebar-button"), href="/page-3"),
        dcc.Link(html.Button('Рост числа фильмов со временем', className="sidebar-button"), href="/page-4"),
        dcc.Link(html.Button('Средние оценки фильмов', className="sidebar-button"), href="/page-5"),
        dcc.Link(html.Button('Информация о фильмах', className="sidebar-button"), href="/page-6"),
    ],
    className="sidebar"
)

# Определение макета страниц
content = html.Div(id='page-content', className='page-content', style={'margin-left': '22%', 'background-color': 'black', 'color': 'white'})

# Начальная разметка приложения
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content
], style={'background-color': 'black', 'color': 'white'})

# Функция для создания общей структуры страницы
def create_page_layout(title, graph_id, graph_function):
    return html.Div(
        children=[
            html.H1(title, style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id=graph_id, figure=graph_function(), style={'margin': '0 auto', 'display': 'block'})
        ],
        style={'width': '80%', 'margin': '0 auto'}
    )

# Описание страниц
page_1_layout = create_page_layout('Распределение фильмов по языкам', 'language-pie-chart', create_language_pie_chart)
page_2_layout = create_page_layout('Топ 50 фильмов по доходам', 'revenue-line-plot', create_revenue_line_plot)
page_3_layout = create_page_layout('Топ 50 фильмов по бюджету', 'budget-top-chart', create_budget_top_chart)
page_4_layout = create_page_layout('Рост числа фильмов со временем', 'popularity-line-plot', create_popularity_line_plot)
page_5_layout = create_page_layout('Средние оценки фильмов', 'vote-average-histogram', create_vote_average_histogram)

page_6_layout = html.Div(
    children=[
        html.H1('Информация о фильмах', style={'color': 'white', 'textAlign': 'center'}),  # Центрирование заголовка
        dcc.Dropdown(
            id='movie-dropdown',
            options=[{'label': title, 'value': title} for title in data['original_title'].unique()],
            placeholder="Выберите фильм",
            style={'color': 'black'}
        ),
        html.Div(id='movie-info'),
        dcc.Graph(id='vote-gauge', style={'display': 'none'})
    ],
    style={'background-color': 'black', 'color': 'white'}
)
# Описание начальной страницы
welcome_layout = html.Div(
    [
        html.H1("Добро пожаловать!", style={'textAlign': 'center', 'marginTop': '10vh'}),
        html.H3("Выберите интересующую Вас статистику по фильмам", style={'textAlign': 'center'}),
        # Добавление изображения на весь экран
        html.Img(src="/static/start.jpg", style={'width': '100%', 'height': '100vh'}),
    ]
)
# Обработка навигации
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return welcome_layout
    elif pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-4':
        return page_4_layout
    elif pathname == '/page-5':
        return page_5_layout
    elif pathname == '/page-6':
        return page_6_layout
    else:
        return html.Div([
            html.H1('404'),
            html.P('Страница не найдена')
        ])

# Обработка обновления графиков
@app.callback(Output('language-pie-chart', 'figure'),
              Input('url', 'pathname'))
def update_language_pie_chart(pathname):
    if pathname == '/page-1':
        return create_language_pie_chart()
    return {}

@app.callback(Output('revenue-line-plot', 'figure'),
              Input('url', 'pathname'))
def update_revenue_line_plot(pathname):
    if pathname == '/page-2':
        return create_revenue_line_plot()
    return {}
@app.callback(Output('runtime-histogram', 'figure'),
              Input('url', 'pathname'))
def update_runtime_histogram(pathname):
    if pathname == '/page-3':
        return create_runtime_histogram()
    return {}

@app.callback(Output('popularity-line-plot', 'figure'),
              Input('url', 'pathname'))
def update_popularity_line_plot(pathname):
    if pathname == '/page-4':
        return create_popularity_line_plot()
    return {}

@app.callback(Output('vote-average-histogram', 'figure'),
              Input('url', 'pathname'))
def update_vote_average_histogram(pathname):
    if pathname == '/page-5':
        return create_vote_average_histogram()
    return {}

# Обработка выбора фильма из выпадающего меню и обновление спидометра
# Обработка выбора фильма из выпадающего меню и обновление спидометра
@app.callback(
    [Output('movie-info', 'children'), Output('vote-gauge', 'figure'), Output('vote-gauge', 'style')],
    [Input('movie-dropdown', 'value')]
)
def display_movie_info(selected_movie):
    if selected_movie is None:
        return html.P("Пожалуйста, выберите фильм из выпадающего меню.", style={'color': 'white'}), {}, {'display': 'none'}

    movie = data[data['original_title'] == selected_movie].iloc[0]

    info = html.Div([
        html.H3(movie['original_title'], style={'color': 'white', 'textAlign': 'center'}),  # Центрирование текста
        html.P(f"Описание: {movie['overview']}", style={'color': 'white'}),
    ], style={'textAlign': 'center'})  # Центрирование заголовка

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=movie['vote_average'],
        title={'text': "Средняя оценка"},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 2], 'color': "red"},
                {'range': [2, 4], 'color': "orange"},
                {'range': [4, 6], 'color': "yellow"},
                {'range': [6, 8], 'color': "lightgreen"},
                {'range': [8, 10], 'color': "green"},
            ]
        }
    ))

    gauge.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )

    return info, gauge, {'display': 'block'}
