import os
import traceback
import bson # type: ignore
import json
import http.client

from cryptography.fernet import Fernet # type: ignore

#project api key : sk-proj-t6V4z2BCXGS9i2e2A7jaT3BlbkFJVOUCg85KM8LZQ1tLQQfL
from bson import ObjectId # type: ignore
from flask import (Flask, jsonify, redirect, render_template, request, # type: ignore
                   send_from_directory, url_for)

from pymongo import MongoClient # type: ignore
from pymongo.collection import Collection # type: ignore
from pymongo.database import Database # type: ignore

# access your MongoDB Atlas cluster
#load_dotenv()
connection_string: str = "mongodb+srv://victorbar40:mongodb@cluster0.tfajwbo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"#os.environ.get("CONNECTION_STRING")
mongo_client: MongoClient = MongoClient(connection_string)

# # add in your database and collection from Atlas
database: Database = mongo_client.get_database("bookshelf")
collection: Collection = database.get_collection("books")

collectionUsers: Collection = database.get_collection("users")
key = "a7zXj8pQKRd_r7Cz7e_TRLIuT_7T2Aq2Uv6t4R9QRUI="#Fernet.generate_key()
fernet = Fernet(key)

app = Flask(__name__)

# sample code ######################################
@app.route('/')
def index2():
   print('Request for index page received')
   return render_template('index2.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
# Sample Code #######################################

# our initial form page
#@app.route('/')  # root is "/"
#def index():
#    return render_template("index.html")

############################ BOOKS ##############################
# CREATE and READ
@app.route('/books', methods=["GET", "POST"])
def books():
    if request.method == 'POST':
        # CREATE
        book: str = request.json['book']
        pages: str = request.json['pages']

        # insert new book into books collection in MongoDB
        collection.insert_one({"book": book, "pages": pages})

        return f"CREATE: Your book {book} ({pages} pages) has been added to your bookshelf.\n "

    elif request.method == 'GET':
        # READ
        bookshelf = list(collection.find())
        novels = []

        for titles in bookshelf:
            book = titles['book']
            pages = titles['pages']
            shelf = {'book': book, 'pages': pages}
            novels.insert(0, shelf)

        return novels


# UPDATE
@app.route("/books/<string:book_id>", methods=['PUT'])
def update_book(book_id: str):
   new_book: str = request.json['book']
   new_pages: str = request.json['pages']
   collection.update_one({"_id": bson.ObjectId(book_id)}, {"$set": {"book": new_book, "pages": new_pages}})

   return f"UPDATE: Your book has been updated to: {new_book} ({new_pages} pages).\n"


# DELETE
@app.route("/books/<string:book_id>", methods=['DELETE'])
def remove_book(book_id: str):
   collection.delete_one({"_id": bson.ObjectId(book_id)})

   return f"DELETE: Your book (id = {book_id}) has been removed from your bookshelf.\n"

###############################################################
key = Fernet.generate_key()
fernet = Fernet(key)

# Example endpoint to receive a parameter in the URL and return a response
def call_chat_gpt_api(prompt):
    try:
        # Establish connection to the API endpoint
        conn = http.client.HTTPSConnection("api.openai.com")
        
        # Set headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-proj-t6V4z2BCXGS9i2e2A7jaT3BlbkFJVOUCg85KM8LZQ1tLQQfL"
        }
        #api_key = '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'
        # Prepare the data to send
        payload = {
            "model": "gpt-4-turbo",  # Model name
            "response_format": {"type": "json_object"},
            "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant. Your response should be in JSON format."
          },
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": prompt
              },
            ]
          }
        ] 
            #"max_tokens": 1000              # Max tokens to generate
        }
        
        # Convert payload to JSON
        json_payload = json.dumps(payload)
        
        # Send POST request to the API
        conn.request("POST", "/v1/chat/completions", json_payload, headers)
        
        # Get response
        response = conn.getresponse()
        
        # Read response data
        data = response.read().decode("utf-8")
        
        # Print response data for debugging
        print("Response:", data)
        
        # Convert response JSON to dictionary
        response_data = json.loads(data)
        
        # Check if 'choices' key exists in response
        if 'choices' in response_data:
            # Return the generated text
            return response_data['choices'][0]['message']['content']
        else:
            print("Unexpected response format:", response_data)
            return None
        
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/gpt', methods=['POST'])
def gpt():
    try:
        # Get the prompt from the POST request
        prompt = "hello , who is the president of US today?"
        
        # Print request data for debugging
        print("Request data:", request.form)
        
        generated_text = call_chat_gpt_api(prompt)
        return jsonify({"generated_text": generated_text})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)})      


