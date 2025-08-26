from supabase import create_client, Client
from rfid import rfid
from dotenv import dotenv_values
from model import predict

env = dotenv_values(".env")

url: str = env['SUPABASE_URL']
key: str = env['SUPABASE_KEY']

supabase: Client = create_client(url, key)

def register(id):
    try:
        response = supabase.from_("DataAnak").insert({"id": id}).execute()
        return response
    except Exception as e:
        return {"error": str(e)}

def analisis():
    anak_id = rfid()
    hasil_predict = predict()

    try:
        # 1. Cek apakah anak_id sudah ada di DataAnak
        check = supabase.from_("DataAnak").select("id").eq("id", anak_id).execute()

        if not check.data:  # kalau belum ada → register
            reg_res = register(anak_id)
            if "error" in reg_res:
                return {"status": "error", "message": reg_res["error"]}

        # 2. Insert ke Analisis
        insert_response = supabase.from_("Analisis").insert({
            "id_anak": anak_id,
            "tinggi": hasil_predict["tinggi"],
            "berat": hasil_predict["berat"],
            "haz": hasil_predict["haz"],
            "status_tinggi": hasil_predict["status_tinggi"],
            "status_berat": hasil_predict["status_berat"],
            "gambar": ""
        }).execute()

        # 3. Update DataAnak
        update_response = supabase.from_("DataAnak").update({
            "status_tinggi": hasil_predict["status_tinggi"],
            "status_berat": hasil_predict["status_berat"]
        }).eq("id", anak_id).execute()

        return {
            "status": "success",
            "insert": insert_response.data,
            "update": update_response.data
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

print(analisis())
