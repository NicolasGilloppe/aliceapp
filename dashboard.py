import streamlit as st
import streamlit_pandas as sp
import pandas as pd
import plotly.express as px
from pymongo.mongo_client import MongoClient
import datetime
import pytz


@st.cache_data(ttl=3600)
def get_datas(clu, database):
    return pd.DataFrame(list(MongoClient(st.secrets["uri"], connectTimeoutMS=30000, socketTimeoutMS=30000)[clu][database].find({})))


# Config
def main():
    df = get_datas('alicedb', 'Alicetest')
    df = df.drop(df.columns[0], axis=1)
    wr_pays = get_datas('alicedb', 'wr_pays')
    wr_bets = get_datas('alicedb', 'wr_bets')
    menu = ['Home', 'Predictions', 'Alice Picks of the Day', 'Alice Historical Datas', 'Download']
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == 'Home':
        st.subheader('Home Page')
        st.write('Welcome to Alice!')
        st.write('Here You can find data-driven predictions on your daily football games!')   
    if choice == 'Predictions':
        st.subheader('Predictions')
        tz = pytz.timezone('Europe/Paris')
        today = datetime.datetime.now(tz).date()
        today = today.strftime('%d-%m-%y')

        if df['Date'][0] != today:
            st.write('There is no matchs today!')
        else:
            round_cols = ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']
            df[round_cols] = df[round_cols].round(2)
            champ_by_bookie = {'Unibet': ['Germany', 'Germany2', 'England', 'England2', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Portugal2', 'Sweden', 'Switzerland', 'Turkey'],
                       'Stake': ['England', 'England2', 'England3', 'England4', 'Germany', 'Germany2', 'Spain', 'Spain2', 'Italy', 'Italy2', 'France', 'France2', 'Netherlands', 'Netherlands2', 'Portugal', 'Portugal2', 'Argentina', 'Austria', 'Australia', 'Brazil', 'Brazil2', 'Chile', 'China', 'Denmark', 'Japan', 'Japan2', 'Mexico', 'Norway', 'Saudi Arabia', 'Scotland', 'Sweden', 'Switzerland', 'Turkey', 'Usa', 'Croatia'],
                       'Betclic': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Turkey', 'Switzerland'],
                       'Winamax': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Switzerland', 'Turkey']
                       }
    
            bookmaker_options = ['Stake', 'Unibet', 'Betclic', 'Winamax']
            selected_bookmakers = st.multiselect("Select Bookmaker", bookmaker_options)
            champ_list = []
            for book in selected_bookmakers:
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

    elif choice == 'Alice Historical Datas':
        st.subheader('Alice Performance')
        check_box = st.checkbox(label='Show Alice Historical Results')
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

    elif choice == 'Alice Picks of the Day':
        st.subheader("Today's Alice Picks Selection")

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

    elif choice == 'Download':
        st.write("Click on the Download Button below to get Alice's probabilities in an external file")
        
        def convert_df(df):
            return df.to_csv().encode('utf-8')
        
        csv = convert_df(df)

        st.download_button(label='Download as CSV', data=csv, file_name='Alice.csv', mime='text/csv')
    






if __name__ == '__main__':
    main()





