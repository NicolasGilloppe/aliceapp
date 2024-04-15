import streamlit as st
import streamlit_pandas as sp
import pandas as pd



# Config
def main():
    menu = ['Home', 'Predictions', 'Alice Historical Datas', 'Download']
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Home':
        st.subheader('Home Page')
        st.write('Welcome to Alice!')
        st.write('Here You can find data-driven predictions on your daily football games!')   
    if choice == 'Predictions':
        st.subheader('Predictions')
        champ_by_bookie = {'Unibet': ['Germany', 'Germany2', 'England', 'England2', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Scotland', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Portugal2', 'Sweden', 'Switzerland', 'Turkey'],
                   'Stake': ['England', 'England2', 'England3', 'England4', 'Germany', 'Germany2', 'Spain', 'Spain2', 'Italy', 'Italy2', 'France', 'France2', 'Netherlands', 'Netherlands2', 'Portugal', 'Portugal2', 'Argentina', 'Austria', 'Australia', 'Brazil', 'Brazil2', 'Chile', 'China', 'Denmark', 'Japan', 'Japan2', 'Mexico', 'Norway', 'Saudi Arabia', 'Scotland', 'Sweden', 'Switzerland', 'Turkey', 'Usa'],
                   'Betclic': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Turkey', 'Switzerland'],
                   'Winamax': ['Germany', 'Germany2', 'England', 'England2', 'Saudi Arabia', 'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Chile', 'China', 'Croatia', 'Denmark', 'Spain', 'Spain2', 'Usa', 'France', 'France2', 'Italy', 'Italy2', 'Japan', 'Mexico', 'Norway', 'Netherlands', 'Portugal', 'Sweden', 'Switzerland', 'Turkey']
                   }
        df = pd.read_excel('Alice.xlsx')
        df = df.drop(df.columns[0], axis=1)
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
        st.write(df[df['Pays'].isin(champ_list)])

        
        lexique = pd.DataFrame(
            {'Alice Naming': ['Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 
                            'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15'],
            'Bet Signification': ['Home team win', 'Draw', 'Away team win', 'Home or Draw', 'Draw or Away',
                            'Over 2.5 goal', 'Under 2.5 goal', 'Both Team To Score', 'One Or Both Team To Not Score',
                            'Home win & Over 1.5 goal', 'Away win & over 1.5 goal']}
        )
        st.table(lexique)
    elif choice == 'Alice Historical Datas':
        st.subheader('Alice Performance')
        url = f"https://docs.google.com/spreadsheets/d/1k-khn63iYWNiDsC9iHVWlQXl1T_LZ1sE7doEptvJtrU/gviz/tq?tqx=out:csv&sheet=Tracking"        
        df = pd.read_csv(url, dtype=str)
        if st.button('Show Alice Historical Results'):
            histo = df[['Date', 'Home', 'Away', 'Country', 'Bet', 'Odds', 'Stake', 'Result', 'Profit', 'BK']]
            st.markdown(histo.style.hide(axis="index").to_html(), unsafe_allow_html=True)



if __name__ == '__main__':
    main()





