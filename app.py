from flask import Flask, request, render_template
import pronotepy
from pronotepy.ent import ac_orleans_tours
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        user_name = request.form.get('nom')
        password = request.form.get('password')

        try :

            client = pronotepy.Client(
                'https://0450047g.index-education.net/pronote/eleve.html',
                username=user_name, # votre identifiant ENT !!!
                password=password, # votre mot de passe
                ent=ac_orleans_tours)
        
        except :
            return render_template('fail.html')
        
        subjects = []
        averages = []
        class_averages = []
        meilleurs_moyennes = []


        for moyenne in client.current_period.averages :
            averages.append(moyenne.student)
            subjects.append(moyenne.subject.name)
            class_averages.append(moyenne.class_average)
            meilleurs_moyennes.append(moyenne.max)


        def convert(liste) :
            for l in range(len(liste)) :
                liste[l] = liste[l].replace(',','.')
                nb = float(liste[l])
                liste[l] = nb
            return liste

        averages = convert(averages)
        class_averages = convert(class_averages)
        meilleurs_moyennes = convert(meilleurs_moyennes)

        groupe = []
        for x in range(len(subjects)*3) :
            if x < len(subjects) :
                groupe.append('Vos moyennes')
            
            elif x >= (len(subjects)) and x < (len(subjects)*2) :
                groupe.append('Moyennes de classe')
            
            else :
                groupe.append('Meilleures moyennes')


        df = pd.DataFrame(dict(
            value = averages+class_averages+meilleurs_moyennes,
            variable = subjects+subjects+subjects,
            group = groupe))
                
        fig = px.line_polar(df, r = 'value', theta = 'variable', line_close = True,
                            markers = True,text = 'value', color = 'group')


        title = f"Moyenne générale : {client.current_period.overall_average} ||  Moyenne générale de la classe : {client.current_period.class_overall_average}"
        max_limit = 20
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max_limit]
                ),
            ),
            title=title,  # Titre du graphique
            title_x=0.47,  # Position horizontale du titre
            title_y=0.02,  # Position verticale du titre (au-dessus du graphique)
        )

        fig.update_traces(textposition = 'top center')

        graph_html = fig.to_html(full_html = False)

        return render_template('graphique.html', graph_html = graph_html)

        # Faire quelque chose avec les données, par exemple, les imprimer côté serveur

        # Vous pouvez également passer ces données à votre modèle ou effectuer d'autres opérations

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000 ,debug=True)