import asyncio
import json
import os
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telethon import TelegramClient, events, functions, types as tg_types
from google import genai
from google.genai import types
from gtts import gTTS

# --- RENDER UCHUN MINI VEB-SERVER (Bot o'chib qolmasligi uchun) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sherzod AI Yordamchisi 24/7 ishlamoqda!")

    def log_message(self, format, *args):
        pass  # Konsolni ortiqcha yozuvlar bilan to'ldirmaslik uchun

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"🌐 Render porti ({port}) ochildi!")
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()
# ------------------------------------------------------------------

API_ID = 32073192
API_HASH = "cae6b9040c05cdf61b6c154e2689b7b4"
GEMINI_KEY = "AQ.Ab8RN6KK5A7_CKLD9Co2uVn4ScWm4CVbSSQ1YxF4fo8bkiV23A"

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
1. Birinchi marta yozgan odamga o'zingni "Assalomu alaykum! Men Sherzodning shaxsiy yordamchisiman" deb tanishtir. Agar suhbat davom etayotgan bo'lsa, qayta-qayta salomlashaverma.
2. Sherzod hozir o'z loyihalari yoki ishlari bilan bandligini aytib, "Qanday masalada yozayotgan edingiz? Yozib qoldirsangiz, o'zlariga yetkazib qo'yaman" deb xushmuomalalik bilan so'ra.
3. Javoblaring xuddi haqiqiy aqlli yordamchinikidek qisqa (1-3 gap), tabiiy, samimiy va sof o'zbek tilida bo'lsin. Uzun robotdek matnlar yozma!
4. Suhbatdoshning oldingi gaplarini eslab qol va mantiqan davom ettir.
5. Agar odam shunchaki "Rahmat", "Xo'p", "Tushunarli" desa, qisqagina "Arzimaydi, salomat bo'ling!" deb suhbatni chiroyli yakunla.
6. MUHIM (SHOSHILINCH HOLAT): Agar suhbatdosh Sherzod juda tez kerakligini, ish juda zarur yoki shoshilinch ekanini aytsa, javobingning eng boshiga albatta [SOS] belgisini qo'y va unga shunday de:
"[SOS] Tushunarli, masala juda muhim ekan! Men hoziroq Sherzodga to'xtovsiz qo'ng'iroq qilib, siz haqingizda xabar beryapman. Agar juda shoshilinch bo'lsa, {ADMIN_PHONE} raqamiga yoki @{ADMIN_USERNAME} profiliga ham bog'lanishingiz mumkin."
"""

MODELLAR = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.8-flash-lite",
    "models/gemini-3.8-flash",
    "models/gemini-3.7-flash",
    "models/gemini-3.5-flash",
    "models/gemini-flash-lite-latest",
    "models/gemini-flash-latest"
]

IGNOR_FILE = "ignor_list.json"
HISTORY_FILE = "chat_history.json"

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

qora_royxat = set(load_json(IGNOR_FILE).get("ignors", []))
xotira = load_json(HISTORY_FILE)

def save_xotira():
    save_json(HISTORY_FILE, xotira)

bot_yoqilgan = True
sos_active = False

@client_tg.on(events.Raw)
async def call_state_handler(update):
    global sos_active
    if isinstance(update, tg_types.UpdatePhoneCall):
        call = update.phone_call
        if isinstance(call, (tg_types.PhoneCallAccepted, tg_types.PhoneCall)):
            if sos_active:
                sos_active = False
                print("✅ Qo'ng'iroq ko'tarildi! SOS trevoga to'xtatildi.")

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

async def make_telegram_call(target_user):
    try:
        user_entity = await client_tg.get_input_entity(target_user)
        protocol = tg_types.PhoneCallProtocol(
            min_layer=65, max_layer=92, udp_p2p=True, udp_reflector=True, library_versions=['2.4.4']
        )
        await client_tg(functions.phone.RequestCallRequest(
            user_id=user_entity, random_id=random.randint(1, 2147483647), g_a_hash=os.urandom(32), protocol=protocol
        ))
        return True
    except Exception as e:
        print(f"⚠️ Qo'ng'iroq xatosi: {e}")
        return False

async def sos_alarm_loop(ism, user_link, matn):
    global sos_active
    if sos_active:
        return
    sos_active = True
    urinish = 1

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
            print(f"SOS xatosi: {e}")
            await client_tg.send_message('me', sos_xabar)
            break

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

@client_tg.on(events.NewMessage())
async def handler(event):
    global bot_yoqilgan, sos_active
    chat_id = event.chat_id
    chat_id_str = str(chat_id)
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
            qora_royxat.add(chat_id_str)
            save_json(IGNOR_FILE, {"ignors": list(qora_royxat)})
            await event.edit("🔇 *Bu chat qora ro'yxatga qo'shildi.*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd == ".start":
            qora_royxat.discard(chat_id_str)
            save_json(IGNOR_FILE, {"ignors": list(qora_royxat)})
            await event.edit("🔊 *Bu chat uchun yordamchi qayta yoqildi!*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd == ".clear":
            xotira.pop(chat_id_str, None)
            save_xotira()
            await event.edit("🧹 *Suhbat xotirasi tozalandi!*")
            await asyncio.sleep(2)
            await event.delete()
            return
        elif cmd.startswith(".ai "):
            savol = matn[4:]
            await event.edit("⏳ *O'ylanmoqda...*")
            for m in MODELLAR:
                try:
                    res = await asyncio.to_thread(
                        client_ai.models.generate_content,
                        model=m,
                        contents=savol
                    )
                    if res and res.text:
                        await event.edit(res.text)
                        break
                except Exception:
                    continue
            return
        else:
            if event.is_private and chat_id_str not in qora_royxat:
                qora_royxat.add(chat_id_str)
                save_json(IGNOR_FILE, {"ignors": list(qora_royxat)})
                print(f"Siz chatga o'zingiz yozdingiz ({chat_id}). Bot bu chatda to'xtatildi.")
            return

    if not bot_yoqilgan or not event.is_private or chat_id_str in qora_royxat:
        return

    sender = await event.get_sender()
    if not sender or sender.bot:
        return

    if getattr(sender, 'username', None) and sender.username.lower() == ADMIN_USERNAME.lower():
        if sos_active:
            sos_active = False
            await event.reply("✅ Trevoga to'xtatildi!")
            return

    ism = sender.first_name or "Foydalanuvchi"
    user_link = f"@{sender.username}" if sender.username else f"ID: {sender.id}"

    contents_to_send = matn
    audio_file_path = None
    is_incoming_voice = False

    if event.voice or event.audio or event.video_note:
        is_incoming_voice = True
        print(f"🎤 [{ism}] dan ovozli xabar keldi, yuklab olinmoqda...")
        try:
            audio_file_path = await event.download_media(file="temp_audio.ogg")
            uploaded_file = await asyncio.to_thread(
                client_ai.files.upload, file=audio_file_path
            )
            contents_to_send = [
                uploaded_file, 
                "Bu ovozli xabarni tingla va Sherzodning yordamchisi sifatida qoidalarga mos ravishda matn bilan javob ber."
            ]
            matn = "[Ovozli xabar]"
        except Exception as e:
            print(f"Ovozli xabarni yuklashda xato: {e}")
            await event.reply("Assalomu alaykum! Ovozli xabaringizni o'qib bo'lmadi, iltimos matn yozib yuboring.")
            return
    elif not matn:
        return

    print(f"📩 [{ism}]: {matn}")

    if chat_id_str not in xotira:
        xotira[chat_id_str] = []
    
    xotira[chat_id_str].append(f"{ism}: {matn}")
    xotira[chat_id_str] = xotira[chat_id_str][-15:]
    save_xotira()
    
    suhbat_tarixi = "\n".join(xotira[chat_id_str])

    if audio_file_path:
        final_contents = contents_to_send
    else:
        final_contents = f"Suhbat tarixi:\n{suhbat_tarixi}\n\nOxirgi xabarga qoidalar asosida javob ber:"

    async with client_tg.action(chat_id, 'typing'):
        await asyncio.sleep(2)
        
        for model_nomi in MODELLAR:
            try:
                response = await asyncio.to_thread(
                    client_ai.models.generate_content,
                    model=model_nomi,
                    contents=final_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SHAXSIY_QOIDALAR,
                        temperature=0.7
                    )
                )
                if response and response.text:
                    javob = response.text.strip()
                    
                    if "[SOS]" in javob:
                        javob = javob.replace("[SOS]", "").strip()
                        asyncio.create_task(sos_alarm_loop(ism, user_link, matn))

                    xotira[chat_id_str].append(f"Yordamchi: {javob}")
                    save_xotira()
                    
                    if is_incoming_voice:
                        try:
                            tts = gTTS(text=javob, lang='uz')
                            voice_path = "response_voice.ogg"
                            tts.save(voice_path)
                            await event.reply(file=voice_path, voice_note=True)
                            if os.path.exists(voice_path):
                                os.remove(voice_path)
                            print(f"🔊 [Ovozli javob yuborildi -> {ism}]")
                        except Exception as ex:
                            print(f"Ovozli javobni yuborishda xato: {ex}")
                            await event.reply(javob)
                    else:
                        await event.reply(javob)
                        
                    print(f"✅ [Yordamchi ({model_nomi}) -> {ism}]: {javob}")
                    break
            except Exception as e:
                print(f"⚠️ {model_nomi} xatosi: {e}")
                continue

    if audio_file_path and os.path.exists(audio_file_path):
        try:
            os.remove(audio_file_path)
        except Exception:
            pass

print("🚀 Serverga moslangan Mukammal Yordamchi ishga tushdi!")
client_tg.start()
client_tg.run_until_disconnected()
