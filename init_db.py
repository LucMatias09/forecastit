from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Recria todas as tabelas
    db.drop_all()
    db.create_all()
    
    # Cria usuário admin
    admin = User(
        name='Administrador',
        email='admin@forecastit.com',
        department='TI',
        role='admin',
        is_approved=True
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print("Banco de dados inicializado com sucesso!")