class OpenAiServer:
    # Replace 'YOUR_API_KEY' with your actual OpenAI API key
    api_key = 'sk-proj-t6V4z2BCXGS9i2e2A7jaT3BlbkFJVOUCg85KM8LZQ1tLQQfL'
    #api_url = 'https://api.openai.com/v1/chat/completions'
    api_url = 'api.openai.com'

    def ask_gpt_about_workout_plan(self, gender, age, height, weight, training_frequency, fitness_level):
        gpt_prompt = f'create a workout plan for the gym (that consists of : a random 2-3 warmup exercises, 4-5 random hard strength exercises , different for each day , and a random 2-3 stretching exercises in the end for each day of workout) for the following properties: gender: {gender} age: {age} height: {height}, weight: {weight}, training Frequency in days per week: {training_frequency}, level at the gym: {fitness_level}. return the plan as a json format without the intro. for each exercise show a description of 2-3 sentences. \
        dont forget to match between the {training_frequency} to the amount of the workout plan days. \
        for example if {training_frequency} is 5, show me a workout plan of 5 days per week,'

        
        json_example = """workout plan example for 5 days:
        {
  "Day 1": {
    "Warmup": {
      "Exercise 1": {
        "Name": "Jumping Jacks",
        "Description": "Start your workout with jumping jacks to elevate your heart rate and warm up your entire body. Jumping jacks engage multiple muscle groups and help improve cardiovascular endurance, setting a strong foundation for the rest of your session.",
        "Image_URL": "https://i.ibb.co/YDJ9BRG/Jumping-jacks.jpg"
      },
      "Exercise 2": {
        "Name": "Arm Circles",
        "Description": "Follow up with arm circles to increase shoulder mobility and flexibility. Arm circles also help in loosening up the shoulder joints, reducing the risk of injury during strength training exercises.",
        "Image_URL": "https://i.ibb.co/WD07QBF/arm-circles.jpg"
      }
    },
    "Strength_Exercises": {
      "Exercise 1": {
        "Name": "Deadlifts",
        "Description": "Incorporate deadlifts to strengthen your posterior chain, including your lower back, glutes, and hamstrings. Deadlifts are a powerful compound movement that promotes functional strength and muscle growth.",
        "Image_URL": "https://i.ibb.co/ygw8qxd/Deadlifts.jpg"
      },
      "Exercise 2": {
        "Name": "Bench Press",
        "Description": "Include bench press to develop upper body strength, particularly targeting the chest, shoulders, and triceps. Bench press is a key exercise for building muscle mass and improving pushing strength.",
        "Image_URL": "https://i.ibb.co/YdKKKmy/Bench-Press.jpg"
      },
      "Exercise 3": {
        "Name": "Pull-Ups",
        "Description": "Integrate pull-ups into your routine to strengthen your back, biceps, and grip. Pull-ups are a challenging bodyweight exercise that enhance upper body muscle definition and improve overall pulling strength.",
        "Image_URL": "https://i.ibb.co/By8t61S/Pull-Ups.jpg"
      },
      "Exercise 4": {
        "Name": "Overhead Press",
        "Description": "Incorporate overhead press to build shoulder strength and stability. Overhead press targets the deltoids, triceps, and upper back muscles, contributing to balanced upper body development.",
        "Image_URL": "https://i.ibb.co/Y0HFCN7/Overhead-Press.jpg"
      },
      "Exercise 5": {
        "Name": "Lat Pulldowns",
        "Description": "Perform lat pulldowns to strengthen your latissimus dorsi, biceps, and upper back. Lat pulldowns help in improving back aesthetics and overall upper body strength.",
        "Image_URL": "https://i.ibb.co/yh6ZZH0/Lat-Pulldowns.webp"
      }
    },
    "Stretching": {
      "Exercise 1": {
        "Name": "Forward Fold",
        "Description": "Finish your workout with a forward fold to stretch your hamstrings and lower back. This helps in relieving tension built up during the workout and promotes flexibility.",
        "Image_URL": "https://i.ibb.co/xH33Smg/Forward-Fold.jpg"
      },
      "Exercise 2": {
        "Name": "Chest Stretch",
        "Description": "Conclude your session with a chest stretch to open up your chest and shoulders. This stretch helps in improving posture and reducing tightness in the chest muscles.",
        "Image_URL": "https://i.ibb.co/2qs6TH7/Chest-Stretch.webp"
      }
    }
  },
  "Day 2": {
    "Warmup": {
      "Exercise 1": {
        "Name": "High Knees",
        "Description": "Start your workout with high knees to increase your heart rate and warm up your lower body. High knees also help in improving coordination and agility.",
        "Image_URL": "https://i.ibb.co/d6BXzrk/High-knees.webp"
      },
      "Exercise 2": {
        "Name": "Jump Rope",
        "Description": "Follow up with jump rope to further elevate your heart rate and enhance coordination. Jump rope is a versatile exercise that targets multiple muscle groups while improving cardiovascular fitness.",
        "Image_URL": "https://i.ibb.co/bgPgf1k/Jump-Rope.png"
      }
    },
    "Strength_Exercises": {
      "Exercise 1": {
        "Name": "Squats",
        "Description": "Perform squats to target your quadriceps, hamstrings, and glutes. Squats are a fundamental compound exercise that builds lower body strength and enhances overall stability and balance.",
        "Image_URL": "https://i.ibb.co/vvGK5w1/Squat.jpg"
      },
      "Exercise 2": {
        "Name": "Deadlifts",
        "Description": "Incorporate deadlifts to strengthen your posterior chain, including your lower back, glutes, and hamstrings. Deadlifts are a powerful compound movement that promotes functional strength and muscle growth.",
        "Image_URL": "https://i.ibb.co/ygw8qxd/Deadlifts.jpg"
      },
      "Exercise 3": {
        "Name": "Push-Ups",
        "Description": "Include push-ups to develop upper body strength, targeting the chest, shoulders, and triceps. Push-ups also engage the core muscles and improve overall muscular endurance.",
        "Image_URL": "https://i.ibb.co/dbr0L5q/Push-Ups.jpg"
      },
      "Exercise 4": {
        "Name": "Barbell Rows",
        "Description": "Integrate barbell rows to strengthen your upper back, biceps, and grip. Barbell rows also improve posture and help in preventing upper back pain.",
        "Image_URL": "https://i.ibb.co/WBT0TnS/Barbell-Rows.webp"
      },
      "Exercise 5": {
        "Name": "Dumbbell Lunges",
        "Description": "Perform dumbbell lunges to target your quadriceps, hamstrings, and glutes. Lunges help in improving lower body strength and balance while enhancing hip flexibility.",
        "Image_URL": "https://i.ibb.co/NghffkK/Dumbbell-Lunges.jpg"
      }
    },
    "Stretching": {
      "Exercise 1": {
        "Name": "Hamstring Stretch",
        "Description": "Finish your workout with a hamstring stretch to improve flexibility and reduce the risk of injury. Hamstring stretches target the muscles at the back of your thighs, helping in relieving tightness and promoting better range of motion.",
        "Image_URL": "https://i.ibb.co/4dLDVh8/Hamstring-Stretch.jpg"
      },
      "Exercise 2": {
        "Name": "Shoulder Stretch",
        "Description": "Conclude your session with a shoulder stretch to alleviate tension and improve mobility in the shoulder joints. Shoulder stretches target the deltoids and rotator cuff muscles, promoting better posture and reducing stiffness.",
        "Image_URL": "https://i.ibb.co/1R5Gk9h/Shoulder-Stretch.webp"
      }
    }
  },
  "Day 3": {
    "Warmup": {
      "Exercise 1": {
        "Name": "Burpees",
        "Description": "Start your workout with burpees to elevate your heart rate and engage multiple muscle groups. Burpees are an efficient full-body exercise that improves cardiovascular fitness and boosts metabolism.",
        "Image_URL": "https://i.ibb.co/C73CrMY/Burpees.jpg"
      },
      "Exercise 2": {
        "Name": "Mountain Climbers",
        "Description": "Follow up with mountain climbers to further activate your core and lower body muscles. Mountain climbers also help in improving coordination and agility.",
        "Image_URL": "https://i.ibb.co/VLqwBdg/Mountain-Climbers.png"
      }
    },
    "Strength_Exercises": {
      "Exercise 1": {
        "Name": "Romanian Deadlifts",
        "Description": "Incorporate Romanian deadlifts to target your hamstrings, glutes, and lower back muscles. Romanian deadlifts are effective for strengthening the posterior chain and improving hip hinge mechanics.",
        "Image_URL": "https://i.ibb.co/4MCH0hY/Romanian-Deadlifts.webp"
      },
      "Exercise 2": {
        "Name": "Dumbbell Bench Press",
        "Description": "Include dumbbell bench press to develop chest, shoulder, and triceps strength. Dumbbell bench press offers a greater range of motion compared to barbell bench press, enhancing muscle activation and stability.",
        "Image_URL": "https://i.ibb.co/RbJwpvn/Dumbbell-Bench-Press.webp"
      },
      "Exercise 3": {
        "Name": "Chin-Ups",
        "Description": "Integrate chin-ups into your routine to strengthen your back, biceps, and grip. Chin-ups are a challenging bodyweight exercise that improves upper body strength and muscle definition.",
        "Image_URL": "https://i.ibb.co/n67Vpch/Chin-Ups.jpg"
      },
      "Exercise 4": {
        "Name": "Barbell Squats",
        "Description": "Perform barbell squats to target your quadriceps, hamstrings, and glutes. Barbell squats are a compound exercise that builds lower body strength and improves functional movement patterns.",
        "Image_URL": "https://i.ibb.co/R2tcgPx/Barbell-squats.jpg"
      }
    },
    "Stretching": {
      "Exercise 1": {
        "Name": "Quad Stretch",
        "Description": "Finish your workout with a quad stretch to release tension in your quadriceps muscles. Quad stretches help in improving flexibility and preventing muscle imbalances.",
        "Image_URL": "https://i.ibb.co/4K09n27/Quad-Stretch.jpg"
      },
      "Exercise 2": {
        "Name": "Triceps Stretch",
        "Description": "Conclude your session with a triceps stretch to alleviate tightness in the back of your arms. Triceps stretches help in improving range of motion and reducing the risk of injury.",
        "Image_URL": "https://i.ibb.co/yyhprW7/Triceps-Stretch.jpg"
      }
    }
  },
  "Day 4": {
    "Warmup": {
      "Exercise 1": {
        "Name": "Jumping Jacks",
        "Description": "Start your workout with jumping jacks to elevate your heart rate and warm up your entire body. Jumping jacks engage multiple muscle groups and help improve cardiovascular endurance, setting a strong foundation for the rest of your session.",
        "Image_URL": "https://i.ibb.co/YDJ9BRG/Jumping-jacks.jpg"
      },
      "Exercise 2": {
        "Name": "Arm Circles",
        "Description": "Follow up with arm circles to increase shoulder mobility and flexibility. Arm circles also help in loosening up the shoulder joints, reducing the risk of injury during strength training exercises.",
        "Image_URL": "https://i.ibb.co/WD07QBF/arm-circles.jpg"
      }
    },
    "Strength_Exercises": {
      "Exercise 1": {
        "Name": "Deadlifts",
        "Description": "Incorporate deadlifts to strengthen your posterior chain, including your lower back, glutes, and hamstrings. Deadlifts are a powerful compound movement that promotes functional strength and muscle growth.",
        "Image_URL": "https://i.ibb.co/ygw8qxd/Deadlifts.jpg"
      },
      "Exercise 2": {
        "Name": "Bench Press",
        "Description": "Include bench press to develop upper body strength, particularly targeting the chest, shoulders, and triceps. Bench press is a key exercise for building muscle mass and improving pushing strength.",
        "Image_URL": "https://i.ibb.co/YdKKKmy/Bench-Press.jpg"
      },
      "Exercise 3": {
        "Name": "Pull-Ups",
        "Description": "Integrate pull-ups into your routine to strengthen your back, biceps, and grip. Pull-ups are a challenging bodyweight exercise that enhance upper body muscle definition and improve overall pulling strength.",
        "Image_URL": "https://i.ibb.co/8cG66R9/Pull-Ups.jpg"
      },
      "Exercise 4": {
        "Name": "Overhead Press",
        "Description": "Incorporate overhead press to build shoulder strength and stability. Overhead press targets the deltoids, triceps, and upper back muscles, contributing to balanced upper body development.",
        "Image_URL": "https://i.ibb.co/SRhMsNN/Overhead-Press.jpg"
      },
      "Exercise 5": {
        "Name": "Lat Pulldowns",
        "Description": "Perform lat pulldowns to strengthen your latissimus dorsi, biceps, and upper back. Lat pulldowns help in improving back aesthetics and overall upper body strength.",
        "Image_URL": "https://i.ibb.co/7kqQQwN/Lat-Pulldowns.webp"
      }
    },
    "Stretching": {
      "Exercise 1": {
        "Name": "Forward Fold",
        "Description": "Finish your workout with a forward fold to stretch your hamstrings and lower back. This helps in relieving tension built up during the workout and promotes flexibility.",
        "Image_URL": "https://i.ibb.co/xH33Smg/Forward-Fold.jpg"
      },
      "Exercise 2": {
        "Name": "Chest Stretch",
        "Description": "Conclude your session with a chest stretch to open up your chest and shoulders. This stretch helps in improving posture and reducing tightness in the chest muscles.",
        "Image_URL": "https://i.ibb.co/2qs6TH7/Chest-Stretch.webp"
      }
    }
  },
  "Day 5": {
    "Warmup": {
      "Exercise 1": {
        "Name": "Burpees",
        "Description": "Start your workout with burpees to elevate your heart rate and engage multiple muscle groups. Burpees are an efficient full-body exercise that improves cardiovascular fitness and boosts metabolism.",
        "Image_URL": "https://i.ibb.co/C73CrMY/Burpees.jpg"
      },
      "Exercise 2": {
        "Name": "Arm Circles",
        "Description": "Follow up with arm circles to increase shoulder mobility and flexibility. Arm circles also help in loosening up the shoulder joints, reducing the risk of injury during strength training exercises.",
        "Image_URL": "https://i.ibb.co/WD07QBF/arm-circles.jpg"
      }
    },
    "Strength_Exercises": {
      "Exercise 1": {
        "Name": "Romanian Deadlifts",
        "Description": "Incorporate Romanian deadlifts to target your hamstrings, glutes, and lower back muscles. Romanian deadlifts are effective for strengthening the posterior chain and improving hip hinge mechanics.",
        "Image_URL": "https://i.ibb.co/4MCH0hY/Romanian-Deadlifts.webp"
      },
      "Exercise 2": {
        "Name": "Dumbbell Bench Press",
        "Description": "Include dumbbell bench press to develop chest, shoulder, and triceps strength. Dumbbell bench press offers a greater range of motion compared to barbell bench press, enhancing muscle activation and stability.",
        "Image_URL": "https://i.ibb.co/RbJwpvn/Dumbbell-Bench-Press.webp"
      },
      "Exercise 3": {
        "Name": "Pull-Ups",
        "Description": "Integrate pull-ups into your routine to strengthen your back, biceps, and grip. Pull-ups are a challenging bodyweight exercise that enhance upper body muscle definition and improve overall pulling strength.",
        "Image_URL": "https://i.ibb.co/8cG66R9/Pull-Ups.jpg"
      },
      "Exercise 4": {
        "Name": "Overhead Press",
        "Description": "Incorporate overhead press to build shoulder strength and stability. Overhead press targets the deltoids, triceps, and upper back muscles, contributing to balanced upper body development.",
        "Image_URL": "https://i.ibb.co/Ypz1R22/Overhead-Press.jpg"
      }
    },
    "Stretching": {
      "Exercise 1": {
        "Name": "Quad Stretch",
        "Description": "Finish your workout with a quad stretch to release tension in your quadriceps muscles. Quad stretches help in improving flexibility and preventing muscle imbalances.",
        "Image_URL": "https://i.ibb.co/4K09n27/Quad-Stretch.jpg"
      },
      "Exercise 2": {
        "Name": "Triceps Stretch",
        "Description": "Conclude your session with a triceps stretch to alleviate tightness in the back of your arms. Triceps stretches help in improving range of motion and reducing the risk of injury.",
        "Image_URL": "https://i.ibb.co/yyhprW7/Triceps-Stretch.jpg"
      }
    }
  }
}
suitable between the name of the exercise to the image, base on this list and on the example above (in the Image_URL): https://i.ibb.co/NmTWd8s/Bulgarian-Split-Squats.webp
    https://i.ibb.co/4V5FPqZ/Face-Pulls.jpg
    https://i.ibb.co/YdKKKmy/Bench-Press.jpg
    https://i.ibb.co/d6BXzrk/High-knees.webp
    https://i.ibb.co/YDJ9BRG/Jumping-jacks.jpg
    https://i.ibb.co/WD07QBF/arm-circles.jpg
    https://i.ibb.co/mbynZw7/Wall-sit.jpg
    https://i.ibb.co/z5KLmFx/Goblet-Squats.webp
    https://i.ibb.co/zGcGSWN/Sumo-Squats.jpg
    https://i.ibb.co/NFzwW0b/Leg-Extension-Machine.webp
    https://i.ibb.co/jZkgnHx/Leg-Curl-Machine.webp
    https://i.ibb.co/tmyFCWB/Box-Jumps.jpg
    https://i.ibb.co/qB5WrvT/Glute-Bridges.jpg
    https://i.ibb.co/YB3Yr4H/Step-Ups.jpg
    https://i.ibb.co/L5KTL6r/Hiptrust.webp
    https://i.ibb.co/L8Mnd4H/Leg-Press.png
    https://i.ibb.co/QY76D23/Calf-Raises.jpg
    https://i.ibb.co/4MCH0hY/Romanian-Deadlifts.webp
    https://i.ibb.co/yRmZc2P/Lunges.jpg
    https://i.ibb.co/ygw8qxd/Deadlifts.jpg
    https://i.ibb.co/vvGK5w1/Squat.jpg
    https://i.ibb.co/MP7gL48/Superman.webp
    https://i.ibb.co/qrh2DNz/Crunches.jpg
    https://i.ibb.co/tXN4pgF/Leg-Raises.jpg
    https://i.ibb.co/V2zwzdK/Bicycle-Crunches.jpg
    https://i.ibb.co/qxYm52k/Russian-Twists.jpg
    https://i.ibb.co/0qJ1WN5/Plank.jpg
    https://i.ibb.co/Zm5RGMW/Incline-Bench-Press.webp
    https://i.ibb.co/bRQ5Fwm/Chest-Flyes.webp
    https://i.ibb.co/R2tcgPx/Barbell-squats.jpg
    https://i.ibb.co/n67Vpch/Chin-Ups.jpg
    . 
    dont show an image with unmatching name for the exercise. for exmaple dont show the : 
    https://i.ibb.co/0qJ1WN5/Plank.jpg for deadlifts.. or https://i.ibb.co/YDJ9BRG/Jumping-jacks.jpg for Dumbbell Bench Press.
    check twice or more your suitable image for the name of the exercise!
    show only the matching image by its name of the link!
    
    if you dont find any suitable image show the default: https://i.ibb.co/f22FSXQ/My-Personal-Trainer-Logo.png"""

        # jpg_text += ""        
        # gpt_prompt += jpg_text
        gpt_prompt += json_example
        #print("prompt is : " + gpt_prompt)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-proj-t6V4z2BCXGS9i2e2A7jaT3BlbkFJVOUCg85KM8LZQ1tLQQfL"  # Replace YOUR_API_KEY with your actual API key
        }
        
        # Prepare the data to send
        payload = {
            "model": "gpt-4-turbo",  # Model name
            "response_format": {"type": "json_object"},
            "messages": [
          {
            "role": "system",
            "content": "You are a helpful assistant. Your response should be in JSON format."
          },
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": gpt_prompt
              },
            ]
          }
        ] 
            #"max_tokens": 1000              # Max tokens to generate
        }
        #request_body = {
        #    "model": "gpt-3.5-turbo",
        #    "messages": [
        #        {"role": "system", "content": "You are a helpful assistant."},
        #        {"role": "user", "content": gpt_prompt}
        #    ]
        #}

        try:
            # response = request.post(
            #     self.api_url,
            #     headers=headers,
            #     data=json.dumps(payload)#request_body)
            # )
            # Convert payload to JSON
            json_payload = json.dumps(payload)
            
            # Send POST request to the API
            conn = http.client.HTTPSConnection("api.openai.com")
            conn.request("POST", "/v1/chat/completions", json_payload, headers)
            
            # Get response
            response = conn.getresponse()

            # Read response data
            data = response.read().decode("utf-8")
            
            # Print response data for debugging
            print("Response:", data)
            
            # Convert response JSON to dictionary
            response_data = json.loads(data)
            
            # Check if 'choices' key exists in response
            if 'choices' in response_data:
                # Return the generated text
                print ("GPT Response : " , response_data['choices'][0]['message']['content'])
                return response_data['choices'][0]['message']['content']
            else:
                print("Unexpected response format:", response_data)
                return None

            #if response.status_code == 200:
            #    response_data = response.json()
            #    return response_data['choices'][0]['message']['content']
            #else:
            #    raise Exception('Failed to fetch GPT response')

        except Exception as e:
            print(f'Error during API request: {e}')
            raise Exception('Failed to fetch GPT response')


