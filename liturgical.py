from datetime import date, timedelta


def easter_date(year: int) -> date:
    """Calcula a data da Páscoa usando o algoritmo de Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_liturgical_periods(year: int) -> dict:
    """Retorna as datas de início de cada período litúrgico para um ano."""
    easter = easter_date(year)
    christmas = date(year, 12, 25)

    # Batismo do Senhor: domingo após 06/01 (ou 06/01 se for domingo)
    epiphany = date(year, 1, 6)
    batismo = epiphany + timedelta(days=(6 - epiphany.weekday()) % 7)
    if batismo == epiphany and epiphany.weekday() != 6:
        batismo = epiphany + timedelta(days=(6 - epiphany.weekday()) % 7)

    # Quarta-feira de Cinzas: 46 dias antes da Páscoa
    cinzas = easter - timedelta(days=46)

    # Tríduo Pascal: Quinta-feira Santa até Sábado Santo
    quinta_santa = easter - timedelta(days=3)

    # Pentecostes: 50 dias após a Páscoa
    pentecostes = easter + timedelta(days=49)

    # Advento: 4º domingo antes do Natal
    natal_weekday = christmas.weekday()
    advento_start = christmas - timedelta(days=natal_weekday + 21 + 7)
    if advento_start.weekday() != 6:
        advento_start = christmas - timedelta(days=(28 + natal_weekday - 6) % 7)

    return {
        "easter": easter,
        "batismo": batismo,
        "cinzas": cinzas,
        "quinta_santa": quinta_santa,
        "pentecostes": pentecostes,
        "advento_start": advento_start,
    }


def get_current_liturgical_period(today: date = None) -> dict:
    """Retorna o período litúrgico atual com datas e nome."""
    if today is None:
        today = date.today()

    year = today.year
    periods = get_liturgical_periods(year)
    easter = periods["easter"]

    # Quaresma: Quarta-feira de Cinzas até Sábado Santo
    if periods["cinzas"] <= today <= easter - timedelta(days=1):
        return {
            "period": "quaresma",
            "name": "Quaresma",
            "start": periods["cinzas"],
            "end": easter - timedelta(days=1),
        }

    # Tríduo Pascal: Quinta-feira Santa até Sábado Santo
    if periods["quinta_santa"] <= today <= easter - timedelta(days=1):
        return {
            "period": "triduo_pascal",
            "name": "Tríduo Pascal",
            "start": periods["quinta_santa"],
            "end": easter - timedelta(days=1),
        }

    # Páscoa: Domingo de Páscoa até Pentecostes
    if easter <= today <= periods["pentecostes"]:
        return {
            "period": "pascoa",
            "name": "Tempo Pascal",
            "start": easter,
            "end": periods["pentecostes"],
        }

    # Natal: 25/12 até Batismo do Senhor
    natal_start = date(year, 12, 25)
    natal_end = periods["batismo"]
    # Se estamos no início do ano, o Natal é do ano anterior
    if today <= periods["batismo"]:
        natal_start = date(year - 1, 12, 25)
        natal_end = periods["batismo"]
    if natal_start <= today <= natal_end:
        return {
            "period": "natal",
            "name": "Tempo do Natal",
            "start": natal_start,
            "end": natal_end,
        }

    # Advento: início do Advento até 24/12
    if periods["advento_start"] <= today <= date(year, 12, 24):
        return {
            "period": "advento",
            "name": "Tempo do Advento",
            "start": periods["advento_start"],
            "end": date(year, 12, 24),
        }

    # Tempo Comum: todo o resto
    return {
        "period": "tempo_comum",
        "name": "Tempo Comum",
        "start": None,
        "end": None,
    }
