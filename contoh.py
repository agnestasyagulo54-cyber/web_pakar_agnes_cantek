gejala_input = input("Masukkan gejala: ")
gejala_pasien = [g.strip().lower() for g in
gejala_input.split(",")]

knowledge_base = {
"Influenza": ["demam", "batuk"],
"Tifus": ["demam", "lemas"],
"Maag": ["mual", "nyeri perut"]
}

hasil = []
hasil = []
for penyakit, gejala in knowledge_base.items():
    if set(gejala).issubset(set(gejala_pasien)):
        hasil.append(penyakit)
if hasil:
    for p in hasil:
        print("Kemungkinan:", p)
else:
    print("Penyakit tidak ditemukan")