# **AI text-extraction bot Recc**

### YouTube transcript
The application initiates with the input of a YouTube URL. Upon entering a YouTube video link, the backend server retrieves the video's transcript via the YouTube API. This transcript is then processed by an NLP model that produces a JSON-formatted response containing information relevant to predefined keywords such as 'media' and 'place.'
To achieve this functionality, it was necessary to fine-tune a Large Language Model (LLM). Following this, the SERP (Search Engine Results Page) and Google Custom Search API are utilized to validate the language model's output. These tools assist in obtaining the launch links and related images.
Consequently, users can access essential data and information from the videos without the need to watch them in their entirety.
This response is called as Recc.

### SMS texting bot
We use the Twilio API to get the same result of YouTube transcript.
So if we send the message to Twilio phone number, bot replies the Recc response.

### Voice Chatbot
Voice Chatbot is the extension of YouTube transcript bot.
If the customer records his speech, the chatbot analyzes this and generates the result using the same templates of YouTube bot.

## install
```
python main.py
```
