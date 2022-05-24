from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://jackson:mwaniki@cluster0.qwpxl.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    response = MessagingResponse()
    user = users.find_one({"number": number})

    if bool(user) == False:
        response.message("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: "
                         "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                         "To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)

        if option == 1:
            response.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: +254715617028 \n*E-mail* : j.gitundu@elloe.ai")
        elif option == 2:
            response.message("You have entered *ordering mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            response.message(
                "You can select one of the following cakes to order: \n\n1️⃣ Red Velvet  \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ Go Back")
        elif option == 3:
            response.message("We work from *9 a.m. to 5 p.m*.")
        elif option == 4:
            response.message("We have multiple stores across the city. Our main center is at *Moi Avenue, Nairobi*")
        else:
            response.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            response.message("You can choose from one of the options below: "
                             "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                             "To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            response.message("Excellent choice 😉")
            response.message("Please enter your address to confirm the order")
        else:
            response.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"];
        response.message("Thank you for shopping with us!")
        response.message(f"Your order for *{selected}* has been received and will be delivered *within an hour*")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_date": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        response.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                         "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                         "To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(response)


if __name__ == "__main__":
    app.run()
