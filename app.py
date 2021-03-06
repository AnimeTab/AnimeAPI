from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import sqlite3
import create_table
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import keyring

app = Flask(__name__)
api = Api(app)
CORS(app)

class AnimeList(Resource):

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM anime"
        result = cursor.execute(query)
        animes = []
        for row in result:
            animes.append({'anime':row[0],'quote':row[1], 'author':row[2], 'color': row[3], 'logo': row[4], 'email': row[5]})
        logging.basicConfig(filename = "logger.log", format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info('Getting Anime Quotes')
        connection.close()

        return {'animes': animes}


class Anime(Resource):

    @classmethod
    def find_quote(cls, quote):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM anime WHERE quote = ?"
        quote.lower()
        quote.replace(" ","")
        result = cursor.execute(query,(quote,))
        row = result.fetchone()
        if row:
            return {'anime':row[0], 'quote': row[1], 'author': row[2], 'color': row[3], 'logo': row[4], 'email': row[5]}
        return None
    
    def post(self, quote):
        if Anime.find_quote(quote):
            return {'message': "This quote already exsits!"}
        parser = reqparse.RequestParser()
        
        parser.add_argument('anime',
        type = str,
        required = True,
        help = "Dont leave blank"
        )

        parser.add_argument('author',
        type = str,
        required = True,
        help = "Don't leave blank"
        )

        parser.add_argument('color',
        type = str,
        required = True,
        help = "Don't leave blank"
        )

        parser.add_argument('logo',
        type = str,
        required = True,
        help = "Don't leave blank"
        )

        parser.add_argument('email',
        type = str,
        required = True,
        help = "Don't leave blank"
        )

        data = parser.parse_args()
        anime = {
            'anime': data['anime'].lower().replace(" ", ""),
            'quote': quote,
            'author': data['author'],
            'color' : data['color'],
            'logo': data['logo'],
            'email': data['email']
        }
        
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO temp VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query,(anime['anime'], anime['quote'], anime['author'], anime['color'], anime['logo'], anime['email']))

        connection.commit()
        connection.close()

        return anime, 201

    def put(self, quote):
        if Anime.find_quote(quote):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "DELETE FROM temp WHERE quote = ?"
            quote.lower()
            quote.replace(" ", "")
            cursor.execute(query,(quote,))
            connection.commit()
            connection.close()
            return {'message': "This quote already exsits!"}
        else:
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "INSERT INTO anime VALUES (?, ?, ?, ?, ?, ?)"
            parser = reqparse.RequestParser()

            parser.add_argument('anime',
            type = str,
            required = True,
            help = "Can't be blank!"
            )

            parser.add_argument('author',
            type = str,
            required = True,
            help = "Can't be blank!"
            )

            parser.add_argument('color',
            type = str,
            required = True,
            help = "Don't leave blank"
            )

            parser.add_argument('logo',
            type = str,
            required = True,
            help = "Don't leave blank"
            )

            parser.add_argument('email',
            type = str,
            required = True,
            help = "Don't leave blank"
            )
            
            data = parser.parse_args()
            
            anime = {
                'anime': data['anime'],
                'quote': quote,
                'author': data['author'],
                'color' : data['color'],
                'logo': data['logo'],
                'email': data['email']
            }    

            cursor.execute(query,(data['anime'], quote, data['author'], anime['color'], anime['logo'], anime['email']))
            cursor.execute("DELETE FROM temp WHERE quote = ?",(quote,))
            connection.commit()
            connection.close()

            sender = "animetab.xyz@gmail.com"
            receiver = anime['email']
            password = keyring.get_password('app','animetab')    
            message = MIMEMultipart()
            message["Subject"] = "Quote Accepted!"
            message["From"] = sender
            message["To"] = receiver
            
            text = """\
               Congrats!
               Your quote has been submitted!
               """
            part1 = MIMEText(text, "plain")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender, password)
                server.sendmail(
                    sender, receiver, message.as_string()
                )
            return anime


class TempList(Resource):
    @classmethod
    def find_quote(cls, quote):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM temp WHERE quote = ?"
        result = cursor.execute(query,(quote,))
        row = result.fetchone()
        if row:
            return {'anime':row[0], 'quote': row[1], 'author': row[2], 'color': row[3], 'logo': row[4], 'email': row[5]}
        return None

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM temp"
        result = cursor.execute(query)
        animes = []
        for row in result:
            animes.append({'anime':row[0],'quote':row[1], 'author':row[2], 'color': row[3], 'logo': row[4], 'email': row[5]})
        connection.close()

        return {'animes': animes}

    def delete(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "DELETE FROM temp"
        result = cursor.execute(query)
        connection.commit()
        connection.close()
        return {'message': "Deleted!"}


class Temp(Resource):
    @classmethod
    def find_quote(cls, quote):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM temp WHERE quote = ?"
        result = cursor.execute(query,(quote,))
        row = result.fetchone()
        if row:
            return {'anime':row[0], 'quote': row[1], 'author': row[2], 'color': row[3], 'logo': row[4], 'email': row[5]}
        return None

    def delete(self, quote):
        if Temp.find_quote(quote):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "DELETE FROM temp WHERE quote = ?"
            cursor.execute(query,(quote,))
            connection.commit()
            connection.close()
            return {'message': "{} has been deleted!".format(quote)}
        else:
            return {'message': "No such quote exits!"}


api.add_resource(AnimeList, '/quotes')
api.add_resource(Anime, '/quote/<string:quote>')
api.add_resource(TempList, '/temp')
api.add_resource(Temp,'/temp/<string:quote>')

if __name__ == "__main__":
    app.run()
