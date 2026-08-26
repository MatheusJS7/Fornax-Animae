from database import SessionLocal
from models import Task

tasks_sao_miguel = [
    {"title": "Novena de São Miguel Arcanjo", "category": "espiritual", "xp_value": 25, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Oração a São Miguel Arcanjo (diária)", "category": "espiritual", "xp_value": 12, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Jejum de 3 dias antes de 29/09", "category": "disciplina", "xp_value": 30, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Leitura sobre São Miguel e os Anjos", "category": "disciplina", "xp_value": 14, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Ato de coragem espiritual", "category": "moral", "xp_value": 18, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Proteger alguém em situação difícil", "category": "caridade", "xp_value": 20, "liturgical_period": "quaresma_sao_miguel"},
]

db = SessionLocal()
for t in tasks_sao_miguel:
    db.add(Task(**t, user_id=17))
db.commit()
db.close()
print(f"{len(tasks_sao_miguel)} tarefas de São Miguel criadas para user 17!")