@app.route('/delete_workout', methods=['POST'])
def delete_workout():
    try:
        print("Starting delete workout")
        data = request.get_json()
        print('Data:', data)

        uid = data.get("insertedOnlyObjectId")
        print('UId:', uid)

        if not uid:
            response_data = {"success": False, "error": "Missing insertedOnlyObjectId"}
            return jsonify(response_data), 400

        #collection = Mongo.connect_to_mongo()
        success = Mongo.delete_workout_by_uid(collectionUsers, uid)

        if success:
            response_data = {"success": True, "message": "Workout plan deleted successfully"}
            return jsonify(response_data), 200
        else:
            response_data = {"success": False, "error": "No Workout Plan found or deletion failed."}
            return jsonify(response_data), 404

    except Exception as e:
        print(f"Exception in delete_workout: {e}")
        traceback.print_exc()
        response_data = {"success": False, "error": str(e)}
        return jsonify(response_data), 400


@app.route('/check_server', methods=['POST'])        
def check_server():
        if request.method == 'POST':
            try:
                print("Starting End Point")
               
                return jsonify("Hello from server")

            except Exception as e:
                return jsonify(error=str(e)), 400
        else:
            return jsonify(error='Invalid method'), 405

# @app.route('/create_workout', methods=['POST'])    

