from app import create_app, db

app = create_app()

# Create tables
def init_db():
    with app.app_context():
        db.create_all()
        print('Banco de dados inicializado com sucesso!')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
