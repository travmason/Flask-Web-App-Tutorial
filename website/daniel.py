import openai
import os
from time import time,sleep
import re
import logging

logging.basicConfig(level=logging.INFO)

class Bot:

    author = ''
    conversation_text = list()

    def open_file(self, filename):
        document = os.getcwd()+'\\'+filename
        logging.info(document)
        with open(document, 'r', encoding='utf-8') as infile:
            return infile.read()

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def gpt3_completion(self, prompt, engine='text-davinci-002', temp=0.9, top_p=1.0, tokens=400, freq_pen=1.5, pres_pen=0.0, stop=['Human:', 'Daniel:']):
        max_retry = 5
        retry = 0
        logging.info('Prompt type:' + str(type(prompt)))
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

    def __init__(self, author):
        self.author = author or 'user_id'
        logging.info("Daniel: Hi, nice to be speaking with you, what's your name?")
        self.conversation_text.append("Daniel: Hi, nice to be speaking with you, what's your name?")
        # user_input = input('Human: ')
        user_input = 'This is some text 1'
        prompt = self.open_file('website\\prompt_greeting.txt').replace('<<NAME_BLOCK>>', user_input)
        response = self.gpt3_completion(str(prompt), temp=0)
        print('Daniel: Hi %s.' % response)

    def turn(self, message):
        # user_input = input('Human: ')
        user_input = session['conversation_text']
        self.conversation_text.append('Human: %s' % message)
        text_block = '\n'.join(self.conversation)
        prompt = self.open_file('website\\prompt_init.txt').replace('<<BLOCK>>', text_block)
        prompt = prompt + '\nDaniel:'
        response = gpt3_completion(prompt)
        print('Daniel: ', response)
        self.conversation_text.append('Daniel: %s' % response)