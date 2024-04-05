from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL connection configuration
mysql_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Function to retrieve CGPA from MySQL based on roll number and branch
def get_cgpa(roll_number, branch):
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Query to fetch CGPA based on roll number and branch
        query = "SELECT cgpa FROM student_data WHERE roll_number = %s AND branch = %s"
        cursor.execute(query, (roll_number, branch))
        
        # Fetching CGPA from the result
        cgpa = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if cgpa:
            return cgpa[0]
        else:
            return None
    except Exception as e:
        print("Error while retrieving CGPA:", e)
        return None

# Webhook route for Dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    action = req.get('queryResult').get('action')
    
    if action == 'get_cgpa':
        parameters = req['queryResult']['parameters']
        roll_number = parameters.get('roll-number')
        branch = parameters.get('branch')
        
        cgpa = get_cgpa(roll_number, branch)
        
        if cgpa is not None:
            fulfillment_text = f"The CGPA of {roll_number} in {branch} branch is {cgpa}."
        else:
            fulfillment_text = "Sorry, I couldn't find CGPA for the given roll number and branch."
        
        response = {
            "fulfillmentText": fulfillment_text
        }
        return jsonify(response)
    else:
        return jsonify({"fulfillmentText": "Unknown action"})


if __name__ == '__main__':
    app.run(debug=True)