@app.route('/do_login', methods=['POST'])        
def do_login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            

            if not username or not password:
                return jsonify(success=False, response="Username and password are required."), 400

            #collection = Mongo.connect_to_mongo()
            user_doc = collectionUsers.find_one({"username": username})

            if user_doc:
                # Decrypt the stored password for comparison
                stored_password = user_doc["password"] 
                # After retrieving the stored encrypted password and key from the database
                
                decrypted_password = fernet.decrypt(stored_password).decode()
                if decrypted_password == password:
                    print("login: _id=", user_doc["_id"])
                    
                # if user_doc["password"] == password:
                #     print("login: _id=", user_doc["_id"])
                    
                    return jsonify(success=True, _id=str(user_doc["_id"]), name=str(user_doc["name"])), 200
                else:
                    return jsonify(success=False, response="Login unsuccessful. Incorrect password."), 401
            else:
                return jsonify(success=False, response="Login unsuccessful. User not found."), 401

        except Exception as e:
            return jsonify(success=False, error=str(e)), 400
    else:
        return jsonify(success=False, error='Invalid method'), 405

@app.route('/show_workout', methods=['POST'])        
def show_workout():
    if request.method == 'POST':
        try:
            print("Starting show_workout")
            data = request.get_json()
            print('User Id :', data)
            print(data)
            
            # Retrieve the document by _id using the Mongo class
            #collection = Mongo.connect_to_mongo()
            userDoc = Mongo.get_workout_by_uid(collectionUsers, data.get("insertedOnlyObjectId"))
            
            if userDoc:
                #workoutplan = str(userDoc["workout_plan"])
                # Construct a dictionary for the response
                
                #response_data = {"workoutplan": workoutplan} 
                response_data = userDoc["workout_plan"]
                # Convert the response_data to JSON format and return
                return jsonify(response_data)
            else:
                response_data = { "error": "No Workout Plan found."} # type: ignore
                return jsonify(response_data), 401

        except Exception as e:
            response_data = {"success": False, "error": str(e)}
            return jsonify(response_data), 400
    else:
        response_data = {"success": False, "error": "Invalid method"}
        return jsonify(response_data), 405


