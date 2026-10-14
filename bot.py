import asyncio
import json
import os
import random
from telethon import TelegramClient, events, functions, types as tg_types
from google import genai
from google.genai import types

API_ID = 32073192
API_HASH = "cae6b9040c05cdf61b6c154e2689b7b4"
GEMINI_KEY = "AQ.Ab8RN6LROn0uv4R-brg1PgMTw0JneXZbyePrfVqNT5aWNOGM7Q"

# Sizning asosiy akkountingiz (qo'ng'iroq va xabar boradigan manzil):
ADMIN_USERNAME = "KurbanbayevSh"
ADMIN_PHONE = "+998949888656"

client_tg = TelegramClient('my_session', API_ID, API_HASH)
client_ai = genai.Client(api_key=GEMINI_KEY)

SHAXSIY_QOIDALAR = f"""
Sen Sherzod Niyazovning shaxsiy AI-yordamchisisan.

Sherzod haqida ma'lumot:
- Texnologiyalar, veb-dasturlash, Arduino/elektronika, zamonaviy dizayn va kreativ loyihalar bilan shug'ullanadi.
- Xarakteri: aniq, zamonaviy, samimiy va vaqtini qadrlaydigan.

Muloqot qoidalari:
1. Birinchi marta yozgan odamga o'zingni "Assalomu alaykum! Men Sherzodning shaxsiy yordamchisiman" deb tanishtir. Suhbat davomida qayta-qayta salomlashma.
2. Sherzod hozir ishda yoki loyihalar bilan bandligini aytib, qanday masalada yozayotganini so'ra.
3. Javoblaring qisqa (1-3 gap), tabiiy va sof o'zbek tilida bo'lsin.
4. MUHIM (SHOSHILINCH HOLAT): Agar suhbatdosh Sherzod juda tez kerakligini, ish juda zarur yoki shoshilinch ekanini aytsa, javobingning eng boshiga albatta [SOS] belgisini qo'y va unga shunday de:
"[SOS] Tushunarli, masala juda muhim ekan! Men hoziroq Sherzodga to'xtovsiz qo'ng'iroq qilib, siz haqingizda xabar beryapman. Agar juda shoshilinch bo'lsa, {ADMIN_PHONE} raqamiga yoki @{ADMIN_USERNAME} profiliga ham bog'lanishingiz mumkin."
"""

MODELLAR = [
    "models/gemini-2.0-flash",
    "models/gemini-2.5-flash",
    "models/gemini-3.5-flash"
]

IGNOR_FILE = "ignor_list.json"

