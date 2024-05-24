import json
import os
import re

import openai
from dotenv import load_dotenv

from app.db_init import session
from .service.RiddlePromptingService import RiddlePromptingService
from .service.UserService import UserService

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
model = 'gpt-3.5-turbo'


def generate_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return openai.embeddings.create(input=text, model=model).data[0].embedding


def similarity(embedding1, embedding2):
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    magnitude1 = sum(a ** 2 for a in embedding1) ** 0.5
    magnitude2 = sum(b ** 2 for b in embedding2) ** 0.5
    return dot_product / (magnitude1 * magnitude2)


userService = UserService(session)
riddlePromptingService = RiddlePromptingService(session)


# Embedding, 1차 프롬프팅
def evaluate_question(question, riddle):
    problem_embedding = json.loads(riddle.problem_embedding_str)
    situation_embedding = json.loads(riddle.situation_embedding_str)
    answer_embedding = json.loads(riddle.answer_embedding_str)
    question_embedding = generate_embedding(question)

    problem_similarity = similarity(question_embedding, problem_embedding)
    situation_similarities = [similarity(question_embedding, emb) for emb in situation_embedding]
    max_similarity = max(situation_similarities)
    answer_similarity = similarity(question_embedding, answer_embedding)

    print('정답 유사도 = ' + str(answer_similarity))
    print('문제 유사도 = ' + str(problem_similarity))
    # print(situation_similarities)
    print('상황 유사도 = ' + str(max_similarity))

    count = 0
    for i in range(len(situation_embedding)):
        situation_similarity = similarity(question_embedding, situation_embedding[i])
        if situation_similarity >= 0.4:
            count += 1
        print("count : " + str(count))
        if count == 0:
            return '문제의 정답과 상관이 없습니다.'
        else:

            gpt_prompting = "당신은 문장 맞추기 퀴즈 시스템의 진행자입니다. 이 시스템의 참여자인 플레이 어는 퀴즈의 정답을 맞추기 위해 질문을 할 것입니다. "
            gpt_prompting += "당신은 플레이어의 질문이 문제 문장, 상황 문장, 정답 문장과 논리적으로 일치한지 판단해야 합니다."
            gpt_prompting += f"문제 문장: {riddle.problem} "
            gpt_prompting += f"상황 문장: {riddle.situation} "
            gpt_prompting += f"정답 문장: {riddle.answer} "
            gpt_prompting += "판단 과정과 결과를 Table 형식으로 표현합니다. "
            gpt_prompting += "| 문장 | 사용자의 입력과 일치하는지 아닌지 판단하는 내용 | True or False |"
            gpt_prompting += "이러한 table형태로 3개의 레코드가 나와야 합니다."

            assistants = riddlePromptingService.get_all_prompting(riddle.riddle_id)
            assistant_prompting = []
            for i in assistants:
                assistant_prompting.append({"role": "user", "content": i.user_query})
                # print(i.user_query)
                assistant_prompting.append({"role": "assistant", "content": i.assistant_response})
                # print(i.assistant_response)
            message = [{"role": "system", "content": gpt_prompting}] + assistant_prompting + [
                {"role": "user", "content": question}]
            # print(message)
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message,
                temperature=0.0,
                top_p=0.5
            )
            ans = response.choices[0].message.content
            print('질문 : ' + question)
            print('응답 : ' + ans)

            myList = []
            myDictionary = {}
            index_dash = ans.find('-')
            ans = ans[index_dash:]
            print(ans)

            TrueMatches = re.finditer("True", ans)
            FalseMatches = re.finditer("False", ans)

            for match in TrueMatches:
                myDictionary[match.start()] = True
            for match in FalseMatches:
                myDictionary[match.start()] = False
            myDictionary = dict(sorted(myDictionary.items()))

            print(myDictionary)

            values = list(myDictionary.values())
            for i in range(len(values)):
                myList.append(values[i])

            print(myList)

            if myList[2] == True:
                return '정답과 유사합니다.'
            elif myList[1] == True:
                return '맞습니다.'
            elif myList[0] == True:
                return '문제에 제공된 문장입니다.'
            return '아닙니다.'


def evaluate_similarity(question, riddle):
    sentences = riddle.progress_sentences.split('$')
    for sentence in sentences:
        print(sentence)
    num_sentence = len(sentences)
    #    prompt_sentence = f"{num_sentence}개의 문장이 있습니다. "
    #    for i in range(num_sentence):
    #        prompt_sentence += f"{i + 1}번째 문장입니다: ({sentences[i]}) "
    print(num_sentence)

    prompt_sentence = "당신은 문장 맞추기 퀴즈 시스템의 진행자입니다. 이 시스템의 참여자인 플레이 어는 퀴즈의 정답을 맞추기 위해 질문을 할 것입니다. "
    prompt_sentence += f"당신은 플레이어의 질문이 아래의 {num_sentence}문장과 논리적으로 일치한지 판단해야 합니다. "
    for i in range(num_sentence):
        prompt_sentence += f"{i + 1}번 문장: {sentences[i]} "
    prompt_sentence += "판단 과정과 결과를 Table 형식으로 표현합니다. "
    prompt_sentence += "| 문장 | 사용자의 입력과 일치하는지 아닌지 판단하는 내용 | True or False | "
    prompt_sentence += f"이러한 table형태로 {num_sentence}개의 레코드가 나와야 합니다. "

    print(prompt_sentence)

    similarity_message = [{"role": "system", "content": prompt_sentence}, {"role": "user", "content": question}]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=similarity_message,
        temperature=0.0,
        top_p=0.5
    )
    ans = response.choices[0].message.content

    # print(ans)

    myList = []
    myDictionary = {}
    index_dash = ans.find('-')
    ans = ans[index_dash:]
    # print(ans)

    TrueMatches = re.finditer("True", ans)
    FalseMatches = re.finditer("False", ans)

    for match in TrueMatches:
        myDictionary[match.start()] = True
    for match in FalseMatches:
        myDictionary[match.start()] = False
    myDictionary = dict(sorted(myDictionary.items()))

    # print(myDictionary)

    values = list(myDictionary.values())
    for i in range(len(values)):
        myList.append(values[i])

    print(myList)
    ####
    # print("####여기는 T/F 결과####")
    # print(myList)
    # print()

    percent = 100
    for i in range(num_sentence - 1, -1, -1):
        if myList[i] == True:
            return percent
        percent -= int((100 / len(myList)))
    return 0