@app.route('/do_register', methods=['POST'])        
def do_register():
    if request.method == 'POST':
        try:
            print("Starting register")
            data = request.get_json()
            print('User details for register:', data)
            # Encrypt the password before storing it
            #data['password'] = encrypt_password(data['password'])
            
            print ("Starting Register User to DB...")
        
            # Check if the user already exists
            query = {"username": data.get("username")}
            print("query:", query)

            existing_user = collectionUsers.find_one(query)
            print("existing user:", existing_user)

            if existing_user:
                responseExistingUser="Registration unsuccessful. User already exists."
                print("Response Existing User:", responseExistingUser)
                return jsonify(responseExistingUser), 401


            # Insert the new user into the MongoDB collection

            print("Data from Client : " , str(data))
            data['password'] = fernet.encrypt(data['password'].encode())
            print('encryption key :', str(key))
            print("Data after encryption : " , str(data))
            result = collectionUsers.insert_one(data)
            
            print ("insert result id:" , str(result.inserted_id))


            return jsonify(success=True, _id=str(result.inserted_id)), 200
        

        except Exception as e:
          print ("error in server is :", str(e))
          return jsonify(success=False, error=str(e)), 400
    else:
        return jsonify(success=False,error='Invalid method'), 405

@app.route('/create_workout', methods=['POST'])    

