#!python3

from pprint import pprint
from openai import OpenAI
import base64
import os
import requests
import json
from time import sleep
import mysql.connector
import bcrypt
import jwt
#from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def get_db_connection():
    return mysql.connector.connect(
        host='database-1.cp8im2sk8sm3.us-east-2.rds.amazonaws.com',
        user='admin',
        password='adminpassword',
        database='recipe_app'
    )


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Store the new user in the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        conn.commit()
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            return jsonify({'message': 'Username already exists'}), 409
        else:
            return jsonify({'message': 'An error occurred'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'User created successfully'}), 201


@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        # Generate JWT token
        token = jwt.encode({'id': user['id'], 'username': user['username']}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'user_id': user['id']}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route("/generate_recipe", methods=['GET'])
def api():
    prompt = request.args.get('prompt')
    print(prompt)

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": "I'd like you to please help generate recipes for me if I give you a list of ingredients and/or maximum number of ingredients (salt and pepper don't count) or describe what I'm in the mood for. I may also give a number of servings. Can you please format your whole response in JSON format, with separate keys for the title, ingredients, instructions, servings, an image_prompt, and any other response message. Each ingredient and instruction should be a single string without any numbering"},
        {"role": "user", "content": prompt}
      ],
      response_format={'type': 'json_object'},
      temperature=1,
      max_tokens=1024,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    #pprint(response.choices[0].message.content)
    resp = dict(response)['choices'][0].message.content
    resp = resp.replace('```json','').replace('```', '')
    print(resp)

    return resp

    
@app.route("/image", methods=['POST'])
def image():
    engine_id = "stable-diffusion-v1-6"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = os.environ.get('STABILITY_API_KEY')
    title = request.json.get('title').replace(' ', '_')
    user_id = request.json.get('user_id')
    prompt = request.json.get('prompt')

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [ {"text": prompt} ],
            "height": 1024,
            "width": 1024,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    for i, image in enumerate(data["artifacts"]):
        with open(f"/home/ec2-user/recipe_app/images/{title}_{user_id}.png", "wb") as f:
            f.write(base64.b64decode(image["base64"]))

    return {'img': data['artifacts'][0]['base64']}


@app.route("/get_saved_image", methods=['GET'])
def get_saved_image():
    user_id = request.args.get('user_id')
    title = request.args.get('title').replace(' ', '_')
    image_path = f"/home/ec2-user/recipe_app/images/{title}_{user_id}.png"


    # Check if the file exists
    if not os.path.exists(image_path):
        print("image_path:", image_path)
        return jsonify({'error': 'Image not found'}), 404

    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    # You can return the base64 string in JSON format
    return jsonify({'image': encoded_image})


@app.route('/save_recipe', methods=['POST'])
#@jwt_required()  # Ensure the user is authenticated
def save_recipe():
    data = request.json
    user_id = data.get('user_id')
    title = data.get('title')
    ingredients = data.get('ingredients')  # Expecting a list
    instructions = data.get('instructions')  # Expecting a list
    image_path = data.get('image_path')
    image_prompt = data.get('image_prompt')
    print('image_prompt:', image_prompt)
    servings = data.get('servings')

    print('image path:', image_path)

    if not all([user_id, title, ingredients, instructions, image_prompt, servings]):
        return jsonify({'message': 'Missing required fields'}), 400

    # Convert lists to JSON strings to store in the database
    ingredients_json = json.dumps(ingredients)
    instructions_json = json.dumps(instructions)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM recipes WHERE title = %s and user_id = %s', (title, user_id))
        recipe = cursor.fetchone()

        if recipe:
            cursor.execute('''
                UPDATE recipes 
                SET user_id = %s, title = %s, ingredients = %s, instructions = %s, image_path = %s, image_prompt = %s, servings = %s
                WHERE title = %s and user_id = %s
            ''', (user_id, title, ingredients_json, instructions_json, image_path, image_prompt, servings, title, user_id))
            #conn.commit()

            return jsonify({'message': 'Recipe updated'}), 200

        cursor.execute('''
            INSERT INTO recipes (user_id, title, ingredients, instructions, image_path, image_prompt, servings)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, title, ingredients_json, instructions_json, image_path, image_prompt, servings))
        conn.commit()
    except mysql.connector.Error as err:
        print(err)
        return jsonify({'message': 'An error occurred while saving the recipe'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Recipe saved successfully'}), 201


#@app.route('/recipes/<int:recipe_id>', methods=['GET'])
@app.route('/get_saved_recipe', methods=['GET'])
#@jwt_required()  # Ensure the user is authenticated
def get_recipe():
    recipe_id = request.args.get('recipe_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
    recipe = cursor.fetchone()

    if not recipe:
        return jsonify({'message': 'Recipe not found'}), 404

    # Convert JSON strings back to Python lists
    recipe['ingredients'] = json.loads(recipe['ingredients'])
    recipe['instructions'] = json.loads(recipe['instructions'])

    cursor.close()
    conn.close()

    return jsonify(recipe), 200


#@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
@app.route('/delete_recipe', methods=['DELETE'])
#@jwt_required()  # Ensure the user is authenticated
def delete_recipe():
    print('body:', request.json)
    user_id = request.json.get('user_id')
    recipe_id = request.json.get('recipe_id')
    title = request.json.get('title').replace(' ', '_')
    print('title:', title)
    image_path = f"/home/ec2-user/recipe_app/images/{title}_{user_id}.png"
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Execute delete query to remove the recipe with the specified ID
        cursor.execute('DELETE FROM recipes WHERE id = %s', (recipe_id,))
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return jsonify({'message': 'Recipe not found'}), 404

        if os.path.exists(image_path):
            os.remove(image_path)
        #else:
            #return jsonify({'message': 'Recipe image not found'}), 404

        return jsonify({'message': 'Recipe deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'message': 'An error occurred while deleting the recipe'}), 500

    finally:
        cursor.close()
        conn.close()


#@app.route('/users/<int:user_id>/recipes', methods=['GET'])
@app.route('/get_user_saved_recipes', methods=['GET'])
#@jwt_required()  # Ensure the user is authenticated
def get_recipes_by_user():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Query to get recipe titles and ids for the given user_id
        cursor.execute('SELECT id, title FROM recipes WHERE user_id = %s', (user_id,))
        recipes = cursor.fetchall()

        # Format the result as a list of dictionaries with title and id
        recipe_list = [{'title': recipe['title'], 'id': recipe['id']} for recipe in recipes]
    except mysql.connector.Error as err:
        return jsonify({'message': 'An error occurred while fetching the recipes'}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(recipe_list), 200

    
if __name__ == "__main__":
    app.run(host='0.0.0.0')



