from time import time
import csv
import re

t0 = time()

getDayAndMonthPattern = re.compile("\(([^)]+)\)")
getLunchOrDinnerPattern = re.compile("(Almoço|Janta)")

rawMsgs = []
with open("Telegram-Super_Família_ICMC.csv", encoding="UTF-8") as f:
    for _, timestamp, sender, _, _, content in csv.reader(f):
        if sender != "Bandejao": continue

        if "fechado" in content.lower(): continue
        if "feriado" in content.lower(): continue
        if ":" not in content: continue
        if "@Kasama" in content: continue
        if "Operação finalizada" in content: continue
        if "cardapio_semanal_restaurante_area_1.pdf" in content: continue
        if "Dia                          Almoço" in content: continue

        d, m, y = [int(i) for i in timestamp.split()[0].split(".")]

        if not (y == 2016 or (y == 2017 and m <= 3 and m <= 10)) and "São Carlos, Área 1" not in content: continue

        content = "".join([s for s in content if s])
        content = content.replace("ª", "ã")
        content = content.replace(".", "")
        content = content.replace(",", "")
        # content = content.replace(":", "")
        content = [s.strip() for s in content.split("\\n")]

        if "São Carlos" in content[0]: content = content[1:]
        if "Kcal" in content[-1]: content = content[:-1]

        timestamp = timestamp.split()[1]

        dayAndMonth = re.findall(getDayAndMonthPattern, content[0])
        if not dayAndMonth: continue
        dayMonthYear = "/".join(["{:02}".format(int(i)) for i in dayAndMonth[0].split("/")]) + "/" + str(y)

        lunchOrDinner = re.findall(getLunchOrDinnerPattern, content[0])
        lunchOrDinner = "Almoço" if lunchOrDinner[0] != "Janta" else "Jantar"
        
        meal = " ".join([s.strip() for s in content if s][1:]).replace("/", " ")
        meal = " ".join(s for s in meal.split(" ") if s)        
        if len(meal) < 50: continue

        msg = {"timestamp": timestamp,
               "dayMonthYear": dayMonthYear,
               "lunchOrDinner": lunchOrDinner,
               "meal": meal}
        rawMsgs.append(msg)

msgs = dict()
for msg in rawMsgs:
    key = (msg["dayMonthYear"], msg["lunchOrDinner"])
    value = (msg["timestamp"], msg["meal"])
    if key in msgs:
        if msg["timestamp"] > msgs[key][0]:
            msgs[key] = value
    else:
        msgs[key] = value

msgs = [[k[0], k[1], v[1]] for k, v in msgs.items()]
msgs = sorted(list(msgs), key=(lambda x: ("".join(x[0].split("/")[::-1]), x[0])))

with open("raw_meals.csv", "w+", encoding="UTF-8", newline="") as f:
    csv.writer(f).writerows(msgs)

print("{} entries written successfully in {:.2f}s.".format(len(msgs), time()-t0))