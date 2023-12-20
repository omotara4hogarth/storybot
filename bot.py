from openai import AzureOpenAI
import json, os, requests, time, ast, spotipy, webbrowser, urllib.request, random, openai
import spotipy.util as util

story_length_words = 2000
volume_soundtrack = 25

openai_safety_guidelines = "Illegal activity OpenAI prohibits the use of our models, tools, and services for illegal activity. Child Sexual Abuse Material or any content that exploits or harms children We report CSAM to the National Center for Missing and Exploited Children. Generation of hateful, harassing, or violent content Content that expresses, incites, or promotes hate based on identity Content that intends to harass, threaten, or bully an individual Content that promotes or glorifies violence or celebrates the suffering or humiliation of others Generation of malware Content that attempts to generate code that is designed to disrupt, damage, or gain unauthorized access to a computer system. Activity that has high risk of physical harm, including: Weapons development Military and warfare Management or operation of critical infrastructure in energy, transportation, and water Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders Activity that has high risk of economic harm, including: Multi-level marketing Gambling Payday lending Automated determinations of eligibility for credit, employment, educational institutions, or public assistance services Fraudulent or deceptive activity, including: Scams Coordinated inauthentic behavior Plagiarism Academic dishonesty Astroturfing, such as fake grassroots support or fake review generation Disinformation Spam Pseudo-pharmaceuticals Adult content, adult industries, and dating apps, including: Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness) Erotic chat Pornography Political campaigning or lobbying, by: Generating high volumes of campaign materials Generating campaign materials personalized to or targeted at specific demographics Building conversational or interactive systems such as chatbots that provide information about campaigns or engage in political advocacy or lobbying Building products for political campaigning or lobbying purposes Activity that violates people’s privacy, including: Tracking or monitoring an individual without their consent Facial recognition of private individuals Classifying individuals based on protected characteristics Using biometrics for identification or assessment Unlawful collection or disclosure of personal identifiable information or educational, financial, or other protected records Engaging in the unauthorized practice of law, or offering tailored legal advice without a qualified person reviewing the information OpenAI’s models are not fine-tuned to provide legal advice. You should not rely on our models as a sole source of legal advice. Offering tailored financial advice without a qualified person reviewing the information OpenAI’s models are not fine-tuned to provide financial advice. You should not rely on our models as a sole source of financial advice. Telling someone that they have or do not have a certain health condition, or providing instructions on how to cure or treat a health condition OpenAI’s models are not fine-tuned to provide medical information. You should never use our models to provide diagnostic or treatment services for serious medical conditions. OpenAI’s platforms should not be used to triage or manage life-threatening issues that need immediate attention. High risk government decision-making, including: Law enforcement and criminal justice Migration and asylum"

plot_gen_role = [
    {
        "role": "system",
        "content": "Respond only with a dictionary with keys corresponding to the plot, soundtrack, colour, font, art_style, example_artwork, text_colour and title. The 'plot' key should have its value given as a list of strings, with every 1-2 sentences of the plot making up a string.  There can be multiple sentences in each string. The total word count of all of the strings combined should be at least {story_length_words} words. The 'soundtrack' key should have its value given as a list of dictionaries with keys 'name' and 'artist', corresponding to each song's name and artist. The 'colour' key should have its value given as a string where the colour is given as a HEX code. The 'font' key should have its value given as a string where the font is given as a string. The 'art_style' key should have its value given as a string. The 'example_artwork' key should have its value given as a string. The 'text_colour' key should have its value given as a string where the colour is given as a HEX code. The 'text_colour' should be both complimentary to, and readable when placed against the 'colour'; in other words, dark 'colour' values should be paired with light 'text_colour' values, and vice versa. The 'title' key should have its value given as a string. Be careful to format your response correctly, as it will be used in a Python script. Use double quotes for your strings. Review the dictionary for any errors that would make it unusable, or cause an error in Python.",
    }
]

prompt_gen_role = [
    {
        "role": "system",
        # "content": "Generate creative and diverse images using Dall-E while ensuring that the content is respectful, non-offensive, and adheres to privacy and safety guidelines.",
        "content": "Generate a detailed, creative image using Dall-E, respecting the limit of 4 images per request. Avoid any depictions of politicians, public figures, or specific artists' styles from the last 100 years. Make sure to specify the type of image (e.g., photo, painting, illustration) and ensure diversity in any human depictions. Do not reference any specific people or celebrities. The description of the image should be concrete, objective, and detailed, with a length of more than three sentences",
        # "content": f"Review the DALL-E prompt for anything that might violate the rules given below, and modify it so it can avoid a content violation whilst generating the same image. Remove any personal names of characters, referring to them by their characteristics instead. Return the modified prompt only as a Python string, do not make any additional comments. Rules: {openai_safety_guidelines}",
    }
]


