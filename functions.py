def calculate_salary_logic(stavka, soat, sinf_foiz, bhm):
    dars_puli = (stavka / 18) * soat
    sinf_puli = bhm * (sinf_foiz / 100)
    toza_oylik = (dars_puli + sinf_puli) * 0.87
    return round(toza_oylik, 2)

async def get_ai_help(query):
    # Bu yerda OpenAI integratsiyasi bo'ladi. Agar API bo'lmasa, namunaviy javob qaytaradi.
    return f"🤖 AI javobi: '{query}' bo'yicha dars ishlanmasi tayyor. \n\n1. Mavzu tushuntirildi.\n2. Mashqlar bajarildi.\n3. Yakuniy xulosa."
