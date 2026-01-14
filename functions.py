def calculate_teacher_salary(stavka, soat, sinf_rahbar_bhm, bhm):
    # 18 soat = 1 stavka
    dars_uchun = (stavka / 18) * soat
    jami = dars_uchun + sinf_rahbar_bhm
    # 12% daromad solig'i + 1% INPS
    toza_oylik = jami * 0.87
    return round(toza_oylik, 2)
