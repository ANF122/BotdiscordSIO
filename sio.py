import discord
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import random
import io
import contextlib
import traceback
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import time
import ast
from transformers import GPTNeoForCausalLM, AutoTokenizer
import torch
import os 
from flask import Flask
from threading import Thread
import threading
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# Créer une instance de Flask
app = Flask(__name__)   
USERNAME = os.getenv('BOT_USERNAME')
PASSWORD = os.getenv('BOT_PASSWORD')

# Charger les variables d'environnement
load_dotenv()
description = "Je suis un bot dédié à aider la classe de SIO1 en programmation."

# Initialisation globale du modèle et du tokenizer
model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
TOKEN = os.getenv('DISCORD_TOKEN')
# Base de connaissances
sujets = {
    "variables": {
        "explication": "Les variables sont des conteneurs pour stocker des données en programmation.",
        "exemple": "x = 5\nnom = 'Alice'\npi = 3.14",
        "exercice": "Créez trois variables : une pour votre âge, une pour votre nom, et une pour votre taille en mètres."
    },
    "boucles": {
        "explication": "Les boucles permettent de répéter des actions un certain nombre de fois ou tant qu'une condition est vraie.",
        "exemple": "for i in range(5):\n    print(i)\n\nwhile x < 10:\n    x += 1",
        "exercice": "Écrivez une boucle qui affiche les carrés des nombres de 1 à 5."
    },
    "fonctions": {
        "explication": "Les fonctions sont des blocs de code réutilisables qui effectuent une tâche spécifique.",
        "exemple": "def saluer(nom):\n    return f'Bonjour, {nom}!'\n\nprint(saluer('Alice'))",
        "exercice": "Créez une fonction qui prend deux nombres en paramètres et retourne leur somme."
    },
    "conditions": {
        "explication": "Les conditions permettent d'exécuter différents blocs de code selon que certaines conditions sont vraies ou fausses.",
        "exemple": "age = 18\nif age >= 18:\n    print('Majeur')\nelse:\n    print('Mineur')",
        "exercice": "Écrivez un programme qui détermine si un nombre est positif, négatif ou zéro."
    }
}

