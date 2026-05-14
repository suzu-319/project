import csv
from flask import Flask, render_template, request

app = Flask(__name__)

# 薬データ（併用はそのまま）
interactions = {
    ("ロキソニン", "カロナール"): "併用時は注意してください"
}
ingredient_group = {
    "ロキソプロフェン": "NSAIDs",
    "イブプロフェン": "NSAIDs",
    "アスピリン": "NSAIDs",

    "アセトアミノフェン": "解熱鎮痛",

    "ロラタジン": "抗ヒスタミン",
    "フェキソフェナジン": "抗ヒスタミン",
    "セチリジン": "抗ヒスタミン"
}

# 薬CSV読み込み
def load_medicines():
    medicines = {}

    with open("medicines.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row = {k.strip(): v for k, v in row.items()}
            medicines[row["name"].strip()] = {
                "ingredient": row["ingredient"],
                "effect": row["effect"],
                "warning": row["warning"],
                "symptoms": row["symptoms"]
            }           

    return medicines

def get_ingredient(medicines, name):
    return medicines.get(name, {}).get("ingredient")



def get_symptom_list(medicines):
    symptom_set = set()

    for data in medicines.values():
        symptoms = data.get("symptoms", "")
        for s in symptoms.split("|"):
            symptom_set.add(s.strip())

    return sorted(symptom_set)


@app.route("/", methods=["GET", "POST"])
def index():

    medicines = load_medicines()
    symptom_list = get_symptom_list(medicines)

    medicine_result = None
    symptom_result = []
    interaction_result = ""

    if request.method == "POST":

        action = request.form.get("action")

        # 薬検索
        if action == "medicine":
            name = request.form.get("medicine","")
            name = name.strip() if name else ""
            if name:
                medicine_result = medicines.get(name)

        # 症状検索
        elif action == "symptom":
            symptom_name = request.form.get("symptom","").strip()

            symptom_result = set()

            for medicine_name, data in medicines.items():
                symptoms = data.get("symptoms","")

                symptom_list_data = [s.strip() for s in symptoms.split("|") if s.strip()]

                if symptom_name in symptom_list_data:
                    symptom_result.add(medicine_name)

            symptom_result = list(symptom_result)


        # 併用チェック
        elif action == "interaction":
            med1 = request.form.get("med1","").strip()
            med2 = request.form.get("med2","").strip()
            ing1 = get_ingredient(medicines, med1)
            ing2 = get_ingredient(medicines, med2)
            if not ing1 or not ing2:
                interaction_result = "薬名が見つかりません"
            else:
                group1 = ingredient_group.get(ing1)
                group2 = ingredient_group.get(ing2)
                if ing1 == ing2:
                    interaction_result = "同じ成分なので併用注意"
                elif group1 and group1 == group2:
                    interaction_result = f"同系統（{group1}）のため併用注意"
                elif not group1 or not group2:
                    interaction_result = "注意：成分情報が不足しています"
                else:
                    interaction_result = "重大な併用注意はありません"

    return render_template(
        "index.html",
        medicine_result=medicine_result,
        symptom_result=symptom_result,
        interaction_result=interaction_result,
        symptom_list=symptom_list
    )


if __name__ == "__main__":
    app.run(debug=True)