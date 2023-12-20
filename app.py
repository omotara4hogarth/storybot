from flask import Flask, render_template, request
from bot import ask_question, get_images
import ast

app = Flask(__name__)

# Run with this command: flask --app app.py --debug run


@app.route("/")
def hello():
    answer = ""
    images = []
    font = "Rubik"
    return render_template("index.html", bot_response=answer, font=font, images=images)


@app.route("/", methods=["POST"])
def index_post():
    plot = request.form["question"]
    query = f"Create a riveting, highly creative story based on the following plotline, and suggest 10 songs to make up its soundtrack (particularly aiming to include songs that capture the specific setting of the story, the language/s used therein, demographic, culture and the key themes of the plot. Try to include songs by artists from the specific setting and time of the story), a colour to reflect the mood of the tale, a font and art style to capture its essence, a famous past artwork in that style as an example, a text colour to contrast against the colour and a title for the story. The names, traits, personalities and other characteristics of your characters should be make sense in the context of the other elements of the plot (such as the theme, location etc.). Ensure that the songs you choose are indeed real songs that can be streamed on popular platforms such as Spotify, YouTube and Apple Music. Note that the colour, font and text colour will be used on a website, so consider the web-aesthetic as well as the plot in your choices. Plot: {plot}"
    response = ask_question(query)
    answer = response[0]
    playlist = response[1]
    print(f"The playlist is: {playlist}")
    answer_list = ast.literal_eval(answer)
    plot = answer_list["plot"]
    colour = answer_list["colour"]
    font = answer_list["font"]
    text_colour = answer_list["text_colour"]
    art_style = answer_list["art_style"]
    example_artwork = answer_list["example_artwork"]
    images = get_images(plot, art_style)
    plot_and_image = {}
    i = 0
    for page in plot:
        plot_img_dict = {"plot": page, "image": images[i]}
        i += 1
        plot_and_image[f"page{i}"] = plot_img_dict
    return render_template(
        "index.html",
        bot_response=plot,
        colour=colour,
        font=font,
        text_colour=text_colour,
        art_style=art_style,
        images=images,
        plot_and_image=plot_and_image,
        playlist=playlist,
    )


@app.route("/hey")
def hey():
    return "Heyyy!"