@tree.command(name="aide", description="Obtenez de l'aide sur un sujet de programmation")
@app_commands.choices(sujet=[
    app_commands.Choice(name=sujet, value=sujet) for sujet in sujets.keys()
])
async def aide(interaction: discord.Interaction, sujet: str):
    if sujet in sujets:
        embed = discord.Embed(title=f"Aide sur : {sujet}", color=discord.Color.blue())
        embed.add_field(name="Explication", value=sujets[sujet]["explication"], inline=False)
        embed.add_field(name="Exemple", value=f"```python\n{sujets[sujet]['exemple']}\n```", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Sujet non trouvé. Utilisez la complétion automatique pour voir les sujets disponibles.")

@tree.command(name="exercice", description="Obtenez un exercice de programmation")
@app_commands.choices(sujet=[
    app_commands.Choice(name=sujet, value=sujet) for sujet in sujets.keys()
])
async def exercice(interaction: discord.Interaction, sujet: str):
    if sujet in sujets:
        embed = discord.Embed(title=f"Exercice sur : {sujet}", color=discord.Color.green())
        embed.add_field(name="Exercice", value=sujets[sujet]["exercice"], inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Sujet non trouvé. Utilisez la complétion automatique pour voir les sujets disponibles.")

@tree.command(name="executer", description="Exécutez du code Python")
async def executer(interaction: discord.Interaction, code: str):
    await interaction.response.defer()
    
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code)
        result = output.getvalue()
        if result:
            await interaction.followup.send(f"Résultat:\n```\n{result}\n```")
        else:
            await interaction.followup.send("Le code s'est exécuté sans sortie.")
    except Exception as e:
        await interaction.followup.send(f"Erreur:\n```\n{traceback.format_exc()}\n```")

@tree.command(name="quiz", description="Répondez à un quiz de programmation")
async def quiz(interaction: discord.Interaction):
    questions = [
        {
            "question": "Quel est le résultat de `2 + 2 * 2` en Python ?",
            "options": ["4", "6", "8", "Erreur"],
            "correct": 1
        },
        {
            "question": "Quelle méthode est utilisée pour ajouter un élément à la fin d'une liste en Python ?",
            "options": [".add()", ".append()", ".insert()", ".extend()"],
            "correct": 1
        },
        {
            "question": "Comment déclare-t-on une fonction en Python ?",
            "options": ["function maFonction():", "def maFonction():", "maFonction():", "declare maFonction():"],
            "correct": 1
        }
    ]
    
    question = random.choice(questions)
    options_str = "\n".join([f"{i+1}. {option}" for i, option in enumerate(question["options"])])
    
    embed = discord.Embed(title="Quiz de programmation", description=question["question"], color=discord.Color.gold())
    embed.add_field(name="Options", value=options_str, inline=False)
    
    await interaction.response.send_message(embed=embed)
    
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit() and 1 <= int(m.content) <= len(question["options"])
    
    try:
        msg = await client.wait_for('message', check=check, timeout=30.0)
        if int(msg.content) - 1 == question["correct"]:
            await interaction.followup.send("Correct ! Bien joué !")
        else:
            await interaction.followup.send(f"Désolé, ce n'est pas correct. La bonne réponse était : {question['options'][question['correct']]}")
    except asyncio.TimeoutError:
        await interaction.followup.send("Temps écoulé ! N'hésitez pas à réessayer avec /quiz.")





@tree.command(name="html", description="Fournit des conseils et des exemples de code HTML pour un sujet spécifique")
async def html(interaction: discord.Interaction, sujet: str):
    conseils = {
        "formulaire": {
            "exemple": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulaire</title>
</head>
<body>
    <h1>Formulaire de Contact</h1>
    <form action="/submit" method="post">
        <label for="name">Nom:</label>
        <input type="text" id="name" name="name" required>
        <br>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        <br>
        <input type="submit" value="Envoyer">
    </form>
</body>
</html>""",
            "conseils": """1. Utilisez des balises `label` pour les champs de formulaire afin d'améliorer l'accessibilité.
2. Assurez-vous que tous les champs nécessaires sont marqués comme `required` pour éviter les soumissions incomplètes.
3. Testez le formulaire sur différents navigateurs pour garantir la compatibilité.""" 
        },
        "tableau": {
            "exemple": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau</title>
</head>
<body>
    <h1>Tableau d'Exemple</h1>
    <table border="1">
        <tr>
            <th>Nom</th>
            <th>Âge</th>
        </tr>
        <tr>
            <td>Alice</td>
            <td>30</td>
        </tr>
        <tr>
            <td>Bob</td>
            <td>25</td>
        </tr>
    </table>
</body>
</html>""",
            "conseils": """1. Utilisez les balises `<th>` pour les en-têtes de colonnes pour améliorer la lisibilité du tableau.
2. Les balises `<tr>`, `<td>` et `<th>` sont essentielles pour structurer les lignes et les cellules du tableau.
3. Ajoutez des attributs CSS pour améliorer le style et l'apparence du tableau."""
        }
    }

    info = conseils.get(sujet.lower())
    if info:
        exemple_code = info["exemple"]
        conseils_text = info["conseils"]
        message = (f"Voici un exemple de code HTML pour {sujet} :\n```html\n{exemple_code}\n```\n\n"
                   f"**Conseils pour {sujet} :**\n{conseils_text}")
    else:
        message = "Désolé, aucun exemple disponible pour ce sujet."

    await interaction.response.send_message(message)

@tree.command(name="css", description="Fournit des conseils et des exemples de code CSS pour un sujet spécifique")
async def css(interaction: discord.Interaction, sujet: str):
    conseils = {
        "couleurs": {
            "exemple": """/* Exemple de couleurs */
body {
    background-color: #f0f0f0;
}

h1 {
    color: #333;
}""",
            "conseils": """1. Utilisez des codes hexadécimaux ou des noms de couleurs pour définir les couleurs des éléments.
2. Assurez-vous que les couleurs offrent un bon contraste pour l'accessibilité.
3. Essayez d'utiliser des variables CSS pour gérer les couleurs globales dans votre projet."""
        },
        "mise_en_page": {
            "exemple": """/* Exemple de mise en page */
.container {
    width: 80%;
    margin: 0 auto;
}

.header {
    background-color: #4CAF50;
    color: white;
    padding: 10px;
    text-align: center;
}""",
            "conseils": """1. Utilisez des conteneurs pour centrer et aligner le contenu de manière cohérente.
2. Les propriétés comme `margin`, `padding` et `text-align` sont essentielles pour la mise en page.
3. Testez la mise en page sur différents écrans pour garantir la réactivité.""" 
        }
    }

    info = conseils.get(sujet.lower())
    if info:
        exemple_code = info["exemple"]
        conseils_text = info["conseils"]
        message = (f"Voici un exemple de code CSS pour {sujet} :\n```css\n{exemple_code}\n```\n\n"
                   f"**Conseils pour {sujet} :**\n{conseils_text}")
    else:
        message = "Désolé, aucun exemple disponible pour ce sujet."

    await interaction.response.send_message(message)




@tree.command(name="docs", description="Fournit des liens vers la documentation pour un langage ou une technologie spécifique")
async def docs(interaction: discord.Interaction, sujet: str):
    links = {
        "python": "https://docs.python.org/3/",
        "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "html": "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "css": "https://developer.mozilla.org/en-US/docs/Web/CSS",
        "react": "https://reactjs.org/docs/getting-started.html",
        "node": "https://nodejs.org/en/docs/"
    }
    link = links.get(sujet.lower(), "Documentation non trouvée.")
    await interaction.response.send_message(f"Documentation pour {sujet} : {link}")

@tree.command(name="error", description="Fournit des solutions pour des erreurs courantes")
async def error(interaction: discord.Interaction, erreur: str):
    solutions = {
        "syntaxerror": "Une `SyntaxError` se produit généralement lorsqu'il y a une erreur de syntaxe dans votre code. Assurez-vous que toutes les parenthèses et accolades sont correctement fermées.",
        "typeerror": "Une `TypeError` survient lorsque vous essayez d'utiliser un type de données incorrect. Vérifiez les types de vos variables.",
        "referenceerror": "Une `ReferenceError` signifie que vous essayez d'utiliser une variable qui n'a pas été déclarée. Assurez-vous que toutes vos variables sont déclarées avant de les utiliser."
    }
    solution = solutions.get(erreur.lower(), "Erreur non reconnue.")
    await interaction.response.send_message(f"Solution pour {erreur} : {solution}")





@tree.command(name="concept", description="Explique un concept de programmation avec un exemple")
async def concept(interaction: discord.Interaction, concept: str):
    concepts = {
        "boucle": "En programmation, une boucle permet d'exécuter une section de code plusieurs fois. Exemple en Python :\n```python\nfor i in range(5):\n    print(i)\n```",
        "fonction": "Une fonction est un bloc de code réutilisable. Exemple en JavaScript :\n```javascript\nfunction greet(name) {\n    return 'Hello, ' + name;\n}\n```",
        "classe": "Une classe est un modèle pour créer des objets. Exemple en Java :\n```java\npublic class Person {\n    String name;\n    int age;\n\n    public Person(String name, int age) {\n        this.name = name;\n        this.age = age;\n    }\n}\n```"
    }
    description = concepts.get(concept.lower(), "Concept non reconnu.")
    await interaction.response.send_message(f"Concept de {concept} :\n{description}")


@tree.command(name="tools", description="Fournit des liens vers des outils de développement utiles")
async def tools(interaction: discord.Interaction):
    tools = {
        "visual studio code": "https://code.visualstudio.com/",
        "Postgresql": "https://www.enterprisedb.com/downloads/postgres-postgresql-download/",
        "postman": "https://www.postman.com/",
        "git": "https://git-scm.com/",
        "docker": "https://www.docker.com/",
        "npm": "https://www.npmjs.com/"
    
    }
    tool_list = "\n".join([f"{name}: {url}" for name, url in tools.items()])
    await interaction.response.send_message(f"Outils de développement utiles :\n{tool_list}")


@tree.command(name="bestpractices", description="Fournit des conseils sur les meilleures pratiques de programmation")
async def bestpractices(interaction: discord.Interaction, sujet: str):
    practices = {
        "python": "1. Utilisez des noms de variables clairs.\n2. Écrivez des tests pour votre code.\n3. Suivez les conventions de style PEP8.",
        "javascript": "1. Utilisez des `const` et `let` au lieu de `var`.\n2. Évitez les fonctions globales.\n3. Utilisez des outils de linting comme ESLint.",
        "html": "1. Utilisez des éléments sémantiques.\n2. Assurez-vous que votre code est valide avec un validateur HTML.\n3. Optimisez les performances en réduisant le nombre d'éléments.",
        "css": "1. Utilisez des préprocesseurs comme SASS ou LESS.\n2. Adoptez des pratiques de nommage cohérentes.\n3. Minimisez les fichiers CSS pour améliorer les performances."
    }
    practice = practices.get(sujet.lower(), "Pratiques non trouvées.")
    await interaction.response.send_message(f"Meilleures pratiques pour {sujet} :\n{practice}")



@tree.command(name="check_syntax", description="Vérifie la syntaxe d'un code source.")
async def check_syntax(interaction: discord.Interaction, language: str, code: str):
    try:
        if language == "python":
            result = subprocess.run(['python', '-m', 'py_compile', '-'], input=code.encode(), capture_output=True)
            output = result.stderr.decode() if result.stderr else "Pas d'erreurs de syntaxe."
        elif language == "javascript":
            result = subprocess.run(['node', '--check'], input=code.encode(), capture_output=True)
            output = result.stderr.decode() if result.stderr else "Pas d'erreurs de syntaxe."
        else:
            await interaction.response.send_message("Langage non supporté.")
            return

        await interaction.response.send_message(f"Résultat de la vérification de syntaxe :\n```{output}```")
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors de la vérification de la syntaxe : {str(e)}")

@tree.command(name="format_code", description="Formate le code source selon les conventions du langage spécifié.")
async def format_code(interaction: discord.Interaction, language: str, code: str):
    try:
        if language == "python":
            formatted_code = black.format_str(code, mode=black.FileMode())
        else:
            await interaction.response.send_message("Langage non supporté pour le formatage.")
            return

        await interaction.response.send_message(f"Code formaté :\n```{formatted_code}```")
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors du formatage du code : {str(e)}")


@tree.command(name="convert_code", description="Convertit le code d'un langage à un autre.")
async def convert_code(interaction: discord.Interaction, language_from: str, language_to: str, code: str):
    try:
        # Note : La conversion entre langages est complexe et peut nécessiter des outils spécifiques.
        await interaction.response.send_message("Conversion entre langages non supportée pour l'instant.")
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors de la conversion du code : {str(e)}")
@tree.command(name="check_code", description="Vérifie le code source pour les bonnes pratiques ou les erreurs.")
async def check_code(interaction: discord.Interaction, code: str):
    try:
        # Cette fonctionnalité nécessiterait une intégration avec des outils d'analyse statique ou des linters.
        await interaction.response.send_message("Vérification de code non supportée pour l'instant.")
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors de la vérification du code : {str(e)}")


@tree.command(name="complexity", description="Analyse la complexité cyclomatique du code")
async def complexity(interaction: discord.Interaction, code: str):
    try:
        # Nettoyer le code pour l'analyse
        code = code.replace("```python\n", "").replace("\n```", "")
        
        # Calculer la complexité cyclomatique
        complexity_results = list(cc_visit(code))
        complexity_score = complexity_results[0].complexity if complexity_results else "Non calculé"
        
        # Calculer les métriques
        metrics = mi_visit(code)
        metrics_score = metrics[0] if metrics else "Non calculé"
        
        response = (f"Complexité cyclomatique : {complexity_score}\n"
                    f"Complexité du code : {metrics_score}")
        await interaction.response.send_message(response)
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")


@tree.command(name="compare", description="Compare les performances de deux morceaux de code")
async def compare(interaction: discord.Interaction, code1: str, code2: str, language: str):
    if language == "python":
        def measure_performance(code):
            exec_globals = {}
            start_time = time.time()
            exec(code, {}, exec_globals)
            end_time = time.time()
            return end_time - start_time
        
        try:
            time1 = measure_performance(code1)
            time2 = measure_performance(code2)
            await interaction.response.send_message(f"Temps d'exécution Code 1: {time1}s\nTemps d'exécution Code 2: {time2}s")
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {str(e)}")
    else:
        await interaction.response.send_message("Langage non supporté pour la comparaison.")

def analyze_code(code):
    tree = ast.parse(code)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return f"Fonctions détectées : {functions}"

@tree.command(name="refactor", description="Fournit des suggestions pour le refactoring de code")
async def refactor(interaction: discord.Interaction, language: str, code: str):
    if language == "python":
        try:
            analysis = analyze_code(code)
            await interaction.response.send_message(f"Suggestions de refactoring :\n{analysis}")
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {str(e)}")
    else:
        await interaction.response.send_message("Langage non supporté pour le refactoring.")


# token ia 
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

@tree.command(name="generate_code", description="Générer du code à partir d'un prompt")
async def generate_code(interaction: discord.Interaction, prompt: str, language: str = "python"):
    await interaction.response.defer()
    try:
        # Ajouter un contexte au prompt pour guider la génération
        prompt_with_context = f"# Code in {language}:\n{prompt}\n"

        inputs = tokenizer(prompt_with_context, return_tensors='pt', padding=True, truncation=True)
        
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs['attention_mask'],
            max_length=200,  # Augmenté pour permettre des réponses plus longues
            pad_token_id=tokenizer.pad_token_id,
            no_repeat_ngram_size=2,
            num_return_sequences=1,
            temperature=0.7,  # Ajusté pour plus de créativité
            top_k=50,
            top_p=0.95,
            do_sample=True
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Formater la réponse
        formatted_response = f"```{language}\n{response}\n```"
        
        await interaction.edit_original_response(content=formatted_response)
    except Exception as e:
        await interaction.edit_original_response(content=f"Une erreur s'est produite : {str(e)}")


@tree.command(name='cours', description='Affiche le lien vers le site de cours de programmation.')
async def cours(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Cours de Programmation",
        description="Voici le lien  du site du professeur de cours de programmation.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Site Web", value="[Cliquez ici pour accéder aux cours](https://btsrabelais22.fr)", inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name='editeur_ligne', description='Affiche le lien vers editeur en ligne .')
async def cours(interaction: discord.Interaction):
    embed = discord.Embed(
        title="editeur en ligne ",
        description="Voici le lien  editeur en ligne.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Site Web", value="[Cliquez ici pour accéder editeur en ligne ](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiR2diNrdaIAxVJQ6QEHSs3Ey0QFnoECBgQAQ&url=https%3A%2F%2Fwww.mycompiler.io%2Ffr%2Fonline-javascript-editor&usg=AOvVaw0LEIaJcSktmmMLKeQLTJ_y&opi=89978449)", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name='ia_links', description='Affiche des liens vers des outils d\'IA.')
async def ia_links(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Outils d'IA",
        description="Voici quelques outils d'IA intéressants.",
        color=discord.Color.blue()
    )
    embed.add_field(name="ChatGPT", value="[Accéder à ChatGPT](https://chat.openai.com/)", inline=False)
    embed.add_field(name="Gemini", value="[Accéder à Gemini](https://gemini.google.com/app?hl=fr)", inline=False) 
    embed.add_field(name="Claude", value="[Accéder à Claude](https://claude.ai/new)", inline=False)  
    await interaction.response.send_message(embed=embed)


@tree.command(name='erreur', description='Analyse une erreur de code.')
async def erreur(interaction: discord.Interaction, erreur: str):
    # Exemple de gestion d'erreurs courantes
    if "SyntaxError" in erreur:
        await interaction.response.send_message("Erreur de syntaxe : vérifiez vos parenthèses ou votre indentation.")
    elif "NameError" in erreur:
        await interaction.response.send_message("Erreur de nom : assurez-vous que toutes les variables sont définies.")
    else:
        await interaction.response.send_message("Erreur non reconnue. Vérifiez votre code.")

@tree.command(name='bibliotheques', description='Recommande des bibliothèques pour un langage donné.')
async def bibliotheques(interaction: discord.Interaction, langage: str):
    recommandations = {
        "python": "Pour Python, je recommande : `requests`, `numpy`, `pandas`.",
        "javascript": "Pour JavaScript, essayez : `axios`, `lodash`, `express`.",
    }
    await interaction.response.send_message(recommandations.get(langage.lower(), "Langage non pris en charge."))

@tree.command(name='projet', description='Suggère une idée de projet de codage.')
async def projet(interaction: discord.Interaction):
    projets = [
        "Créez un bot Discord.",
        "Développez une application de gestion de tâches.",
        "Réalisez un site web personnel.",
    ]
    await interaction.response.send_message(f"Voici une idée de projet : {projets[0]}")


@tree.command(name='deploiement', description='Fournit des étapes pour déployer une application.')
async def deploiement(interaction: discord.Interaction):
    etapes = (
        "1. Choisissez un hébergeur (ex : Heroku, Render).",
        "2. Préparez votre application pour le déploiement.",
        "3. Configurez les variables d'environnement.",
        "4. Déployez votre application.",
    )
    await interaction.response.send_message("\n".join(etapes))

tree.command(name='creer_salle', description='Crée une salle de discussion temporaire pour la collaboration.')
async def creer_salle(interaction: discord.Interaction, nom: str):
    channel = await interaction.guild.create_text_channel(nom)
    await interaction.response.send_message(f"Salle de discussion créée : {channel.mention} !")

@tree.command(name='supprimer_salle', description='Supprime la salle de discussion actuelle.')
async def supprimer_salle(interaction: discord.Interaction):
    if interaction.channel:
        await interaction.channel.delete()
        await interaction.response.send_message("Salle de discussion supprimée.")
    else:
        await interaction.response.send_message("Vous devez être dans une salle de discussion.")

@tree.command(name='donner_role', description='Donne un rôle à un utilisateur pour la collaboration.')
async def donner_role(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
    await membre.add_roles(role)
    await interaction.response.send_message(f"Rôle {role.name} attribué à {membre.display_name}.")

@tree.command(name='partager_code', description='Partage un extrait de code.')
async def partager_code(interaction: discord.Interaction, *, code: str):
    await interaction.channel.send(f"```python\n{code}\n```")

@tree.command(name='annoncer', description='Annonce la création d\'une nouvelle salle de discussion.')
async def annoncer(interaction: discord.Interaction):
    canal_annonces = discord.utils.get(interaction.guild.text_channels, name='annonces')
    if canal_annonces:
        await canal_annonces.send(f"Nouvelle salle de discussion créée par {interaction.user.mention} : {interaction.channel.mention}")
        await interaction.response.send_message("Annoncé dans le canal des annonces.")
    else:
        await interaction.response.send_message("Aucun canal d'annonces trouvé.")

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} est connecté et prêt à aider!')
    await client.change_presence(activity=discord.Game(name=" HELP SIO1"))

@app.route('/')
def home():
    return "Welcome to the bot sio!", 200


@app.route('/protected-route', methods=['GET'])
def protected_route():
    auth = request.authorization
    if not auth or not (auth.username == USERNAME and auth.password == PASSWORD):
        abort(401)  # Unauthorized
    return "Welcome to the protected sio route!", 200

# Lancer le serveur Flask dans un thread
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

if __name__ == '__main__':
    # Démarrer le serveur Flask dans un thread
    threading.Thread(target=run_flask).start()
    # Démarrer le bot Discord
    client.run(os.getenv('DISCORD_TOKEN'))