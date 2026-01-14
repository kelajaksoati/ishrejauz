def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    """
    Oylik hisoblash formulasi:
    1. Dars soati uchun: (Stavka / 18) * soat
    2. Sinf rahbarlik uchun: (BHM * foiz / 100)
    3. Soliqlar: Jami summadan 13% ayiriladi (12% daromad + 1% INPS)
    """
    dars_uchun = (stavka / 18) * soat
    sinf_uchun = bhm * (sinf_foiz / 100)
    
    jami = dars_uchun + sinf_uchun
    toza_oylik = jami * 0.87  # 100% - 13% = 87%
    
    return round(toza_oylik, 2)
