from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
import streamlit_pandas as sp
import pytz
import re
import datetime
import plotly.express as px
import bcrypt
import plotly.graph_objects as go

def get_max(df, bet):
    columns = [f'Stake_{bet}', f'Unibet_{bet}', f'Betclic_{bet}', f'Winamax_{bet}']
    values = [float(df[col].values[0]) for col in columns]
    max_value = max(values)
    max_url = f"{columns[values.index(max_value)].replace(f'_{bet}', '')}_Url"
    name = max_url.replace('_Url', '')
    return max_value, max_url, name

def get_odds(df, bet):
    columns = [f'Stake_{bet}', f'Unibet_{bet}', f'Betclic_{bet}', f'Winamax_{bet}']
    values = [float(df[col].values[0]) for col in columns]

    return values


def add_space(i):
    for _ in range(1, i):
        st.write('')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

@st.cache_data(ttl=300)
def get_datas(clu, database):
    return pd.DataFrame(list(MongoClient(st.secrets["uri"], connectTimeoutMS=30000, socketTimeoutMS=30000)[clu][database].find({})))

class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def get_session_state():
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = SessionState(is_user_logged=False, user_data=None)
    return st.session_state['session_state']

def get_user_infos(clu, database, email):
    return MongoClient(st.secrets["uri"], connectTimeoutMS=30000, socketTimeoutMS=30000)[clu][database].find_one({'_id': email})

def insert_datas(clu, database, datas):
    MongoClient(st.secrets["uri"], connectTimeoutMS=30000, socketTimeoutMS=30000)[clu][database].insert_one(datas)

def login(session_state):
    email = st.text_input('Email Address')
    password = st.text_input('Password', type='password')   
    if st.button('Login'):
        if email and password:
            result = get_user_infos('UsersDb', 'Users', email)
            if result is not None:
                if verify_password(password, result.get('password')):
                    session_state.is_user_logged = True
                    session_state.user_data = result
                    session_state = get_session_state()
                    st.write('You are now Logged In. Please click on the Login button once more!')
                else:
                    st.write('Password Invalid')
            else:
                st.write('No Account found for This Email')
        else:
            st.write('Please enter Email and Password')

def signup():
    email = st.text_input('Email Address', key='email_input')
    name = st.text_input('Name', key='name_input')
    password = st.text_input('Password', type='password', key='password_input')
    conf_password = st.text_input('Confirm Your Password', type='password', key='password_check_input')
    books = st.multiselect('Select Bookmakers:', ['Stake', 'Unibet', 'Betclic', 'Winamax'])

    if st.button('Sign Up'):
        if not is_valid_email(email):
            st.warning('Please provide a valid email address')
            return
        elif password and conf_password and password != conf_password:
            st.warning('Please enter the same password')
        elif password and conf_password and email and password == conf_password and name:
            insert_datas('UsersDb', 'Users', {'_id': email, 'name': name, 'password': hash_password(password), 'Books': books})
            st.write('Your Account Has Been Created Succesfully. You Can Now Login')