def create_workout():
        #if request.method == 'POST':
            try:
                               
                print("Starting Create Workout")
                data = request.get_json()
                print('User Parameters:', data)
                print(data)
                open_ai_server = OpenAiServer()
                workout_plan = open_ai_server.ask_gpt_about_workout_plan(data["gender"],data["age"],data["height"],data["weight"],data["training_frequency"],data["fitness_level"])

                print ('workout plan : ' + workout_plan)
                
              
                print ("Mongo connected in create_workout")
                response, status_code = Mongo.create_workout(collectionUsers, data["insertedOnlyObjectId"],workout_plan)
                
                print("response: ", response )
                print("status_code: ", status_code )
                
                return response, status_code

            except Exception as e:
                print(f"Exception during create workout: {e}")
                return jsonify(error=str(e)), 400


class Mongo:
    #def connect_to_mongo():
    #    mongo_uri = "mongodb+srv://yaelbar:q1w2e3r4t5@mpt-cluster.riqpsu9.mongodb.net/?retryWrites=true&w=majority&appName=MPTCluster"
    #    client = MongoClient(mongo_uri)
    #    db = client.get_database('MPTDB')
    #    collection = db['users']
    #    return collection
    
    def retrieve_documentId_by_username(collection, username):
        # Retrieve the document based on the username parameter
        if username:
            query = {"username": username}
            document = collection.find_one(query)
            print ("retrieve_documentId_by_username query : " + query)
            if document:
                print("Document found:")
                print(document)
                return document["_id"]
            else:
                print(f"No document found for username: {username}")
                return None
        else:
            print("Invalid username provided.")
            return None

    def retrieve_full_document_by_username(collection, username):
        # Retrieve the document based on the username parameter
        print ("Username is :" + username)
        #if username:
        query = {"username": + str(username)}
        print ("query is:" + query)
        document = collection.find_one(query)
        print ("retrieve_full_document_by_username query : " + query)
        if document:
            print("Document found:")
            print(document)
            return document
        else:
            print(f"No document found for username: {username}")
            return None
        # else:
        #     print("Invalid username provided.")
        #     return None
        
    def get_workout_by_uid(collection, uid):
        # Retrieve the document based on the username parameter
        if uid:
            # Convert the string _id to ObjectId
            object_id = ObjectId(uid)
            
            query = {"_id": object_id}
            print ("query inside get_workout_by_uid : " , str(query))
            document = collection.find_one(query)

            if document:
                print("Document found:")
                print(document)
                return document
            else:
                print(f"No document found for uid: {uid}")
                return None
        else:
            print("Invalid uid provided.")
            return None

    def delete_workout_by_uid(collection, uid):
        try:
            object_id = ObjectId(uid)
            print('ObjectId:', object_id)
            existing_workout = collection.find_one({"_id": object_id})
            print('Existing workout:', existing_workout)
            if existing_workout:
                result = collection.update_one({"_id": object_id}, {"$unset": {"workout_plan": ""}})
                return result.modified_count > 0
            else:
                return False
        except Exception as e:
            print(f"Error in delete_workout_by_uid: {e}")
            traceback.print_exc()
            return False


    def create_workout(collection, uid , workoutPlan):
        print ("Starting Create Workout...")
        #query = {"username":"yaelbar","password":"12345","name":"Yael Bar","phoneNumber":"0556669708"}
        
        # Check if the user already exists
        query = {"_id": ObjectId(uid)}
        print("query:", query)

        existing_user = collection.find_one(query)
        print("existing user:", existing_user)

        if existing_user:
            existing_user["workout_plan"] = workoutPlan

        try:
            # Define the update query
            update_query = {"$set": existing_user}
            print("update_query:", update_query)

            # Use update_one to update the document
            result = collection.update_one(query, update_query)

            if result.modified_count > 0:
                print(f"Document with _id {uid} updated successfully.")
                return jsonify(workoutPlan), 200
            else:
                print(f"No document found with _id {uid}.")
                return jsonify("Update Workoutplan failed"), 400

        except Exception as e:
            print(f"Error updating document: {e}")
            # Print the ObjectId
            print(f"Inserted ObjectId: {uid}")
        
    

def get_exercise_details_locally(exercise_name):
    # Here you can implement logic to fetch exercise details from your local data
    # For example, you can parse the text provided in your code snippet
    # to get the details based on the exercise name
    # You can also retrieve images and other details from your data source
    # This function should return exercise details in a format suitable for your frontend
    # For simplicity, let's just return a dummy exercise detail for now

    # Assume exercise details are stored in a dictionary
    exercise_details = {
        'name': exercise_name,
        'description': 'This is a sample exercise description for ' + exercise_name,
        'image_url': 'https://i.ibb.co/s1QSPcr/nisui-logo.jpg'  # You should replace this with the actual image URL
    }
    return exercise_details

server = OpenAiServer()


####################My Personal Trainer ########################


if __name__ == '__main__':
   app.run()
