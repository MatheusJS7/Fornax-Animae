from database import SessionLocal
from models import Task

tasks = [
    # ==================== TAREFAS GERAIS (all) ====================
    # Espiritual
    {"title": "Oração matinal (10+ min)", "category": "espiritual", "xp_value": 12, "liturgical_period": "all"},
    {"title": "Lectio Divina (15 min)", "category": "espiritual", "xp_value": 18, "liturgical_period": "all"},
    {"title": "Exame de consciência noturno (5 passos)", "category": "espiritual", "xp_value": 14, "liturgical_period": "all"},
    {"title": "Missa assistida com atenção", "category": "espiritual", "xp_value": 22, "liturgical_period": "all"},
    {"title": "Rosário completo (15 mistérios)", "category": "espiritual", "xp_value": 16, "liturgical_period": "all"},
    {"title": "Oração noturna + ato de contrição", "category": "espiritual", "xp_value": 10, "liturgical_period": "all"},
    {"title": "Confissão (semanal/quinzenal)", "category": "espiritual", "xp_value": 30, "liturgical_period": "all"},
    # Disciplina
    {"title": "Acordar no horário sem adiar o alarme", "category": "disciplina", "xp_value": 10, "liturgical_period": "all"},
    {"title": "Exercício físico (20+ min)", "category": "disciplina", "xp_value": 12, "liturgical_period": "all"},
    {"title": "Trabalho/estudo com foco completo", "category": "disciplina", "xp_value": 14, "liturgical_period": "all"},
    {"title": "Telas desligadas 1h antes de dormir", "category": "disciplina", "xp_value": 8, "liturgical_period": "all"},
    {"title": "Refeição com sobriedade e gratidão", "category": "disciplina", "xp_value": 8, "liturgical_period": "all"},
    {"title": "Leitura formativa (30 min) em vez de telas", "category": "disciplina", "xp_value": 10, "liturgical_period": "all"},
    # Moral
    {"title": "Evitei ocasiões de pecado conhecidas", "category": "moral", "xp_value": 15, "liturgical_period": "all"},
    {"title": "Controlei a língua (sem murmúrio/crítica)", "category": "moral", "xp_value": 10, "liturgical_period": "all"},
    {"title": "Ato de humildade concreto", "category": "moral", "xp_value": 12, "liturgical_period": "all"},
    {"title": "Perdoei alguém (mesmo interiormente)", "category": "moral", "xp_value": 14, "liturgical_period": "all"},
    {"title": "Recusei um prazer desnecessário (mortificação)", "category": "moral", "xp_value": 12, "liturgical_period": "all"},
    # Caridade
    {"title": "Servi alguém sem esperar retorno", "category": "caridade", "xp_value": 20, "liturgical_period": "all"},
    {"title": "Visitei ou liguei para alguém sozinho/doente", "category": "caridade", "xp_value": 28, "liturgical_period": "all"},
    {"title": "Obra de misericórdia corporal", "category": "caridade", "xp_value": 25, "liturgical_period": "all"},
    {"title": "Serviço voluntário comunitário", "category": "caridade", "xp_value": 35, "liturgical_period": "all"},
    {"title": "Orei intencionalmente por alguém em sofrimento", "category": "caridade", "xp_value": 14, "liturgical_period": "all"},

    # ==================== QUARESMA ====================
    {"title": "Jejum de algum prazer (PC, doces, redes sociais)", "category": "disciplina", "xp_value": 15, "liturgical_period": "quaresma"},
    {"title": "Rezar o Terço da Misericórdia", "category": "espiritual", "xp_value": 12, "liturgical_period": "quaresma"},
    {"title": "Estação da Cruz (sexta-feira)", "category": "espiritual", "xp_value": 20, "liturgical_period": "quaresma"},
    {"title": "Escolher uma virtude pra praticar os 40 dias", "category": "moral", "xp_value": 18, "liturgical_period": "quaresma"},
    {"title": "Jejum de língua (sem reclamar por 1 dia)", "category": "moral", "xp_value": 15, "liturgical_period": "quaresma"},
    {"title": "Visitar alguém que preciso perdoar", "category": "caridade", "xp_value": 25, "liturgical_period": "quaresma"},
    {"title": "Doação concreta (tempo ou dinheiro)", "category": "caridade", "xp_value": 20, "liturgical_period": "quaresma"},
    {"title": "Leitura de um livro espiritual", "category": "disciplina", "xp_value": 16, "liturgical_period": "quaresma"},
    {"title": "Confissão quaresmal completa", "category": "espiritual", "xp_value": 35, "liturgical_period": "quaresma"},
    {"title": "Abstenção de carne na sexta-feira", "category": "moral", "xp_value": 10, "liturgical_period": "quaresma"},

    # ==================== QUARESMA DE SÃO MIGUEL ARCANJO ====================
    {"title": "Novena de São Miguel Arcanjo", "category": "espiritual", "xp_value": 25, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Oração a São Miguel Arcanjo (diária)", "category": "espiritual", "xp_value": 12, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Jejum de 3 dias antes de 29/09 (Três Hagiology)", "category": "disciplina", "xp_value": 30, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Leitura sobre São Miguel e os Anjos", "category": "disciplina", "xp_value": 14, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Ato de coragem espiritual (combater tentações)", "category": "moral", "xp_value": 18, "liturgical_period": "quaresma_sao_miguel"},
    {"title": "Proteger alguém em situação difícil", "category": "caridade", "xp_value": 20, "liturgical_period": "quaresma_sao_miguel"},

    # ==================== ADVENTO ====================
    {"title": "Esperança ativa: 1 ato de bondade por dia", "category": "caridade", "xp_value": 12, "liturgical_period": "advento"},
    {"title": "Oração pela preparação do coração", "category": "espiritual", "xp_value": 14, "liturgical_period": "advento"},
    {"title": "Coroa do Advento: acender uma vela e orar", "category": "espiritual", "xp_value": 12, "liturgical_period": "advento"},
    {"title": "Desapegar: doar algo que não uso", "category": "caridade", "xp_value": 15, "liturgical_period": "advento"},
    {"title": "Leitura profética sobre o Messias", "category": "disciplina", "xp_value": 14, "liturgical_period": "advento"},

    # ==================== NATAL ====================
    {"title": "Louvor ao Menino Jesus", "category": "espiritual", "xp_value": 10, "liturgical_period": "natal"},
    {"title": "Visitar um presépio", "category": "espiritual", "xp_value": 12, "liturgical_period": "natal"},
    {"title": "Compartilhar a alegria do Natal com alguém", "category": "caridade", "xp_value": 15, "liturgical_period": "natal"},
    {"title": "Agradecer pelas bênçãos do ano escrevendo", "category": "moral", "xp_value": 12, "liturgical_period": "natal"},
    {"title": "Missa do Gallo", "category": "espiritual", "xp_value": 20, "liturgical_period": "natal"},

    # ==================== PÁSCOA ====================
    {"title": "Testemunhar a alegria da Ressurreição", "category": "caridade", "xp_value": 15, "liturgical_period": "pascoa"},
    {"title": "Oração de ação de graças pelo Batismo", "category": "espiritual", "xp_value": 12, "liturgical_period": "pascoa"},
    {"title": "Viver com renovada esperança", "category": "moral", "xp_value": 14, "liturgical_period": "pascoa"},
    {"title": "Compartilhar a fé com alguém", "category": "caridade", "xp_value": 18, "liturgical_period": "pascoa"},
    {"title": "Missa dominical com atenção plena", "category": "espiritual", "xp_value": 16, "liturgical_period": "pascoa"},
]

db = SessionLocal()
for t in tasks:
    db_task = Task(**t, user_id=11)
    db.add(db_task)
db.commit()
db.close()
print(f"{len(tasks)} tarefas criadas com sucesso!")