@st.cache_data(ttl=300)
def main():
    st.write("<h2 style='text-align: center; font-size: 80px;'>Welcome to Alice</h2>", unsafe_allow_html=True)
    st.write("<h2 style='text-align: center; font-size: 15px; color: cyan;'>Your-all-in one personal betting algorithm</h2>", unsafe_allow_html=True)
    add_space(4)

    session_state = get_session_state()

    if not session_state.is_user_logged:
        col1, col2 = st.columns(2)
        with col1:
            st.write("<h2 style='text-align: center; font-size: 30px;'>Login</h2>", unsafe_allow_html=True)
            login(session_state)
            session_state = get_session_state()
        with col2:
            st.write("<h2 style='text-align: center; font-size: 30px;'>Sign Up</h2>", unsafe_allow_html=True)
            signup()
        
    else:
        user_data = session_state.user_data
        user_name = user_data.get('name')
        user_username = user_data.get('_id')
        user_bookies = user_data['Books']
        df = get_datas('alicedb', 'Alice_1')

        champ_by_bookie = {'Unibet': ['Germany', 'Germany2', 'England', 'England2', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Portugal2', 'Sweden', 'Switzerland', 'Turkey', 'Saudi Arabia'],
                        'Stake': ['England', 'England2', 'England3', 'England4', 'Germany', 'Germany2', 'Spain', 'Spain2', 'Italy', 'Italy2', 'France', 'France2', 'Netherlands', 'Netherlands2', 'Portugal', 'Portugal2', 'Argentina', 'Austria', 'Australia', 'Brazil', 'Brazil2', 'Chile', 'China', 'Denmark', 'Japan', 'Japan2', 'Mexico', 'Norway', 'Saudi Arabia', 'Scotland', 'Sweden', 'Switzerland', 'Turkey', 'Usa', 'Croatia'],
                        'Betclic': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Turkey', 'Switzerland'],
                        'Winamax': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Switzerland', 'Turkey']
                        }
        
        champ_list = []
        for book in user_bookies:
            for _ in champ_by_bookie[book]:
                if _ not in champ_list:
                    champ_list.append(_)
        missed = df[~df['Pays'].isin(champ_list)]
        lexique = pd.DataFrame(
                    {'Alice Naming': ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 
                                    'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15'],
                    'Bet Signification': ['Home team win', 'Draw', 'Away team win', 'Home or Draw', 'Draw or Away',
                                    'Over 2.5 goal', 'Under 2.5 goal', 'Both Team To Score', 'One Or Both Team To Not Score',
                                    'Home win & Over 1.5 goal', 'Away win & over 1.5 goal']}
                )
        
        trans = pd.DataFrame(
                    {'Naming': ['MP', 'W', 'D', 'L', 'GF', 
                                    'GA', 'GD', 'GFPG', 'GAPG', 'AS', 'DS'],
                    'Signification': ['Number of matchs played', 'Wins', 'Draws', 'Losses', 'Number of Goal Scored',
                                    'Number of Goal Conceded', 'Goal Difference', 'Average Number of Goal Score per Game', 'Average Number of Goal Conceded per game',
                                    'Team Attack Strength Compared to League Average', 'Team Defensive Strength Compared to League Average']}
                )
        
        try:
            df = df.drop(df.columns[0], axis=1)
        except:
            pass
        choice = st.selectbox("Menu", ['Predictions', 'Advanced Statistics', "Today's Picks", 'Historical Datas', 'Download'])

        if choice == 'Predictions':
            st.write('You can get your Daily Picks Here')
            st.title('Predictions')

            if df['Date'][0] != datetime.datetime.now(pytz.timezone('Europe/Paris')).date().strftime('%d-%m-%y'):
                st.subheader('There is no matchs today!')
            else:
                round_cols = ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']
                df[round_cols] = df[round_cols].round(2)
        
                df = sp.filter_df(df, sp.create_widgets(df[['Pays', 'Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']], {'Pays': 'multiselect'}))
                
                for col in round_cols:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}")
        
                st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        
                if st.checkbox(label='Show Bets Signification'):
                    st.markdown(lexique.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        elif choice == 'Historical Datas':
            url = "https://docs.google.com/spreadsheets/d/1k-khn63iYWNiDsC9iHVWlQXl1T_LZ1sE7doEptvJtrU/gviz/tq?tqx=out:csv&sheet=Tracking"        
            historical = pd.read_csv(url, dtype=str)[['Date', 'Home', 'Away', 'Country', 'Bet', 'Odds', 'Stake', 'Result', 'Profit', 'BK']].dropna()
            histo_bk = historical['BK'].to_list()
            histo_last_bk = float(histo_bk[-1].replace(',', '.')) - 100
            histo_bk = [float(value.replace(',', '.')) for value in histo_bk]
            plotly_fig = px.line(historical, x=historical.index, y=histo_bk, title='Alice Return on Investment Over Time')
            plotly_fig.update_yaxes(title_text='Portfolio')
            plotly_fig.update_xaxes(title_text='Number of Bets')
            st.title('Alice Performance')
            st.link_button(label='Link to Alice historical results', url='https://docs.google.com/spreadsheets/d/1k-khn63iYWNiDsC9iHVWlQXl1T_LZ1sE7doEptvJtrU/edit#gid=0')
            st.write(f"Alice generated a {round(float(histo_last_bk), 2)}% ROI in {len(historical)} bets, with an average win rate of {(round(float(len(historical[historical['Result'] == '1'])) / float(len(historical)), 2)) * 100}%!!")
            st.plotly_chart(plotly_fig)
            if st.checkbox(label='Show Historical Results'):
                st.markdown(historical.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        elif choice == 'Download':
            st.write("Click on the Download Button below to get Alice's probabilities in an external file")

            def convert_df(df):
                return df.to_csv().encode('utf-8')            
            st.download_button(label='Download as CSV', data=convert_df(df), file_name='Alice.csv', mime='text/csv')

        elif choice == "Today's Picks":
            user_picks = get_datas('alicedb', 'odds_1')
            rows_to_drop = []
            for index, row in user_picks.iterrows():
                c = 0
                for book in user_bookies:
                    if row[f'Odds_{book}'] not in ['', None, 0, 0.0, '0', '0.0']:
                        c += 1
                if c == 0:
                    rows_to_drop.append(index)
            user_picks.drop(rows_to_drop, inplace=True)
            if user_picks.empty or user_picks['Date'][0] != datetime.datetime.now().date().strftime('%d-%m-%y'):
                st.write("There's no matchs for you today!")
            else:
                bk = st.text_input('Enter your Bankroll:')
                try:
                    bk = float(bk)
                    for index, row in user_picks.iterrows():
                        odd = 0
                        for book in user_bookies:
                            odds = float(row[f'Odds_{book}'])
                            if odds > odd:
                                user_picks.at[index, 'Odd'] = odds
                                user_picks.at[index, 'Bookmaker'] = book

                    for index, row in user_picks.iterrows():
                        st.link_button(label= f"{row['Time']}: {row['Home']} vs {row['Away']}, bet {round(bk*(float(row['Coeff'])/100), 2)}€ on {row['Bets']} @ {row['Odd']}. Bookmaker is {row['Bookmaker']}", url= f"{row[f'{book}_Url']}")
                except ValueError:
                    st.warning('Veuillez entrer une Bankroll valide')
                    
                if st.checkbox(label='Show Bets Signification'):
                    st.markdown(lexique.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        
        elif choice == 'Advanced Statistics':
            datas = get_datas('alicedb', 'leaguesdb').drop(['_id'], axis=1).fillna(0)
            df['Match'] = '[' + df['Pays'] + '] / ' + df['Home'] + ' - ' + df['Away']
            unique_matches = df['Match'].unique()

            st.title('Select a Match')
            selected_match = st.selectbox('', unique_matches)
            spays = selected_match.split('] / ')[0][1:] if '] / ' in selected_match else None
            match_display = selected_match.split('] / ', 1)[1] if '] / ' in selected_match else selected_match
            shome, saway = match_display.split(' - ')
            if selected_match:
                hsel = datas[(datas['Squad'] == shome) & (datas['Pays'] == spays)]
                asel = datas[(datas['Squad'] == saway) & (datas['Pays'] == spays)]
                data = {
                    ' ': ['MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'GFPG', 'GAPG', 'AS', 'DS'],
                    shome: [hsel['MPH'].values[0], round(hsel['HW/MP'].values[0] * hsel['MPH'].values[0]), round(hsel['HD/MP'].values[0]*hsel['MPH'].values[0]), round(hsel['HL/MP'].values[0]*hsel['MPH'].values[0]), hsel['GFH'].values[0], hsel['GAH'].values[0], (hsel['GFH'].values[0] - hsel['GAH'].values[0]), hsel['HGFPG'].values[0], hsel['HGAPG'].values[0], hsel['HAS'].values[0], hsel['HDS'].values[0]],
                    saway: [asel['MPA'].values[0], round(asel['AW/MP'].values[0]*asel['MPA'].values[0]), round(asel['AD/MP'].values[0]*asel['MPA'].values[0]), round(asel['AL/MP'].values[0]*asel['MPA'].values[0]), asel['GFA'].values[0], asel['GAA'].values[0], (asel['GFA'].values[0] - asel['GAA'].values[0]), asel['AGFPG'].values[0], asel['AGAPG'].values[0], asel['AAS'].values[0], asel['ADS'].values[0]]
                }
                dff = pd.DataFrame(data)
                for col in [shome, saway]:
                    dff[col] = dff[col].apply(lambda x: f"{x:.2f}")
                st.subheader('Alice Predictions')
                temp = df[df['Home'] == shome]
                dic = pd.DataFrame({'Proba_Home': [temp['Proba_H'].values[0]], 'Proba_Draw': [temp['Proba_D'].values[0]], 'Proba_Away': [temp['Proba_A'].values[0]], 'Proba_HD': [temp['Proba_HD'].values[0]], 'Proba_DA': [temp['Proba_DA'].values[0]], 'Proba_Over': [temp['Proba_O'].values[0]], 'Proba_Under': [temp['Proba_U'].values[0]], 'Proba_BTTS': [temp['Proba_BTTS'].values[0]], 'Proba_NoBTTS': [temp['Proba_NoBTTS'].values[0]]})
                for col in ['Proba_Home', 'Proba_Draw', 'Proba_Away', 'Proba_HD', 'Proba_DA', 'Proba_Over', 'Proba_Under', 'Proba_BTTS', 'Proba_NoBTTS']:
                    dic[col] = dic[col].apply(lambda x: f"{x:.2f}")
                
                st.markdown(dic.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                add_space(3)
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader('Statistics')
                    add_space(3)
                    st.markdown(dff.style.hide(axis='index').to_html(), unsafe_allow_html=True)
                    if st.checkbox(label='Show Bets Signification'):
                        st.markdown(trans.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                with col2:
                    odds_df = get_datas('alicedb', 'odds_df').drop('_id', axis=1)
                    affi = {'Stake': 'https://stake.bet/?c=7AcXNyMl', 'Unibet': 'https://unibet.fr/myaccount/register.html?promo=LFQRK'}
                    odds_df = odds_df[odds_df['Home'] == shome]
                    st.subheader('Odds')
                    if not st.toggle('Switch to All Odds'):
                        for bet in ['Home', 'Draw', 'Away', 'HD', 'DA', 'Over', 'Under', 'BTTS', 'NoBTTS']:
                            od, od_url, bookie = get_max(odds_df, bet)
                            if bookie not in user_bookies and bookie in affi.keys():
                                st.link_button(label=f"{bet} @ {od} on {bookie}", url=affi[bookie])
                            else:
                                st.link_button(label=f"{bet} @ {od} on {bookie}", url=odds_df[od_url].values[0])
                    else:
                        for bet in ['Home', 'Draw', 'Away', 'HD', 'DA', 'Over', 'Under', 'BTTS', 'NoBTTS']:
                            st.subheader(bet)
                            co1, co2, co3, co4 = st.columns(4)
                            with co1:
                                val = odds_df[f'Stake_{bet}'].values[0]
                                st.write('Stake')
                                if 'Stake' not in user_bookies:
                                    st.link_button(label=f'{val}', url=affi['Stake'])
                                else:
                                    st.link_button(label=f'{val}', url= odds_df['Stake_Url'].values[0])
                            with co2:
                                val = odds_df[f'Unibet_{bet}'].values[0]
                                st.write('Unibet')
                                if 'Unibet' not in user_bookies:
                                    st.link_button(label=f'{val}', url=affi['Unibet'])
                                else:
                                    st.link_button(label=f'{val}', url= odds_df['Unibet_Url'].values[0])
                            with co3:
                                val = odds_df[f'Winamax_{bet}'].values[0]
                                st.write('Winamax')
                                st.link_button(label=f'{val}', url= odds_df['Winamax_Url'].values[0])
                            with co4:
                                val = odds_df[f'Betclic_{bet}'].values[0]
                                st.write('Betclic')
                                st.link_button(label=f'{val}', url= odds_df['Betclic_Url'].values[0])

                gr1, gr2 = st.columns(2)
                with gr1:
                    st.title(shome)
                    value1 = dff[dff[' '] == 'W'][shome].values[0]
                    value2 = dff[dff[' '] == 'D'][shome].values[0]
                    value3 = dff[dff[' '] == 'L'][shome].values[0]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['Win'], y=[value1], name='Win', marker_color='green'))
                    fig.add_trace(go.Bar(x=['Draw'], y=[value2], name='Draw', marker_color='grey'))
                    fig.add_trace(go.Bar(x=['Lose'], y=[value3], name='Lose', marker_color='red'))
                    fig.update_layout(title='Home Results',
                        barmode='group',
                        width=400,
                    )
                    st.plotly_chart(fig)

                    value1 = dff[dff[' '] == 'GFPG'][shome].values[0]
                    value2 = dff[dff[' '] == 'GAPG'][shome].values[0]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['Goal For'], y=[value1], name='', marker_color='Green'))
                    fig.add_trace(go.Bar(x=['Goal Against'], y=[value2], name='', marker_color='red'))
                    fig.update_layout(title='Average Goal per Home Game',
                        barmode='group',
                        width=400,
                    )
                    st.plotly_chart(fig)
                with gr2:
                    st.title(saway)
                    value1 = dff[dff[' '] == 'W'][saway].values[0]
                    value2 = dff[dff[' '] == 'D'][saway].values[0]
                    value3 = dff[dff[' '] == 'L'][saway].values[0]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['Win'], y=[value1], name='Lose', marker_color='green'))
                    fig.add_trace(go.Bar(x=['Draw'], y=[value2], name='Draw', marker_color='grey'))
                    fig.add_trace(go.Bar(x=['Lose'], y=[value3], name='Win', marker_color='red'))
                    fig.update_layout(title='Away Results',
                        barmode='group',
                        width=400,
                    )
                    st.plotly_chart(fig)

                    value1 = dff[dff[' '] == 'GFPG'][saway].values[0]
                    value2 = dff[dff[' '] == 'GAPG'][saway].values[0]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['Goal For'], y=[value1], name='', marker_color='Green'))
                    fig.add_trace(go.Bar(x=['Goal Against'], y=[value2], name='', marker_color='red'))
                    fig.update_layout(title='Average Goal per Away Game',
                        barmode='group',
                        width=400,
                    )
                    st.plotly_chart(fig)



if __name__ == '__main__':
    main()
