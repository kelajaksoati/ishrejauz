import logging

def calculate_salary_final(data, db):
    """
    O'qituvchi oyligini hisoblashning eng mukammal varianti.
    Asosiy dars, sinf rahbarlik, daftar tekshirish, kabinet mudirligi, 
    sertifikat va olis hudud ustamalarini hisobga oladi.
    """
    try:
        # 1. Bazadan joriy sozlamalarni olish (BHM va Toifa stavkalari)
        settings = db.get_settings()
        bhm = int(settings.get('bhm', 375000))
        
        # Toifa va stavka (agar bazada bo'lmasa, standart qiymat)
        toifa_nomi = str(data.get('toifa', 'mutaxassis')).lower()
        stavka = int(settings.get(toifa_nomi, 3500000))
        
        # Dars soati (nuqta yoki vergul bilan kiritilsa ham ishlaydi)
        soat = float(str(data.get('soat', 0)).replace(',', '.'))

        # 2. ASOSIY DARS MAOSHI (18 soat = 1 stavka)
        asosiy_maosh = (stavka / 18) * soat
        
        # 3. SINF RAHBARLIK (O'quvchi soniga qarab: <=15: 50%, <=25: 75%, >25: 100% BHM)
        sinf_rahbar_summa = 0
        u_soni = 0
        if data.get('sinf_rahbar'):
            u_soni = int(data.get('uquvchi_soni', 0))
            foiz = 0.5 if u_soni <= 15 else (0.75 if u_soni <= 25 else 1.0)
            sinf_rahbar_summa = bhm * foiz
            
        # 4. DAFTAR VA KABINET (BHM ga nisbatan)
        # Daftar tekshirish (15% BHM), Kabinet mudirligi (50% BHM)
        daftar_summa = (bhm * 0.15) if data.get('daftar') else 0
        kabinet_summa = (bhm * 0.5) if data.get('kabinet') else 0
        
        # 5. SERTIFIKAT USTAMASI (Stavkaning 20% qismi)
        sert_summa = (stavka * 0.2) if data.get('sertifikat') else 0

        # 6. OLIS HUDUD USTAMASI (Stajga qarab stavkadan: <3y: 10%, <5y: 20%, >=5y: 50%)
        olis_summa = 0
        staj = 0
        if data.get('olis_hudud'):
            staj = int(data.get('staj', 0))
            if staj < 3:
                olis_foiz = 0.1
            elif staj < 5:
                olis_foiz = 0.2
            else:
                olis_foiz = 0.5
            olis_summa = stavka * olis_foiz

        # 7. JAMI HISOB-KITOB
        total_gross = asosiy_maosh + sinf_rahbar_summa + daftar_summa + kabinet_summa + sert_summa + olis_summa
        
        # Daromad solig'i (12%) va Pensiya (1%) = Jami 13% ushlanma
        soliq = total_gross * 0.13
        final_salary = total_gross - soliq

        # 8. NATIJANI FORMATLASH (Markdown va chiroyli ko'rinish)
        res = (
            f"📊 **Oylik ish haqi hisob-kitobi:**\n\n"
            f"🔹 **Toifa:** {toifa_nomi.capitalize()}\n"
            f"🔹 **Stavka:** {stavka:,.0f} so'm\n"
            f"🔹 **Dars yuklamasi:** {soat} soat\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"➕ **Dars maoshi:** {asosiy_maosh:,.0f} so'm\n"
        )
        
        if sinf_rahbar_summa:
            res += f"➕ **Sinf rahbarlik ({u_soni} o'quvchi):** {sinf_rahbar_summa:,.0f} so'm\n"
        if daftar_summa:
            res += f"➕ **Daftar tekshirish:** {daftar_summa:,.0f} so'm\n"
        if kabinet_summa:
            res += f"➕ **Kabinet mudirligi:** {kabinet_summa:,.0f} so'm\n"
        if sert_summa:
            res += f"➕ **Sertifikat ustamasi (20%):** {sert_summa:,.0f} so'm\n"
        if olis_summa:
            res += f"➕ **Olis hudud ({staj} yil staj):** {olis_summa:,.0f} so'm\n"
        
        res += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 **Jami (Gryutto):** {total_gross:,.0f} so'm\n"
            f"✂️ **Ushlanmalar (13%):** {soliq:,.0f} so'm\n\n"
            f"✅ **Qo'lga tegadigan summa:**\n"
            f"👉 **{round(final_salary, 0):,.0f} so'm**"
        ).replace(',', ' ') # O'zbekiston formatida bo'sh joy bilan ajratish

        return res

    except Exception as e:
        logging.error(f"Salary Calculation Error: {e}")
        return "❌ Hisoblashda xatolik yuz berdi. Iltimos, ma'lumotlarni raqamda va to'g'ri kiritganingizni tekshiring."
