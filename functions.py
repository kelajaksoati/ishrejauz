def calculate_salary_logic(stavka, soat, sinf_rahbar_bhm_foiz, bhm):
    # O'zbekiston tizimida 18 soat - 1 stavka
    asosiy_oylik = (stavka / 18) * soat
    sinf_uchun = bhm * (sinf_rahbar_bhm_foiz / 100)
    jami = asosiy_oylik + sinf_uchun
    # 12% daromad solig'i + 1% pensiya
    toza_oylik = jami * 0.87
    return round(toza_oylik, 2)
