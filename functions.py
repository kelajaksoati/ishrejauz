import logging
import os

# --- ULTRA OYLIK HISOBLASH FUNKSIYASI ---
def calculate_salary_final(data, db):
    """
    O'qituvchi oyligini murakkab algoritmlar (staj, o'quvchilar soni) bilan hisoblash.
    data: FSMContext dan kelgan ma'lumotlar (soat, toifa, uquvchi_soni, staj va h.k.)
    db: Database obyekti (settings dagi joriy narxlarni olish uchun)
    """
    try:
        settings = db.get_settings()
        
        # 1. Asosiy parametrlar va xatolikdan himoya
        soat = float(str(data.get('soat', 0)).replace(',', '.'))
        bhm = int(settings.get('bhm', 375000))
        toifa = str(data.get('toifa', 'mutaxassis')).lower()
        
        # Toifa stavkasini bazadan olish (oliy, birinchi, ikkinchi, mutaxassis)
        stavka = int(settings.get(toifa, 3500000))
        
        # 2. Asosiy dars maoshi (18 soatlik dars yuklamasi 1 stavka hisoblanadi)
        asosiy_maosh = (stavka / 18) * soat
        
        # 3. Sinf rahbarlik (O'quvchi soniga qarab BHM foizida - Qonunchilikka ko'ra)
        sinf_rahbar_summa = 0
        if data.get('sinf_rahbar'):
            u_soni = int(data.get('uquvchi_soni', 0))
            if u_soni <= 15:
                foiz = 0.5  # 50% BHM
            elif u_soni <= 25:
                foiz = 0.75 # 75% BHM
            else:
                foiz = 1.0  # 100% BHM
            sinf_rahbar_summa = bhm * foiz
            
        # 4. Daftar tekshirish (Settings dagi summa yoki yo'q bo'lsa BHM 15%)
        daftar_summa = 0
        if data.get('daftar'):
            bazaviy_daftar = int(settings.get('daftar', 0))
            daftar_summa = bazaviy_daftar if bazaviy_daftar > 0 else (bhm * 0.15)
            
        # 5. Kabinet mudirligi (BHM 50% yoki bazadagi narx)
        kabinet_summa = 0
        if data.get('kabinet'):
            bazaviy_kabinet = int(settings.get('kabinet', 0))
            kabinet_summa = bazaviy_kabinet if bazaviy_kabinet > 0 else (bhm * 0.5)

        # 6. Sertifikat ustamasi (Stavkaga nisbatan 20%)
        # Izoh: O'zbekistonda xalqaro sertifikatlar uchun ustama stavkaning 20% yoki 50% bo'ladi
        sert_summa = 0
        if data.get('sertifikat'):
            sert_summa = stavka * 0.20 

        # 7. Olis hudud va Staj ustamasi (Pedagogik stajga qarab foizlar)
        olis_summa = 0
        if data.get('olis_hudud'):
            staj = int(data.get('staj', 0))
            # Stajga qarab ustama foizi: 1-3 yil (10%), 3-5 yil (20%), 5 yildan ko'p (50%)
            if 1 <= staj < 3:
                olis_foiz = 0.1
            elif 3 <= staj < 5:
                olis_foiz = 0.2
            elif staj >= 5:
                olis_foiz = 0.5
            else:
                olis_foiz = 0.1 # Minimal staj
            olis_summa = stavka * olis_foiz

        # --- JAMI HISOBLASH (GRYUTTO) ---
        total_gross = asosiy_maosh + sinf_rahbar_summa + daftar_summa + kabinet_summa + sert_summa + olis_summa
        
        # Daromad solig'i (12%) va Pensiya (1%) = Jami 13% ushlanma
        soliq = total_gross * 0.13
        final_salary = total_gross - soliq

        # --- NATIJANI CHIROYLI SHAKLLANTIRISH ---
        res = (
            f"📊 **Oylik ish haqi hisob-kitobi:**\n\n"
            f"🔹 **Toifa:** {toifa.replace('mutaxassis', 'Mutaxassis').capitalize()}\n"
            f"🔹 **Toifa stavkasi:** {stavka:,.0f} so'm\n"
            f"🔹 **Dars yuklamasi:** {soat} soat\n"
            f"----------------------------\n"
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
            f"\n💰 **Jami (Gryutto):** {total_gross:,.0f} so'm\n"
            f"✂️ **Ushlanmalar (13%):** {soliq:,.0f} so'm\n"
            f"✅ **Qo'lga tegadigan summa:** {round(final_salary, 0):,.0f} so'm"
        ).replace(',', ' ') # Uzb format uchun probel qo'shish
        
        return res
        
    except Exception as e:
        logging.error(f"Salary Ultra Error: {e}")
        return "❌ Hisoblashda xatolik! Ma'lumotlarni to'g'ri kiritganingizni tekshiring."