def ask_question(question):
    print("!!!!!!!!! NOW: Asking GPT for the plot !!!!!!!!!")
    client = AzureOpenAI(
        api_key=os.getenv("AZ_KEY"),
        azure_endpoint=os.getenv("AZ_ENDPOINT"),
        api_version="2023-12-01-preview",
    )

    messages = [{"role": "user", "content": question}]
    messages.extend(plot_gen_role)

    response = client.chat.completions.create(model="GPT-4", messages=messages)

    answer = response.choices[0].message.content
    # answer = debug(answer)
    print(answer)
    playlist = create_playlist(
        ast.literal_eval(answer)["title"], ast.literal_eval(answer)["soundtrack"]
    )

    result = [answer, playlist]
    return result


def debug(dictionary):
    print("!!!!!!!!! NOW: Debugging the dictionary !!!!!!!!!")
    client = AzureOpenAI(
        api_key=os.getenv("AZ_KEY"),
        azure_endpoint=os.getenv("AZ_ENDPOINT"),
        api_version="2023-12-01-preview",
    )

    messages = [
        {
            "role": "user",
            "content": f"Review the following dictionary for any errors that would make it unusable, or cause an error in Python. Return the modified dictionary only, do not make any comment. If the given dictionary is correct, return it as is. Dictionary: {dictionary}",
        }
    ]

    response = client.chat.completions.create(model="GPT-4", messages=messages)

    answer = response.choices[0].message.content
    dictionary = answer
    return dictionary


def summarise(page, plot_list):
    print("!!!!!!!!! NOW: Summarising a page for DALL-E !!!!!!!!!")
    client = AzureOpenAI(
        api_key=os.getenv("AZ_KEY"),
        azure_endpoint=os.getenv("AZ_ENDPOINT"),
        api_version="2023-12-01-preview",
    )

    query = f"Summarise the key scene described in the following page from a short story into a brief 1 sentence prompt for Open AI's DALL-E image generator tool. Use descriptive language and keep it simple. Provide an image description, and details of the lighting and field of view. Imagine that DALL-E has not been passed any other part of the book and will not read any of your previous or future prompts - so include any relevant context from the rest of the story in your prompt to ensure DALL-E can create an image that is consistent with the overall story.  Based on the plot, describe the appearance of the characters in detail, in such a way that the DALL-E is able to maintain consistency in their depiction across all pages.  Do not incorporate any information from future pages, so as not to reveal any unknown information to the illustrator and readers. Do not use any words that could violate OpenAI's usage policies or safety guidelines - if needed, rephrase your prompt to avoid violating this policy. The full story is given below as a list of pages. Find your given page within the full story, and use only the pages that come before it to contextualise your prompt. Page: {page}. Full story: {plot_list}"
    messages = [{"role": "user", "content": query}]
    prompt_gen_role.extend(messages)
    print(messages)

    response = client.chat.completions.create(model="GPT-4", messages=prompt_gen_role)

    answer = response.choices[0].message.content
    return answer


def review_for_violations(string):
    query = f"Review the following DALL-E prompt for anything that might violate the OpenAI content rules, or that might trigger the content-filtering system, and modify it so it can avoid a content violation whilst generating the same image. Remove any personal names of characters, referring to them by their characteristics instead. Return the modified prompt only as a Python string, do not make any additional comments. Prompt: {string}"
    client = AzureOpenAI(
        api_key=os.getenv("AZ_KEY"),
        azure_endpoint=os.getenv("AZ_ENDPOINT"),
        api_version="2023-12-01-preview",
    )

    messages = [{"role": "system", "content": query}]

    response = client.chat.completions.create(model="GPT-4", messages=messages)

    answer = response.choices[0].message.content
    return answer


def get_images(plot_list, art_style):
    print("!!!!!!!!! NOW: Getting the illustrations from DALL-E !!!!!!!!!")
    # api_version = "2022-08-03-preview"
    # api_key = os.getenv("AZURE_OPENAI_KEY")
    # azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AzureOpenAI(
        api_key=os.getenv("SAT_AZ_KEY"),
        azure_endpoint=os.getenv("SAT_AZ_ENDPOINT"),
        api_version="2023-12-01-preview",
    )

    # url = "{}dalle/text-to-image?api-version={}".format(azure_endpoint, api_version)
    # headers = {"api-key": api_key, "Content-Type": "application/json"}

    img_urls = []

    for string in plot_list:
        summary = summarise(string, plot_list).replace('"', "").replace("'", "")
        prompt = f"A vivid, immersive artwork depicting a scene, in the {art_style} art style. {summary}"
        print(prompt)
        response = client.images.generate(
            prompt=prompt,
            size="1024x1024",
            style="natural",
            quality="hd",
            model="dalle3",
            # model="dalle2",
        )
        json_response = json.loads(response.model_dump_json())
        image_url = json_response["data"][0]["url"]
        img_urls.append(image_url)
        print(img_urls)
        # Generate an image summary through GPT for alt text
    return img_urls


