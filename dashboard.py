from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
import streamlit_pandas as sp
import pycountry
import pytz
import re
import datetime
import plotly.express as px

champ_by_bookie = {'Unibet': ['Germany', 'Germany2', 'England', 'England2', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Portugal2', 'Sweden', 'Switzerland', 'Turkey'],
                   'Stake': ['England', 'England2', 'England3', 'England4', 'Germany', 'Germany2', 'Spain', 'Spain2', 'Italy', 'Italy2', 'France', 'France2', 'Netherlands', 'Netherlands2', 'Portugal', 'Portugal2', 'Argentina', 'Austria', 'Australia', 'Brazil', 'Brazil2', 'Chile', 'China', 'Denmark', 'Japan', 'Japan2', 'Mexico', 'Norway', 'Saudi Arabia', 'Scotland', 'Sweden', 'Switzerland', 'Turkey', 'Usa'],
                   'Winamax': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Romania', 'Sweden', 'Switzerland', 'Turkey'],
                   'Betclic': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Romania', 'Sweden', 'Switzerland', 'Turkey']
                   }

# Connect to Mongo
uri = "mongodb+srv://nicolasgilloppe:s0S8eaYt0mIMdYE7@alicedb.eqrplwk.mongodb.net/?retryWrites=true&w=majority&appName=alicedb"
cluster = MongoClient(uri)
db = cluster["UsersDb"]
collection = db['Users']

@st.cache_data(ttl=300)
def get_datas(clu, database):
    return pd.DataFrame(list(MongoClient(st.secrets["uri"], connectTimeoutMS=30000, socketTimeoutMS=30000)[clu][database].find({})))


@st.cache_data(ttl=300)
def get_user_picks(username):
    db = cluster["UsersDb"]
    collection = db['Users']
    result = collection.find_one({'_id': username})
    books = result.get('Books')
    bk = result.get('Bankroll')

    db = cluster["alicedb"]
    collection = db['wr_bets']
    wrb = pd.DataFrame(list(collection.find({}))).drop('_id', axis=1)

    collection = db['wr_pays']
    wrp = pd.DataFrame(list(collection.find({}))).drop('_id', axis=1)

    collection = db['odds_1']
    df = pd.DataFrame(list(collection.find({}))).drop('_id', axis=1)
    covered = []

    for book in books:
        for _ in champ_by_bookie[book]:
            if _ not in covered:
                covered.append(_)

    df = df[df['Pays'].isin(covered)]
    missed = df[~df['Pays'].isin(covered)]
    
    for index, row in df.iterrows():
        max_odd = 0
        selected_bookmaker = None
        for book in books:
            odds = float(row[f'Odds_{book}'])
            if odds > max_odd:
                max_odd = odds
                selected_bookmaker = book

        df.at[index, 'Max_Odd'] = max_odd
        df.at[index, 'Selected_Bookmaker'] = selected_bookmaker

        coeff = wrb[wrb['Bets'] == row['Bets']]['Pick'].values[0] + wrp[wrp['Pays'] == row['Pays']]['Pick'].values[0]

        if max_odd < 1.6:
            coeff += 1
        elif max_odd < 2:
            coeff += 0.5

        df.at[index, 'Coeff'] = coeff
        df.at[index, 'Mise'] = float(bk) * (float(coeff / 100))

        df = df[['Date', 'Time', 'Champ', 'Home', 'Away', 'Bets', 'Selected_Bookmaker', f'{selected_bookmaker}_Url', 'Max_Odd', 'Mise']]
        
        data = df.to_dict(orient="records")
        db = cluster["UsersDb"]
        collection = db[f'{username}']
        collection.insert_many(data)

        df.columns = ['Date', 'Time', 'Champ', 'Home', 'Away', 'Bets', 'Bookmaker', 'Url', 'Odd', 'Mise']
        return df

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

def login(session_state):
    email = st.text_input('Email Address')
    password = st.text_input('Password', type='password')
    
    butt = st.button('Login')
    if butt:
        if email and password:
            result = collection.find_one({'_id': email})
            if result is not None:
                real_password = result.get('password')
                if password != real_password:
                    st.write('Password Invalid')
                else:
                    session_state.is_user_logged = True
                    session_state.user_data = result
                    st.write('You are now Logged In')
            else:
                st.write('No Account found for This Email')
        else:
            st.write('Please enter Email and Password')

def signup():
    country_code_list = [country.alpha_2 for country in pycountry.countries]
    country_names = [country.name for country in pycountry.countries]
    country_name_code_dict = dict(zip(country_names, country_code_list))

    email = st.text_input('Email Adress', key='email_input')
    if email:
        if not is_valid_email(email):
            st.warning('Please provide a valid email address')
            return
    name = st.text_input('Name', key='name_input')
    password = st.text_input('Password', type='password', key='password_input')
    conf_password = st.text_input('Confirm Your Password', type='password', key='password_check_input')
    selected_country_name = st.selectbox('Country', country_names)
    selected_country_code = country_name_code_dict[selected_country_name]
    try:
        country_timezone = pytz.country_timezones[selected_country_code][0]
        utc_offset_str = pytz.timezone(country_timezone).localize(pytz.datetime.datetime.now()).strftime('%z')
        if utc_offset_str[0] == '+':
            utc = float(utc_offset_str[1:]) / 100
        elif utc_offset_str[0] == '-':
            utc = -float(utc_offset_str[1:]) / 100
        else:
            utc = 0
    except KeyError:
        utc = 0

    bankroll = st.text_input('Please Enter Your Bankroll', key='bk_input')
    books = st.multiselect('Select Bookmakers:', ['Stake', 'Unibet', 'Betclic', 'Winamax'])
    
    good_bk = False

    try: 
        float(bankroll)
        good_bk = True
    except:
        if bankroll is None:
            st.write('Please Enter A Valid Number')

    if password and conf_password and password != conf_password:
        st.write('### Please enter the same Password!!')
    elif password and conf_password and email and password == conf_password and good_bk and name:
        butt = st.button('Sign Up')
        if butt:
            datas = {'_id': email, 'name': name, 'password': password, 'Utc': utc, 'Bankroll': bankroll, 'Books': books}
            collection.insert_one(datas)
            st.write('Your Account Has Been Created Succesfully. You Can Now Login')

def main():
    st.write("<h2 style='text-align: center; font-size: 80px;'>Welcome to Alice</h2>", unsafe_allow_html=True)
    st.write("<h2 style='text-align: center; font-size: 15px; color: cyan;'>Your-all-in one personal betting algorithm</h2>", unsafe_allow_html=True)
    st.write('')
    st.write('')
    st.write('')
    col1, col2 = st.columns(2)

    with col1:
        st.write("<h2 style='text-align: center; font-size: 30px;'>Login</h2>", unsafe_allow_html=True)
        session_state = get_session_state()
        login(session_state)
    with col2:
        st.write("<h2 style='text-align: center; font-size: 30px;'>Sign Up</h2>", unsafe_allow_html=True)
        signup()

    if session_state.is_user_logged:
        user_data = session_state.user_data
        user_name = user_data.get('name')
        user_username = user_data.get('_id')
        user_utc = int(user_data.get('Utc'))
        user_bk = user_data.get('Bankroll')
        user_bookies = user_data['Books']
        df = get_datas('alicedb', f'Alice_{user_utc}')
        df = df.drop(df.columns[0], axis=1)
        wr_pays = get_datas('alicedb', 'wr_pays')
        wr_bets = get_datas('alicedb', 'wr_bets')
        menu = ['Predictions', "Today's Picks", 'Historical Datas', 'Personal Picks', 'Download']
        choice = st.selectbox("Menu", menu)

        if choice == 'Predictions':

            st.write('You can get your Daily Picks Here')
            st.title('Predictions')
            tz = pytz.timezone('Europe/Paris')
            today = datetime.datetime.now(tz).date()
            today = today.strftime('%d-%m-%y')

            if df['Date'][0] != today:
                st.subheader('There is no matchs today!')
            else:
                round_cols = ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']
                df[round_cols] = df[round_cols].round(2)
                champ_by_bookie = {'Unibet': ['Germany', 'Germany2', 'England', 'England2', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Portugal2', 'Sweden', 'Switzerland', 'Turkey'],
                        'Stake': ['England', 'England2', 'England3', 'England4', 'Germany', 'Germany2', 'Spain', 'Spain2', 'Italy', 'Italy2', 'France', 'France2', 'Netherlands', 'Netherlands2', 'Portugal', 'Portugal2', 'Argentina', 'Austria', 'Australia', 'Brazil', 'Brazil2', 'Chile', 'China', 'Denmark', 'Japan', 'Japan2', 'Mexico', 'Norway', 'Saudi Arabia', 'Scotland', 'Sweden', 'Switzerland', 'Turkey', 'Usa', 'Croatia'],
                        'Betclic': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Turkey', 'Switzerland'],
                        'Winamax': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Switzerland', 'Turkey']
                        }
        
                champ_list = []
                for book in user_bookies:
                    champs = champ_by_bookie[book]
                    for _ in champs:
                        if _ not in champ_list:
                            champ_list.append(_)
        
                create_data = {'Pays': 'multiselect'}
                all_widgets = sp.create_widgets(df[['Pays', 'Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']], create_data)
                df = sp.filter_df(df, all_widgets)
                df = df[df['Pays'].isin(champ_list)]
                
                for col in round_cols:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}")
        
                st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                
                lexique = pd.DataFrame(
                    {'Alice Naming': ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 
                                    'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15'],
                    'Bet Signification': ['Home team win', 'Draw', 'Away team win', 'Home or Draw', 'Draw or Away',
                                    'Over 2.5 goal', 'Under 2.5 goal', 'Both Team To Score', 'One Or Both Team To Not Score',
                                    'Home win & Over 1.5 goal', 'Away win & over 1.5 goal']}
                )
        
                check_lex = st.checkbox(label='Show Bets Signification')
                if check_lex:
                    st.markdown(lexique.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        elif choice == 'Historical Datas':
            st.title('Alice Performance')
            check_box = st.checkbox(label='Show Historical Results')
            st.link_button(label='Link to Alice historical results', url='https://docs.google.com/spreadsheets/d/1k-khn63iYWNiDsC9iHVWlQXl1T_LZ1sE7doEptvJtrU/edit#gid=0')
            url = "https://docs.google.com/spreadsheets/d/1k-khn63iYWNiDsC9iHVWlQXl1T_LZ1sE7doEptvJtrU/gviz/tq?tqx=out:csv&sheet=Tracking"        
            df = pd.read_csv(url, dtype=str)
            df = df[['Date', 'Home', 'Away', 'Country', 'Bet', 'Odds', 'Stake', 'Result', 'Profit', 'BK']].dropna()
            
            bk = df['BK'].to_list()
            last_bk = float(bk[-1].replace(',', '.')) - 100
            bk = [float(value.replace(',', '.')) for value in bk]
            plotly_fig = px.line(df, x=df.index, y=bk, title='Alice Return on Investment Over Time')
            plotly_fig.update_yaxes(title_text='Portfolio')
            plotly_fig.update_xaxes(title_text='Number of Bets')
            st.write(f'Alice generated a {last_bk}% ROI in {len(df)} bets!')
            wins = len(df[df['Result'] == '1'])
            st.write(f'With an average win rate of {(round(float(wins) / float(len(df)), 2)) * 100}%!!')
            st.plotly_chart(plotly_fig)


            if check_box:
                histo = df.copy()
                st.markdown(histo.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        elif choice == 'Download':
            st.write("Click on the Download Button below to get Alice's probabilities in an external file")
            
            def convert_df(df):
                return df.to_csv().encode('utf-8')
            
            csv = convert_df(df)

            st.download_button(label='Download as CSV', data=csv, file_name='Alice.csv', mime='text/csv')

        elif choice == "Today's Picks":
            
            def get_today_based_on_utc(user_utc):
                utc_now = datetime.datetime.now(pytz.utc)
                utc_offset = datetime.timedelta(hours=user_utc)
                user_now = utc_now + utc_offset
                user_tz = pytz.timezone('Europe/Paris')
                user_today = user_now.astimezone(user_tz).date()
                return user_today.strftime('%d-%m-%y')
            
            today = get_today_based_on_utc(user_utc)

            if df['Date'][0] != today:
                st.subheader('There is no matchs today!')
            else:
                selection = pd.DataFrame(columns=['Time', 'Champ', 'Home', 'Away', 'Pays', 'Bets', 'Conf'])
                for index, row in df.iterrows():
                    datas = [row['Time'], row['Champ'], row['Home'], row['Away'], row['Pays']]
                    for _ in ['H', 'D', 'A', 'HD', 'DA', 'O', 'U', 'BTTS', 'NoBTTS', 'Ho15', 'Ao15']:
                        conf = 0
                        try:
                            bets = wr_bets[_]
                        except:
                            bets = 0
                        
                        try:
                            pays = wr_pays[row['Pays']]
                        except:
                            pays = 0
        
                        if float(bets) >= 0.8:
                            conf += 1
                        elif float(bets) >= 0.7:
                            conf += 0.75
                        elif float(bets) >= 0.6:
                            conf += 0.5
                        
                        if float(pays) >= 0.8:
                            conf += 1
                        elif float(pays) >= 0.7:
                            conf += 0.75
                        elif float(pays) >= 0.6:
                            conf += 0.5
        
                        if float(row[f'Proba_{_}']) >= 0.8:
                            conf += 1
                        elif float(row[f'Proba_{_}']) >= 0.7:
                            conf += 0.75
                        elif float(row[f'Proba_{_}']) >= 0.6:
                            conf += 0.5
                        
                        selection.loc[len(selection)] = datas + [_, conf]
                
                selection = selection[selection['Conf'] >= 2.25]
                if len(selection) > 3:
                    nombre_lignes_a_supprimer = len(selection) - 3
                    indices_lignes_a_supprimer = selection.sample(n=nombre_lignes_a_supprimer).index
                    selection = selection.drop(indices_lignes_a_supprimer)
        
                st.markdown(selection.drop('Conf', axis=1).style.hide(axis="index").to_html(), unsafe_allow_html=True)
                content = """
                Please note that while these selections reflect Alice's preferences, she may not necessarily place bets on all of them. They serve as indicative suggestions for your personal betting decisions. Various factors, including odds, bankroll management, Alice's recent performance, and more, should be considered before placing any wagers. Additionally, these picks may differ from the daily recommendations provided under your personnal betting strategy
                """
                st.write('')
                st.write('')
                st.write(content)
        elif choice == 'Personal Picks':
            user_picks = get_user_picks(user_username)
            
            for index, row in user_picks.iterrows():
                st.markdown(f"[{row['Time']}: {row['Home']} vs {row['Away']}, stake {row['Mise']}€ on {row['Bets']} @ {row['Odd']}. Bookmaker is {row['Bookmaker']}](row['Url'])", unsafe_allow_html=False)



if __name__ == '__main__':
    main()
