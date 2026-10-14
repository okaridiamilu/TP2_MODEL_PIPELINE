from src.app import create_app

# Point d'entree du serveur : c'est le SEUL fichier qui demarre le serveur.
# Les tests importent uniquement src.app.create_app, jamais ce fichier,
# donc aucun port n'est occupe pendant les tests.

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