def create_playlist(title, soundtrack):
    print("!!!!!!!!! NOW: Creating the playlist !!!!!!!!!")
    credentials = "spotipy_keys.json"
    with open(credentials, "r") as keys:
        json_creds = json.load(keys)
    client_id = json_creds["client_id"]
    client_secret = json_creds["client_secret"]
    redirect_uri = json_creds["redirect"]
    username = json_creds["username"]
    scope = "user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public"
    auth = util.prompt_for_user_token(
        username, scope, client_id, client_secret, redirect_uri
    )
    sp = spotipy.Spotify(auth=auth)
    soundtrack_list = []
    for song in soundtrack:
        track_results = sp.search(
            q=f"artist:{song['artist']} track:{song['name']}", type="track", limit=1
        )
        track = track_results["tracks"]["items"]
        if track != None and len(track) != 0:
            uri = track[0]["uri"]
            soundtrack_list.append(uri)
    print(soundtrack_list)
    my_playlist = sp.user_playlist_create(
        user=username, name=f"Storybot: {title} Soundtrack", public=True
    )
    sp.user_playlist_add_tracks(username, my_playlist["id"], soundtrack_list)
    playlist_link = my_playlist["external_urls"]["spotify"]
    webbrowser.open(my_playlist["external_urls"]["spotify"])

    first_part_key_link = playlist_link.replace(
        "https://open.spotify.com/playlist/", ""
    )
    separator = "?"
    key_link = first_part_key_link.split(separator, 1)[0]

    embed_link = (
        f"https://open.spotify.com/embed/playlist/{key_link}?utm_source=generator"
    )
    print(embed_link)
    return embed_link


dict = {
    "plot": [
        "In Osaka, Japan, the year is 1999. The air is tense in the beautiful, antique-laden house of the Fujimura family. In the family’s simple, modest tatami room, an unseen brutality occurs: Shigenori Fujimura is found dead by his wife, Yumiko Fujimura. Just outside the room, their blind son, Yuuki, barely eighteen with a heart full of dreams, had been listening to a ghastly, painful struggle.",
        "Despite missing his sight, Yuuki has an acute sense of hearing, heightened over the years as nature's form of compensation. He can distinguish his mother’s voice from his father’s, recognise their footsteps, their laughter and their silent tears that the world never sees. On the night of his father's death, he'd heard the chilling sounds, an argument, a struggle. So, when the police arrive, he remains eerily silent - not sure if what he heard was his mother committing an act of atrocious violence.",
        "The core theme of the tale is the moral dilemma faced by Yuuki. Like an intricate Japanese floral arrangement, it's a blooming puzzle with delicate layers. It questions how far one could go to protect their family, and whether it's morally correct to not act when you know a loved one crossed a line. The story spans over months of grilling investigations, rumours, leaks to the press, and an intense trial. As the threads unravel, Yuuki's tumultuous battle with his morals and the wish to protect his mother take centre stage.",
        "Finally, he takes a stand and speaks: a twist so unexpected, it overturns every suspicion and every laid-out evidence. His mother walks free, with all charges dropped – but at the cost of Yuuki's freedom and peace. He sacrifices his own future to protect her, bearing the cross of his mother’s alleged sin. A twisted tale of protection, sacrifice and a blind son’s love.",
    ],
    "soundtrack": [
        {"name": "Gyakujō", "artist": "L'Arc~en~Ciel"},
        {"name": "Flower", "artist": "L'Arc~en~Ciel"},
        {"name": "Kaze no Yukue", "artist": "L'Arc~en~Ciel"},
        {"name": "Kagayaku Sora no Shijima ni wa", "artist": "Kalafina"},
        {"name": "Neko", "artist": "DISH//"},
        {"name": "Sashinobete", "artist": "Yuki Tsujimura"},
        {"name": "Hoshiai", "artist": "Yuki Tsujimura"},
        {"name": "Gone", "artist": "Yuna"},
        {"name": "Silent Majority", "artist": "Keyakizaka46"},
        {"name": "Forbidden Colors", "artist": "Ryuichi Sakamoto & David Sylvian"},
    ],
    "colour": "#83afea",
    "font": "MS Mincho",
    "art_style": "Ukiyo-e style",
    "text_colour": "#000000",
    "title": "Echos in the Silent Room",
}

# create_playlist(dict["title"], dict["soundtrack"])
get_images(dict["plot"], dict["art_style"])