def load_ignor():
    if os.path.exists(IGNOR_FILE):
        try:
            with open(IGNOR_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_ignor(data):
    with open(IGNOR_FILE, "w") as f:
        json.dump(list(data), f)

qora_royxat = load_ignor()
xotira = {}
bot_yoqilgan = True

# SOS trevoga holatini boshqarish uchun o'zgaruvchi:
sos_active = False

# ==========================================
# 1. AGAR QO'NG'IROQNI KO'TARSANGIZ TREVOGANI TO'XTATISH
# ==========================================
@client_tg.on(events.Raw)
async def call_state_handler(update):
    global sos_active
    if isinstance(update, tg_types.UpdatePhoneCall):
        call = update.phone_call
        # Qo'ng'iroq qabul qilinsa (ko'tarilsa):
        if isinstance(call, (tg_types.PhoneCallAccepted, tg_types.PhoneCall)):
            if sos_active:
                sos_active = False
                print("✅ Qo'ng'iroq ko'tarildi! SOS trevoga to'xtatildi.")

# ==========================================
# 2. AGAR XABARNI O'QISANGIZ TREVOGANI TO'XTATISH
# ==========================================
@client_tg.on(events.MessageRead(inbox=False))
async def read_handler(event):
    global sos_active
    if sos_active:
        try:
            chat = await event.get_chat()
            if getattr(chat, 'username', None) and chat.username.lower() == ADMIN_USERNAME.lower():
                sos_active = False
                print("✅ Xabar o'qildi! SOS trevoga to'xtatildi.")
        except Exception:
            pass

# ==========================================
# 3. QO'NG'IROQ QILISH VA TAKRORLASH FUNKSIYASI
# ==========================================
async def make_telegram_call(target_user):
    try:
        user_entity = await client_tg.get_input_entity(target_user)
        protocol = tg_types.PhoneCallProtocol(
            min_layer=65,
            max_layer=92,
            udp_p2p=True,
            udp_reflector=True,
            library_versions=['2.4.4']
        )
        await client_tg(functions.phone.RequestCallRequest(
            user_id=user_entity,
            random_id=random.randint(1, 2147483647),
            g_a_hash=os.urandom(32),
            protocol=protocol
        ))
        return True
    except Exception as e:
        print(f"⚠️ Qo'ng'iroq xatosi: {e}")
        return False

async def sos_alarm_loop(ism, user_link, matn):
    global sos_active
    if sos_active:
        return  # Agar trevoga allaqachon ishlayotgan bo'lsa, ustma-ust tushmasin
    
    sos_active = True
    urinish = 1

    # Maksimal 10 marta (har 35 soniyada) siz o'qimaguningizcha/ko'tarmaguningizcha qayta qiladi:
    while sos_active and urinish <= 10:
        sos_xabar = (
            f"🚨 **SHOSHILINCH CHAQIRUV ({urinish}-urinish)!**\n\n"
            f"❗️ **{ism} ({user_link}) ismli insonning sizda juda zarur ishi bor ekan!**\n"
            f"💬 **Yozgan xabari:** \"{matn}\"\n\n"
            f"🔕 *Qo'ng'iroqni to'xtatish uchun shu xabarni o'qing, qo'ng'iroqni ko'taring yoki '+' deb javob yozing!*"
        )
        try:
            await client_tg.send_message(ADMIN_USERNAME, sos_xabar)
            await make_telegram_call(ADMIN_USERNAME)
            print(f"🚨 SOS #{urinish}: @{ADMIN_USERNAME} ga xabar yozildi va qo'ng'iroq qilindi!")
        except Exception as e:
            print(f"SOS yuborishda xato: {e}")
            await client_tg.send_message('me', sos_xabar)
            break

        # 35 soniya kutadi (shu vaqt ichida o'qisangiz yoki ko'tarsangiz darhol to'xtaydi)
        for _ in range(35):
            if not sos_active:
                break
            await asyncio.sleep(1)
        
        urinish += 1

    if not sos_active:
        try:
            await client_tg.send_message(ADMIN_USERNAME, "✅ **Xabarni ko'rdingiz, qayta qo'ng'iroq qilish to'xtatildi!**")
        except Exception:
            pass
    sos_active = False

# ==========================================
# 4. ASOSIY XABARLAR HANDLERI
# ==========================================
@client_tg.on(events.NewMessage())
async def handler(event):
    global bot_yoqilgan, sos_active
    chat_id = event.chat_id
    matn = (event.raw_text or "").strip()

    if event.out:
        cmd = matn.lower()
        if cmd == ".off":
            bot_yoqilgan = False
            sos_active = False
            await event.edit("🔴 **Yordamchi vaqtincha o'chirildi.**")
            return
        elif cmd == ".on":
            bot_yoqilgan = True
            await event.edit("🟢 **Yordamchi yoqildi!**")
            return
        elif cmd == ".stop":
            qora_royxat.add(chat_id)
            save_ignor(qora_royxat)
            await event.edit("🔇 *Bu chat qora ro'yxatga qo'shildi.*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd == ".start":
            qora_royxat.discard(chat_id)
            save_ignor(qora_royxat)
            await event.edit("🔊 *Bu chat uchun yordamchi qayta yoqildi!*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd == ".clear":
            xotira.pop(chat_id, None)
            await event.edit("🧹 *Suhbat xotirasi tozalandi!*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd.startswith(".ai "):
            savol = matn[4:]
            await event.edit("⏳ *O'ylanmoqda...*")
            for m in MODELLAR:
                try:
                    res = await asyncio.to_thread(client_ai.models.generate_content, model=m, contents=savol)
                    if res and res.text:
                        await event.edit(res.text)
                        break
                except Exception:
                    continue
            return
        else:
            if event.is_private and chat_id not in qora_royxat:
                qora_royxat.add(chat_id)
                save_ignor(qora_royxat)
                print(f"Siz chatga o'zingiz yozdingiz ({chat_id}). Bot bu chatda to'xtatildi (.start bilan yoqiladi).")
            return

    if not bot_yoqilgan or not event.is_private or chat_id in qora_royxat:
        return

    sender = await event.get_sender()
    if not sender or sender.bot:
        return

    # Agar @KurbanbayevSh (o'zingiz) botga javob yozsangiz, SOS trevogani darhol to'xtatadi:
    if getattr(sender, 'username', None) and sender.username.lower() == ADMIN_USERNAME.lower():
        if sos_active:
            sos_active = False
            await event.reply("✅ Trevoga to'xtatildi!")
            return

    ism = sender.first_name or "Foydalanuvchi"
    user_link = f"@{sender.username}" if sender.username else f"ID: {sender.id}"

    if not matn:
        if event.voice or event.audio or event.video_note:
            await event.reply("Assalomu alaykum! Men Sherzodning yordamchisiman. Hozir ovozli xabarlarni eshita olmayman, iltimos, gapingizni matn ko'rinishida yozib qoldiring.")
        return

    print(f"📩 [{ism}]: {matn}")

    if chat_id not in xotira:
        xotira[chat_id] = []
    
    xotira[chat_id].append(f"{ism}: {matn}")
    xotira[chat_id] = xotira[chat_id][-12:]
    suhbat_tarixi = "\n".join(xotira[chat_id])

    prompt = f"Suhbat tarixi:\n{suhbat_tarixi}\n\nOxirgi xabarga qoidalar asosida javob ber:"

    async with client_tg.action(chat_id, 'typing'):
        await asyncio.sleep(2)
        
        for model_nomi in MODELLAR:
            try:
                response = await asyncio.to_thread(
                    client_ai.models.generate_content,
                    model=model_nomi,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SHAXSIY_QOIDALAR,
                        temperature=0.7
                    )
                )
                if response and response.text:
                    javob = response.text.strip()
                    
                    # SHOSHILINCH HOLAT ANIQLANSA:
                    if "[SOS]" in javob:
                        javob = javob.replace("[SOS]", "").strip()
                        # Orqa fonda to'xtovsiz qo'ng'iroq va xabar funksiyasini ishga tushiramiz:
                        asyncio.create_task(sos_alarm_loop(ism, user_link, matn))

                    xotira[chat_id].append(f"Yordamchi: {javob}")
                    await event.reply(javob)
                    print(f"✅ [Yordamchi -> {ism}]: {javob}")
                    break
            except Exception as e:
                print(f"⚠️ {model_nomi} xatosi: {e}")
                continue

print("🚀 Uzluksiz SOS Qo'ng'iroq tizimli Yordamchi ishga tushdi!")
client_tg.start()
client_tg.run_until_disconnected()